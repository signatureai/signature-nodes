import ast
import importlib.util
import os
import shutil
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


def create_categories(nodes_dir: Path) -> list:
    categories = _init_categories(nodes_dir)
    for path in nodes_dir.rglob("*.py"):
        if path.name not in ["__init__.py", "categories.py", "shared.py"]:
            with open(path) as f:
                content = f.read()
                for name in categories:
                    if name in content:
                        categories[name]["files"].append(path)

    return [v for v in categories.values() if v["files"]]


def _init_categories(nodes_dir: Path) -> dict:
    categories_path = nodes_dir / "categories.py"
    if not categories_path.exists():
        return {}

    spec = importlib.util.spec_from_file_location("categories", categories_path)
    if spec is None or spec.loader is None:
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    categories = {}
    for name, value in module.__dict__.items():
        if name.endswith("_CAT"):
            output_base_name = name[:-4].lower()
            categories[name] = {
                "output_base_name": output_base_name,
                "documentation_path": value,
                "files": [],
            }

    return categories


def _extract_classes_with_docs(content: str) -> list[tuple[str, str, dict]]:
    classes = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Get both docstring and DESCRIPTION
        docstring = ast.get_docstring(node)
        description = _extract_description(node)

        # Use DESCRIPTION if available, otherwise use docstring
        doc = docstring if docstring else description
        if not doc:
            continue

        metadata = _extract_class_metadata(node)
        classes.append((node.name, doc, metadata))

    return classes


def _extract_description(node: ast.ClassDef) -> str:
    """Extract DESCRIPTION class attribute if it exists."""
    for item in node.body:
        if isinstance(item, ast.Assign):
            for target in item.targets:
                if isinstance(target, ast.Name) and target.id == "DESCRIPTION":
                    if isinstance(item.value, ast.Constant):
                        return item.value.value
                    elif isinstance(item.value, ast.Str):  # For older Python versions
                        return item.value.s
    return ""


def _extract_class_metadata(node: ast.ClassDef) -> dict:
    input_types = {}
    return_types = []
    category = None

    for item in node.body:
        if isinstance(item, ast.ClassDef) and item.name == "INPUT_TYPES":
            continue

        if not isinstance(item, (ast.FunctionDef, ast.Assign)):
            continue

        if isinstance(item, ast.FunctionDef):
            if item.name != "INPUT_TYPES":
                continue
            if not any(isinstance(d, ast.Name) and d.id == "classmethod" for d in item.decorator_list):
                continue

            for stmt in item.body:
                if not isinstance(stmt, ast.Return):
                    continue
                if not isinstance(stmt.value, ast.Dict):
                    continue

                input_types = _process_input_types_dict(stmt.value)

        else:  # ast.Assign
            for target in item.targets:
                if not isinstance(target, ast.Name):
                    continue

                if target.id == "RETURN_TYPES":
                    return_types = _extract_return_types(item)
                elif target.id == "CATEGORY":
                    category = _extract_category(item)

    return {
        "input_types": input_types,
        "return_types": return_types,
        "category": category,
    }


def _process_input_types_dict(dict_node):
    result = {}
    try:
        result = _process_top_level_dict(dict_node)
    except Exception as e:
        print(f"Error processing input types dict: {e}")
        traceback.print_exc()
    return result


def _process_top_level_dict(dict_node):
    result = {}
    for key, value in zip(dict_node.keys, dict_node.values):
        if not isinstance(key, (ast.Constant, ast.Str)):
            continue

        key_name = key.value if isinstance(key, ast.Constant) else key.s
        if not isinstance(value, ast.Dict):
            continue

        result[key_name] = _process_nested_dict(value)
    return result


def _process_nested_dict(dict_node):
    nested_dict = {}
    for k, v in zip(dict_node.keys, dict_node.values):
        if not isinstance(k, (ast.Constant, ast.Str)):
            continue

        param_name = k.value if isinstance(k, ast.Constant) else k.s
        if not isinstance(v, ast.Tuple):
            continue

        param_info = _process_param_info(v)
        if param_info:
            nested_dict[param_name] = param_info
    return nested_dict


def _process_param_info(tuple_node):
    param_info = {}

    if isinstance(tuple_node.elts[0], ast.Constant):
        param_info["type"] = tuple_node.elts[0].value
    elif isinstance(tuple_node.elts[0], ast.Name):
        param_info["type"] = tuple_node.elts[0].id
    else:
        param_info["type"] = getattr(tuple_node.elts[0], "s", str(tuple_node.elts[0]))

    if len(tuple_node.elts) > 1 and isinstance(tuple_node.elts[1], ast.Dict):
        for opt_k, opt_v in zip(tuple_node.elts[1].keys, tuple_node.elts[1].values):
            opt_name = opt_k.value if isinstance(opt_k, ast.Constant) else getattr(opt_k, "s", str(opt_k))
            if isinstance(opt_v, ast.Constant):
                param_info[opt_name] = opt_v.value

    return param_info


def _extract_return_types(node):
    try:
        return ast.literal_eval(node.value)
    except (ValueError, SyntaxError, TypeError):
        return []


def _extract_category(node):
    try:
        if isinstance(node.value, ast.Name):
            return node.value.id
        return None
    except (AttributeError, TypeError):
        return None


def create_category_files(docs_dir: Path, categories: list):
    nodes_docs_dir = docs_dir / "nodes"
    os.makedirs(nodes_docs_dir, exist_ok=True)

    for category in categories:
        module_classes = []
        module_content = ""
        for file in category["files"]:
            content = _read_file_content(file)
            classes = _extract_classes_with_docs(content)
            if classes or any(docstring for _, docstring, _ in classes):
                module_classes.extend(classes)
                module_content += content

        _write_module_documentation(nodes_docs_dir, category["output_base_name"], module_classes, module_content)


def _read_file_content(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()


def _write_module_documentation(docs_dir: Path, module_name: str, classes: list, content: str):
    doc_file = docs_dir / f"{module_name}.md"
    with open(doc_file, "w") as doc:
        title = module_name.replace("_", " ").title()
        doc.write(f"# {title} Nodes\n\n")

        for class_name, docstring, metadata in classes:
            if not docstring:
                continue

            _write_class_documentation(
                doc=doc,
                class_name=class_name,
                docstring=docstring,
                metadata=metadata,
                module_name=module_name,
                content=content,
            )


def _write_class_documentation(**kwargs):
    doc = kwargs["doc"]
    class_name = kwargs["class_name"]
    docstring = kwargs["docstring"]
    metadata = kwargs["metadata"]
    module_name = kwargs["module_name"]  # Add this line to extract module_name
    content = kwargs["content"]  # Add this line to extract content

    doc.write(f"## {class_name}\n\n")

    # Clean and split the docstring
    cleaned_docstring = docstring.strip('"""').strip("'''").strip()
    sections = cleaned_docstring.split("\n\n")

    # Write description paragraphs (everything before the first "key: value" pattern)
    description = []
    for section in sections:
        # If the section doesn't contain ": " or starts with a known keyword, treat it as description
        if not any(section.startswith(k + ":") for k in ["Args", "Returns", "Raises", "Notes"]):
            description.append(section.strip())
        else:
            break

    # Write description paragraphs
    doc.write("\n\n".join(description) + "\n\n")

    if metadata["input_types"]:
        _write_input_documentation(doc, metadata["input_types"])

    if metadata["return_types"]:
        _write_return_documentation(doc, metadata)

    _write_code_documentation(doc, class_name, module_name, content)


def _write_input_documentation(doc, input_types: dict):
    doc.write("### Inputs\n\n")
    doc.write("| Group | Name | Type | Default | Extras |\n")
    doc.write("|-------|------|------|---------|--------|\n")

    for group_name, inputs in input_types.items():
        for name, type_info in inputs.items():
            if isinstance(type_info, dict):
                _write_dict_input(doc, group_name, name, type_info)
            else:
                raise ValueError(f"Unknown input type: {type(type_info)}")
    doc.write("\n")


def _write_return_documentation(doc, metadata: dict):
    doc.write("### Returns\n\n")
    doc.write("| Name | Type |\n")
    doc.write("|------|------|\n")

    return_names = metadata.get("return_names", [])
    for i, return_type in enumerate(metadata["return_types"]):
        name = return_names[i] if i < len(return_names) else return_type.lower()
        type_name = "ANY" if return_type == "any_type" else return_type
        doc.write(f"| {name} | `{type_name}` |\n")
    doc.write("\n\n")


def _write_code_documentation(doc, class_name: str, module_name: str, content: str):
    tree = ast.parse(content)

    # Source code section
    doc.write('??? note "Source code"\n\n')
    doc.write("    ```python\n")
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name != class_name:
            continue

        try:
            # Find the class in the original source by line matching
            lines = content.split("\n")
            class_lines = []
            in_class = False
            class_indent = None

            for line in lines:
                stripped = line.lstrip()
                current_indent = len(line) - len(stripped)

                if f"class {class_name}" in line:
                    in_class = True
                    class_indent = current_indent
                    class_lines.append(stripped)
                    continue

                if not in_class:
                    continue

                if stripped and class_indent is not None and current_indent <= class_indent:
                    # We've reached the end of the class
                    break

                if not stripped:
                    class_lines.append("")
                    continue

                # Remove only the class-level indentation
                if class_indent is not None:
                    remaining_indent = current_indent - class_indent
                    class_lines.append(" " * remaining_indent + stripped)
                else:
                    class_lines.append(stripped)

            if class_lines:
                # Add markdown code block indentation (4 spaces) to each line
                indented_lines = ["    " + line if line else "" for line in class_lines]
                doc.write("\n".join(indented_lines) + "\n")
            else:
                doc.write(f"    class {class_name}:\n        # Source code extraction failed\n")

        except Exception as e:
            print(f"Warning: Could not extract source for class {class_name}: {e}")
            doc.write(f"    class {class_name}:\n        # Source code extraction failed\n")
    doc.write("    ```\n\n")


def _write_dict_input(doc, group_name: str, name: str, type_info: dict):
    type_name = type_info.get("type", "unknown")
    if "ast.List" in type_name:
        type_name = "LIST"
    default = type_info.get("default", "")
    extras = ", ".join(f"{k}={v}" for k, v in type_info.items() if k not in ["type", "default"])
    doc.write(f"| {group_name} | {name} | `{type_name}` | {default} | {extras} |\n")


def create_mkdocs_config(categories: list):
    category_tree = {}
    parts_and_output_base_names = [
        (
            [p.strip() for p in category["documentation_path"].split("/")][1:],
            category["output_base_name"],
        )
        for category in categories
    ]
    for parts, output_base_name in sorted(parts_and_output_base_names, key=lambda x: -len(x[0])):
        current_level = category_tree
        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        last_part = parts[-1]
        if last_part in current_level and len(current_level[last_part]) > 0:
            # Add parent category as first dict entry
            old_children = current_level[last_part]
            new_children = {last_part: f"nodes/{output_base_name}.md"}
            new_children.update(old_children)
            current_level[last_part] = new_children
        else:
            current_level[last_part] = f"nodes/{output_base_name}.md"

    def _build_nav_structure(tree):
        result = []
        for key, value in tree.items():
            if isinstance(value, dict):
                result.append({key: _build_nav_structure(value)})
            else:
                result.append({key: value})
        return result

    nav_structure = [
        {"Home": "index.md"},
        {"Nodes": [*_build_nav_structure(category_tree)]},
    ]

    config = f"""site_name: Signature Nodes Documentation
theme:
    name: material
    features:
        - navigation.instant
        - navigation.tracking
        - navigation.sections
        - navigation.expand
        - navigation.top
        - search.highlight
        - search.share
        - toc.follow
    palette:
        # Force dark mode
        scheme: slate
        primary: indigo
        accent: indigo

plugins:
    - search

markdown_extensions:
    - pymdownx.highlight:
        anchor_linenums: true
    - pymdownx.inlinehilite
    - pymdownx.snippets
    - pymdownx.superfences
    - admonition
    - pymdownx.details
    - pymdownx.emoji:
        emoji_index: !!python/name:material.extensions.emoji.twemoji
        emoji_generator: !!python/name:material.extensions.emoji.to_svg

nav: {nav_structure}"""

    return config


def copy_readme_to_index(project_base_dir: Path):
    readme_path = project_base_dir / "README.md"
    index_path = project_base_dir / "docs" / "index.md"

    if not readme_path.exists():
        return

    with open(readme_path, encoding="utf-8") as f:
        content = f.read()

    content = content.replace("# Signature for ComfyUI", "# Signature Nodes Documentation")

    os.makedirs(project_base_dir / "docs", exist_ok=True)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    nodes_dir = BASE_DIR / "nodes"
    docs_dir = BASE_DIR / "docs"

    sys.path.insert(0, str(BASE_DIR))

    init_file = nodes_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()

    shutil.rmtree(docs_dir)
    os.makedirs(docs_dir, exist_ok=True)

    copy_readme_to_index(BASE_DIR)

    categories = create_categories(nodes_dir)
    create_category_files(docs_dir, categories)

    mkdocs_config = BASE_DIR / "mkdocs.yml"
    with open(mkdocs_config, "w") as f:
        f.write(create_mkdocs_config(categories))


if __name__ == "__main__":
    main()

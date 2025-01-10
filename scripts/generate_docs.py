import ast
import importlib.util
import os
import sys
import traceback
from pathlib import Path

base_dir = Path(__file__).parent.parent
sys.path.insert(0, str(base_dir))


# Add this function to dynamically load categories
def load_categories():
    categories_path = base_dir / "nodes" / "categories.py"
    if not categories_path.exists():
        return {}

    spec = importlib.util.spec_from_file_location("categories", categories_path)
    if spec is None or spec.loader is None:  # Add this check
        return {}

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return {name: value for name, value in module.__dict__.items() if name.endswith("_CAT")}


def extract_classes_with_docs(content: str) -> list[tuple[str, str, dict]]:
    classes = []
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        docstring = ast.get_docstring(node)
        if not docstring:
            continue

        metadata = _extract_class_metadata(node)
        classes.append((node.name, docstring, metadata))

    return classes


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
                    return_types = extract_return_types(item)
                elif target.id == "CATEGORY":
                    category = extract_category(item)

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
    param_info["type"] = (
        tuple_node.elts[0].value
        if isinstance(tuple_node.elts[0], ast.Constant)
        else getattr(tuple_node.elts[0], "s", str(tuple_node.elts[0]))
    )

    if len(tuple_node.elts) > 1 and isinstance(tuple_node.elts[1], ast.Dict):
        for opt_k, opt_v in zip(tuple_node.elts[1].keys, tuple_node.elts[1].values):
            opt_name = opt_k.value if isinstance(opt_k, ast.Constant) else getattr(opt_k, "s", str(opt_k))
            if isinstance(opt_v, ast.Constant):
                param_info[opt_name] = opt_v.value

    return param_info


def extract_return_types(node):
    try:
        return ast.literal_eval(node.value)
    except (ValueError, SyntaxError, TypeError):
        return []


def extract_category(node):
    try:
        if isinstance(node.value, ast.Name):
            return node.value.id
        return None
    except (AttributeError, TypeError):
        return None


def create_category_files(nodes_dir: str, docs_dir: str):
    nodes_docs_dir = os.path.join(docs_dir, "nodes")
    os.makedirs(nodes_docs_dir, exist_ok=True)

    for file in os.listdir(nodes_dir):
        if not _is_valid_node_file(file):
            continue

        module_name = file[:-3]
        content = _read_file_content(os.path.join(nodes_dir, file))
        classes = extract_classes_with_docs(content)

        if not (classes and any(docstring for _, docstring, _ in classes)):
            continue

        _write_module_documentation(nodes_docs_dir, module_name, classes, content)


def _is_valid_node_file(filename: str) -> bool:
    return filename.endswith(".py") and filename not in ["__init__.py", "categories.py", "shared.py"]


def _read_file_content(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()


def _write_module_documentation(docs_dir: str, module_name: str, classes: list, content: str):
    doc_file = os.path.join(docs_dir, f"{module_name}.md")
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
    doc.write(f'??? note "Source code in {module_name}.py"\n\n')
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


def create_mkdocs_config(docs_dir: str):
    category_usage = {}
    nodes_dir = base_dir / "nodes"
    categories = load_categories()

    for file in os.listdir(nodes_dir):
        if file.endswith(".py") and file not in ["__init__.py", "categories.py", "shared.py"]:
            with open(nodes_dir / file) as f:
                content = f.read()
                for name, value in categories.items():
                    if name in content or f"from .categories import {name}" in content:
                        category_usage[value] = True

    category_tree = {}
    catalog_keys = list(category_usage.keys())
    for cat_value in catalog_keys:
        parts = cat_value.split("/")
        parts = [p.strip() for p in parts]

        parts = parts[1:]

        current_level = category_tree
        for _, part in enumerate(parts[:-1]):
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

        last_part = parts[-1].strip()

        nodes_docs_dir = os.path.join(docs_dir, "nodes")
        existing_docs = {f[:-3]: f for f in os.listdir(nodes_docs_dir) if f.endswith(".md")}

        clean_name = " ".join(last_part.split()[1:] if "️" in last_part else last_part.split())
        clean_name = clean_name.lower().replace(" ", "_")

        variations = [
            clean_name,
            clean_name.replace("_", ""),
            clean_name.split("_", maxsplit=1)[0] if "_" in clean_name else clean_name,
            "".join(c for c in clean_name if c.isalnum()),
            clean_name.replace("input", "").replace("output", ""),
            clean_name.rsplit("_", maxsplit=1)[-1] if "_" in clean_name else clean_name,
        ]

        doc_path = None
        for var in variations:
            if var in existing_docs:
                doc_path = f"nodes/{existing_docs[var]}"
                break
            for doc_name in existing_docs:
                if var in doc_name or doc_name in var:
                    doc_path = f"nodes/{existing_docs[doc_name]}"
                    break
            if doc_path:
                break

        if doc_path:
            current_level[last_part] = doc_path
        else:
            continue

    def build_nav_structure(tree):
        result = []
        for key, value in tree.items():
            if isinstance(value, dict):
                result.append({key: build_nav_structure(value)})
            else:
                result.append({key: value})
        return result

    nav_structure = [{"Home": "index.md"}, {"Nodes": [*build_nav_structure(category_tree)]}]

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


def create_category_docs(docs_dir: str):
    category_usage = {}
    nodes_dir = os.path.join(docs_dir, "..", "nodes")
    categories = load_categories()

    for file in os.listdir(nodes_dir):
        if file.endswith(".py") and file not in ["__init__.py", "categories.py", "shared.py"]:
            with open(os.path.join(nodes_dir, file)) as f:
                content = f.read()
                for name, value in categories.items():
                    if name in content or f"from .categories import {name}" in content:
                        category_usage[value] = True

    main_categories = []
    other_categories = []
    category_usage_keys = list(category_usage.keys())
    for cat_value in category_usage_keys:
        parts = cat_value.split("/")
        if len(parts) == 2:
            main_categories.append(cat_value)
        elif len(parts) == 3 and "📦 Others" in parts[1]:
            other_categories.append(cat_value)

    main_categories.sort()
    other_categories.sort()


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
    project_base_dir = Path(__file__).parent.parent
    nodes_dir = project_base_dir / "nodes"
    docs_dir = project_base_dir / "docs"

    sys.path.insert(0, str(project_base_dir))

    init_file = nodes_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()

    os.makedirs(docs_dir, exist_ok=True)

    copy_readme_to_index(project_base_dir)

    create_category_docs(str(docs_dir))

    create_category_files(str(nodes_dir), str(docs_dir))

    mkdocs_config = project_base_dir / "mkdocs.yml"
    with open(mkdocs_config, "w") as f:
        f.write(create_mkdocs_config(str(docs_dir)))


if __name__ == "__main__":
    main()

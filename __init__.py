import importlib
import inspect
import logging
import re
from os import remove, walk
from os.path import abspath, dirname, exists, join, realpath, sep
from shutil import copyfile

from dotenv import load_dotenv
from signature_core import __version__
from signature_core.logger import console

logger = logging.getLogger(__name__)
NEUROCHAIN_AVAILABLE = False

try:
    import neurochain

    NEUROCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("neurochain package not available")

load_dotenv()

script_file = realpath(__file__)
script_folder = dirname(script_file)
if "custom_nodes" in script_folder:
    base_comfy_dir = script_folder.split("custom_nodes")[0]
    signature_js = "signature.js"
    signature_js_path = join(script_folder, "nodes/web/")
    web_extensions = join(base_comfy_dir, "web/extensions/")
    src = join(signature_js_path, signature_js)
    dst = join(web_extensions, signature_js)
    if exists(web_extensions):
        if exists(dst):
            remove(dst)
        copyfile(src, dst)


def get_node_class_mappings(nodes_directory: str):
    node_class_mappings = {}
    node_display_name_mappings = {}

    plugin_file_paths = []

    for path, _, files in walk(nodes_directory):
        for name in files:
            if not name.endswith(".py"):
                continue
            plugin_file_paths.append(join(path, name))

    for plugin_file_path in plugin_file_paths:
        plugin_rel_path = plugin_file_path.replace(".py", "").replace(sep, ".")
        plugin_rel_path = plugin_rel_path.split("signature-core-nodes.nodes.")[-1]

        if not NEUROCHAIN_AVAILABLE and plugin_rel_path.startswith("neurochain"):
            continue

        try:
            module = importlib.import_module("signature-core-nodes.nodes." + plugin_rel_path)

            for item in dir(module):
                value = getattr(module, item)
                if (
                    not value
                    or not inspect.isclass(value)
                    or not value.__module__.startswith("signature-core-nodes.nodes.")
                ):
                    continue

                if hasattr(value, "FUNCTION"):
                    class_name = item.replace("2", "")
                    snake_case = (
                        str(value.CLASS_ID)
                        if hasattr(value, "CLASS_ID")
                        else (
                            str(value.CLASS_NAME)
                            if hasattr(value, "CLASS_NAME")
                            else re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).lower()
                        )
                    )
                    key = f"signature_{snake_case}"
                    node_class_mappings[key] = value
                    item_name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z]{2})(?=[A-Z][a-z])", " ", item)
                    node_display_name_mappings[key] = f"SIG {item_name}"
        except ImportError as e:
            console.log(f"[red]Error importing {plugin_rel_path}: {e}")

    return node_class_mappings, node_display_name_mappings


# Get the path to the nodes directory
nodes_path = join(dirname(abspath(__file__)), "nodes")
NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = get_node_class_mappings(nodes_path)

WEB_DIRECTORY = "./nodes/web"
NAME = "🔲 Signature Nodes"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "MANIFEST"]

MANIFEST = {
    "name": NAME,
    "version": __version__,
    "author": "Marco, Frederico, Anderson",
    "description": "SIG Nodes",
}

import importlib
import inspect
import logging
import os
import re
import sys
from os import walk
from os.path import abspath, dirname, join, sep

from .env import env
from .utils import parallel_for

logger = logging.getLogger(__name__)

logger.info(f"Environment: {env}")

BASE_COMFY_DIR: str = os.path.dirname(os.path.realpath(__file__)).split("custom_nodes")[0]
SIGNATURE_NODES_DIR: str = os.path.dirname(os.path.realpath(__file__)).split("src")[0]

MAX_INT: int = sys.maxsize
MAX_FLOAT: float = sys.float_info.max


SIGNATURE_CORE_AVAILABLE = False
SIGNATURE_FLOWS_AVAILABLE = False
NEUROCHAIN_AVAILABLE = False

try:
    from signature_core import __version__

    SIGNATURE_CORE_AVAILABLE = True
except ImportError:
    raise ImportError("signature_core package not available")

try:
    neurochain_module = importlib.import_module("neurochain")
    if neurochain_module is not None:
        NEUROCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("neurochain package not available")

try:
    flows_module = importlib.import_module("signature_flows")
    if flows_module is not None:
        os.environ["COMFYUI_DIR"] = BASE_COMFY_DIR
        SIGNATURE_FLOWS_AVAILABLE = True
except ImportError:
    logger.warning("signature_flows package not available")


def get_node_class_mappings(nodes_directory: str):
    node_class_mappings = {}
    node_display_name_mappings = {}

    plugin_file_paths = []
    for path, _, files in walk(nodes_directory):
        for name in files:
            if not name.endswith(".py"):
                continue
            plugin_file_paths.append(join(path, name))

    def process_plugin_file(plugin_file_path: str, idx: int = 0, worker_id: int = 0) -> tuple[dict, dict]:
        file_class_mappings = {}
        file_display_mappings = {}

        plugin_rel_path = plugin_file_path.replace(".py", "").replace(sep, ".")
        plugin_rel_path = plugin_rel_path.split("signature-nodes.nodes.")[-1]

        if not NEUROCHAIN_AVAILABLE and plugin_rel_path.startswith("neurochain"):
            return {}, {}

        try:
            module = importlib.import_module("signature-nodes.nodes." + plugin_rel_path)

            for item in dir(module):
                value = getattr(module, item)
                if not value or not inspect.isclass(value) or not value.__module__.startswith("signature-nodes.nodes."):
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
                    file_class_mappings[key] = value
                    item_name = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z]{2})(?=[A-Z][a-z])", " ", item)
                    file_display_mappings[key] = f"SIG {item_name}"
        except ImportError as e:
            logger.info(f"[red]Error importing {plugin_rel_path}: {e}")

        return file_class_mappings, file_display_mappings

    parallel_process = os.getenv("PARALLEL_PROCESSING", "False") == "True"
    if parallel_process:
        results = parallel_for(process_plugin_file, plugin_file_paths)
    else:
        results = [process_plugin_file(file_path, idx, 0) for idx, file_path in enumerate(plugin_file_paths)]

    for file_mappings, file_display_names in results:
        if isinstance(file_mappings, dict) and isinstance(file_display_names, dict):
            node_class_mappings.update(file_mappings)
            node_display_name_mappings.update(file_display_names)

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
    "description": "SIG Nodes",
}

if SIGNATURE_FLOWS_AVAILABLE:
    from .services.signature_flow_service import SignatureFlowService
    from .services.signature_model_service import SignatureModelService

    SignatureFlowService.setup_routes()
    SignatureModelService.setup_routes()

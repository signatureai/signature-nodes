import { app } from "../../../scripts/app.js";

function setDefaults(node) {
  node.flowInput = undefined;
  node.flowOutput = undefined;
  node.end_loop = undefined;

  for (let i = 0; i < node.inputs.length; i++) {
    const input = node.inputs[i];
    if (input.name === "flow") {
      node.flowInput = node.inputs[i];
    }
    if (input.name === "end_loop") {
      node.end_loop = node.inputs[i];
    }
  }
  for (let i = 0; i < node.outputs.length; i++) {
    const input = node.outputs[i];
    if (input.name === "flow") {
      node.flowOutput = node.outputs[i];
    }
  }
  if (node.flowInput !== undefined) {
    node.inputs = [node.flowInput];
  } else {
    node.inputs = [];
  }

  if (node.flowOutput !== undefined) {
    node.outputs = [node.flowOutput];
  } else {
    node.outputs = [];
  }

  if (node.end_loop !== undefined) {
    node.inputs.push(node.end_loop);
  }
  node.addInput("init_value_0", "*");
  node.addOutput("value_0", "*");
}

const COLOR_THEMES = {
  red: { nodeColor: "#332222", nodeBgColor: "#553333" },
  green: { nodeColor: "#223322", nodeBgColor: "#335533" },
  blue: { nodeColor: "#222233", nodeBgColor: "#333355" },
  pale_blue: { nodeColor: "#2a363b", nodeBgColor: "#3f5159" },
  cyan: { nodeColor: "#223333", nodeBgColor: "#335555" },
  purple: { nodeColor: "#332233", nodeBgColor: "#553355" },
  yellow: { nodeColor: "#443322", nodeBgColor: "#665533" },
  orange: { nodeColor: "#663322", nodeBgColor: "#995533" },
  none: { nodeColor: null, nodeBgColor: null }, // no color
};

function setNodeColors(node, theme) {
  if (!theme) {
    return;
  }
  node.shape = "box";
  if (theme.nodeColor && theme.nodeBgColor) {
    node.color = theme.nodeColor;
    node.bgcolor = theme.nodeBgColor;
  }
}

const ext = {
  // Unique name for the extension
  name: "signature.logic",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    const class_name = nodeType.comfyClass;

    nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
      if (
        class_name === "signature_do_while_loop_start" ||
        class_name === "signature_do_while_loop_end" ||
        class_name === "signature_loop_start" ||
        class_name === "signature_loop_end"
      ) {
        if (type === 1 && link_info && link_info.target_id) {
          const node = app.graph.getNodeById(link_info.target_id);
          if (!node || !node.inputs[index]) return;

          const inputName = node.inputs[index].name;
          if (inputName.includes("init_value_")) {
            if (connected) {
              let idx = 0;
              for (let i = 0; i < node.inputs.length; i++) {
                if (node.inputs[i].name.includes("init_value_")) {
                  idx = idx + 1;
                }
              }
              node.addInput("init_value_" + idx, "*");
              node.addOutput("value_" + idx, "*");
            } else {
              node.inputs.splice(index, 1);
              const outputName = inputName.replace("init_value_", "value_");
              for (let i = 0; i < node.outputs.length; i++) {
                if (node.outputs[i].name === outputName) {
                  node.outputs.splice(i, 1);
                  break;
                }
              }
            }

            let idx = 0;
            for (let i = 0; i < node.inputs.length; i++) {
              if (node.inputs[i].name.includes("init_value_")) {
                node.inputs[i].name = "init_value_" + idx;
                idx = idx + 1;
              }
            }
            idx = 0;
            for (let i = 0; i < node.outputs.length; i++) {
              if (node.outputs[i].name.includes("value_")) {
                node.outputs[i].name = "value_" + idx;
                idx = idx + 1;
              }
            }
          }
        }
      }
    };
  },
  async nodeCreated(node) {
    const class_name = node.comfyClass;
    if (
      class_name === "signature_do_while_loop_start" ||
      class_name === "signature_do_while_loop_end" ||
      class_name === "signature_loop_start" ||
      class_name === "signature_loop_end"
    ) {
      setDefaults(node);
      setNodeColors(node, COLOR_THEMES["pale_blue"]);
    }
  },
};

app.registerExtension(ext);

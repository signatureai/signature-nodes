import { app } from "../../../scripts/app.js";
import { COLOR_THEMES, setDefaults, setNodeColors } from "./helpers/logic_nodes/main.js";

const ext = {
  // Unique name for the extension
  name: "signature.logic",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    const class_name = nodeType.comfyClass;

    nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
      if (class_name === "signature_loop_start" || class_name === "signature_loop_end") {
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
    if (class_name === "signature_loop_start" || class_name === "signature_loop_end") {
      setDefaults(node);
      setNodeColors(node, COLOR_THEMES["pale_blue"]);
    }
  },
};

app.registerExtension(ext);

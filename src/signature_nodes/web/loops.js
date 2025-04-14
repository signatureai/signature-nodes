import { app } from "../../../scripts/app.js";
import { excludeLoops, NODE_COLORS, updateInputsOutputs } from "./helpers/loops/main.js";

const ext = {
  name: "signature.DoWhileLoopStart",

  async nodeCreated(node) {
    if (!excludeLoops.includes(node.comfyClass)) return;

    node.shape = "box";
    node.color = NODE_COLORS.nodeColor;
    node.bgcolor = NODE_COLORS.nodeBgColor;

    let startIndex = 0;
    if (node.comfyClass === "signature_for_loop_start" || node.comfyClass === "signature_for_loop_end") {
      startIndex = 1;
    }

    const widgetNumSlots = node.widgets.find((w) => w.name === "num_slots");
    let widgetValue = widgetNumSlots.value;
    updateInputsOutputs(node, parseInt(widgetValue), startIndex);
    let originalDescriptor = Object.getOwnPropertyDescriptor(widgetNumSlots, "value");
    Object.defineProperty(widgetNumSlots, "value", {
      get() {
        let valueToReturn =
          originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(widgetNumSlots) : widgetValue;
        return valueToReturn;
      },
      set(newVal) {
        const oldVal = widgetValue;

        if (originalDescriptor && originalDescriptor.set) {
          originalDescriptor.set.call(widgetNumSlots, newVal);
        } else {
          widgetValue = newVal;
        }

        if (oldVal !== newVal) {
          updateInputsOutputs(node, parseInt(newVal), startIndex);
        }
      },
    });

    const originalDrawForeground = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
      originalDrawForeground?.apply?.(this, arguments);

      for (const outputName of node.outputsHidden) {
        const slotOutput = node.findOutputSlot(outputName);
        if (slotOutput < 0) continue;
        const pos = node.getConnectionPos(false, slotOutput);

        pos[0] -= node.pos[0] - 10;
        pos[1] -= node.pos[1];

        ctx.beginPath();
        ctx.strokeStyle = "red";
        ctx.lineWidth = 4;
        ctx.moveTo(pos[0] - 5, pos[1] - 5);
        ctx.lineTo(pos[0] + 5, pos[1] + 5);
        ctx.moveTo(pos[0] + 5, pos[1] - 5);
        ctx.lineTo(pos[0] - 5, pos[1] + 5);
        ctx.stroke();
      }
    };
  },
};

app.registerExtension(ext);

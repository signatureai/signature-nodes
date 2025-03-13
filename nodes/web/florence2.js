import { app } from "../../../scripts/app.js";
import { updateInputsOutputs } from "./helpers/florence2/main.js";

app.registerExtension({
  name: "signature.Florence",

  async nodeCreated(node) {
    if (node.comfyClass !== "signature_florence") return;

    const widgetMetadata = node.widgets.find((w) => w.name === "sig_additional_metadata");
    let metadata = {};
    if (widgetMetadata) {
      metadata = JSON.parse(widgetMetadata.value || "{}");
      node.widgets.splice(node.widgets.indexOf(widgetMetadata), 1);
    }

    const widgetTaskToken = node.widgets.find((w) => w.name === "task_token");
    if (!widgetTaskToken) return;

    const originalInputNames = node.inputs.map((i) => i.name);
    const originalWidgetNames = node.widgets.map((w) => w.name);

    let widgetValue = widgetTaskToken.value;
    updateInputsOutputs(node, widgetValue, metadata, originalInputNames, originalWidgetNames);
    let originalDescriptor = Object.getOwnPropertyDescriptor(widgetTaskToken, "value");
    Object.defineProperty(widgetTaskToken, "value", {
      get() {
        let valueToReturn =
          originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(widgetTaskToken) : widgetValue;
        return valueToReturn;
      },
      set(newVal) {
        const oldVal = widgetValue;

        if (originalDescriptor && originalDescriptor.set) {
          originalDescriptor.set.call(widgetTaskToken, newVal);
        } else {
          widgetValue = newVal;
        }

        if (oldVal !== newVal) {
          updateInputsOutputs(node, newVal, metadata, originalInputNames, originalWidgetNames);
        }
      },
    });

    const originalDrawForeground = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
      originalDrawForeground?.apply?.(this, arguments);

      for (const outputName of node.hiddenOutputs) {
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
});

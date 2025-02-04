import { app } from "../../../scripts/app.js";

function updateInputsOutputs(node, newVal, metadata, originalInputNames, originalWidgetNames) {
  // Hide inputs and widgets
  node.hiddenInputs ||= [];
  node.hiddenWidgets ||= [];
  node.inputs ||= [];
  node.widgets ||= [];

  node.inputs = [...node.inputs, ...node.hiddenInputs];
  node.widgets = [...node.widgets, ...node.hiddenWidgets];
  node.hiddenInputs = [];
  node.hiddenWidgets = [];

  node.inputs.sort((a, b) => originalInputNames.indexOf(a.name) - originalInputNames.indexOf(b.name));
  node.widgets.sort((a, b) => originalWidgetNames.indexOf(a.name) - originalWidgetNames.indexOf(b.name));

  for (const hideInput of metadata[newVal].hide_inputs) {
    const input = node.inputs.find((i) => i.name === hideInput);
    if (input) {
      node.hiddenInputs.push(input);
      node.inputs.splice(node.inputs.indexOf(input), 1);
    }
    const widget = node.widgets.find((w) => w.name === hideInput);
    if (widget) {
      node.hiddenWidgets.push(widget);
      node.widgets.splice(node.widgets.indexOf(widget), 1);
      if (widget.type === "customtext") {
        const textarea = document.querySelector(`textarea[placeholder="${widget.name}"]`);
        if (textarea) {
          textarea.style.display = "none";
        }
      }
    }
  }

  node.hiddenOutputs = metadata[newVal].hide_outputs;

  node.setSize(node.computeSize());
}

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
          originalDescriptor.set.call(w, newVal);
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

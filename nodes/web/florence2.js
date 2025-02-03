import { app } from "../../../scripts/app.js";

function updateInputsOutputs(node, newVal, metadata, originalInputNames, originalOutputNames, originalWidgetNames) {
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

  // Hide outputs
  node.hiddenOutputs ||= [];
  node.outputs ||= [];
  const lenOutputsBefore = node.outputs.length;
  const allOutputs = [...node.outputs, ...node.hiddenOutputs];
  allOutputs.sort((a, b) => originalOutputNames.indexOf(a.name) - originalOutputNames.indexOf(b.name));
  node.hiddenOutputs = [];

  for (const output of allOutputs) {
    const slotIndex = node.findOutputSlot(output.name);
    if (slotIndex >= 0) {
      if (metadata[newVal].hide_outputs.includes(output.name)) {
        node.hiddenOutputs.push(output);
        node.removeOutput(slotIndex);
      } else {
        // if the slot is in the outputs then we have to remove it and re-create it with the links
        let storedLinks = [];
        if (output.links) {
          storedLinks = output.links.map((l) => node.graph.links[l]);
        }
        node.removeOutput(slotIndex);
        node.addOutput(output.name, output.type);
        const newOutput = node.findOutputSlot(output.name);
        for (const link of storedLinks) {
          const targetNode = node.graph.nodes.find((n) => n.id === link.target_id);
          if (targetNode) {
            node.connect(newOutput, targetNode, link.target_slot);
          }
        }
      }
    } else {
      if (!metadata[newVal].hide_outputs.includes(output.name)) {
        node.addOutput(output.name, output.type);
      } else {
        node.hiddenOutputs.push(output);
      }
    }
  }

  if (node.outputs.length !== lenOutputsBefore) {
    if (node.widgets && node.widgets.length > 0) {
      node.widgets[0].last_y += (node.outputs.length - lenOutputsBefore) * LiteGraph.NODE_SLOT_HEIGHT;
    }
  }

  node.setSize(node.computeSize());
}

app.registerExtension({
  name: "signature.Florence",

  async nodeCreated(node) {
    if (node.comfyClass !== "signature_florence") return;
    for (const w of node.widgets || []) {
      if (w.name !== "task_token") continue;

      const widgetMetadata = node.widgets.find((w) => w.name === "sig_additional_metadata");
      let metadata = {};
      if (widgetMetadata) {
        metadata = JSON.parse(widgetMetadata.value || "{}");
        node.widgets.splice(node.widgets.indexOf(widgetMetadata), 1);
      }

      const originalInputNames = node.inputs.map((i) => i.name);
      const originalOutputNames = node.outputs.map((o) => o.name);
      const originalWidgetNames = node.widgets.map((w) => w.name);

      let widgetValue = w.value;
      updateInputsOutputs(node, widgetValue, metadata, originalInputNames, originalOutputNames, originalWidgetNames);
      let originalDescriptor = Object.getOwnPropertyDescriptor(w, "value");
      Object.defineProperty(w, "value", {
        get() {
          let valueToReturn =
            originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(w) : widgetValue;
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
            updateInputsOutputs(node, newVal, metadata, originalInputNames, originalOutputNames, originalWidgetNames);
          }
        },
      });
    }
  },
});

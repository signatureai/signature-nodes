const updateInputsOutputs = (node, newVal, metadata, originalInputNames, originalWidgetNames) => {
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
};

export { updateInputsOutputs };

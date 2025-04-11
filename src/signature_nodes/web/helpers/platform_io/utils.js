const NODES = {
  signature_input_image: "Input Image",
  signature_input_text: "Input Text",
  signature_input_number: "Input Number",
  signature_input_slider: "Input Slider",
  signature_input_boolean: "Input Boolean",
  signature_output: "Output",
};

const output = (node, widget) => {
  const widgetType = widget.value.toUpperCase();
  if (node.inputs !== undefined) {
    for (const input of node.inputs) {
      if (input.name === "value") {
        input.type = widgetType;
      }
    }
  }

  const widgets = node.widgets || [];
  for (const w of widgets) {
    if (w.name === "title") {
      if (w.value.startsWith("Output ")) {
        if (widget.value[0] === undefined) {
          break;
        }
        const modStr = widget.value[0].toUpperCase() + widget.value.slice(1);
        w.value = "Output " + modStr;
      }
      break;
    }
  }
};

const inputImage = (node, widget) => {
  const name = widget.value;
  const type = widget.value.toUpperCase();
  if (node.inputs !== undefined) {
    node.inputs[0].type = type;
  } else {
    node.addInput(name, type);
  }

  if (node.outputs !== undefined) {
    node.outputs[0].name = name;
    node.outputs[0].type = type;
  } else {
    node.addOutput(name, type);
  }
};

const inputNumber = (node, widget) => {
  const widgetType = widget.value.toUpperCase();
  if (node.inputs !== undefined) {
    if (node.inputs.length > 0) {
      if (node.inputs[0].name === "value") {
        node.inputs[0].type = widgetType;
      }
    }
  }
  if (node.outputs !== undefined) {
    node.outputs[0].type = widgetType;
    node.outputs[0].name = widget.value;
  }

  const widgets = node.widgets || [];
  let valueWidget = null;
  for (const w of widgets) {
    if (w.name === "value") {
      valueWidget = w;
      break;
    }
  }

  if (node.type === "signature_input_number") {
    return;
  }
  if (valueWidget !== null) {
    if (widget.value === "int") {
      valueWidget.options.precision = 0.0;
      valueWidget.options.round = 0.0;
      valueWidget.options.step = 1.0;
    } else {
      valueWidget.options.precision = 2;
      valueWidget.options.round = 0.01;
      valueWidget.options.step = 0.01;
    }
  }
};

const inputSelector = (node, widget) => {
  const widgetType = widget.value.toUpperCase();

  const widgets = node.widgets || [];
  let valueWidget = null;
  // check last widget
  last_widget = widgets[widgets.length - 1];
  // if the value is different the ""
  if (last_widget.value !== "") {
    node.addInput("input_" + widgets.length, widgetType);
  }
};

const inputText = (node, widget) => {
  // Safety check for widget
  if (!widget) {
    console.error("Widget is undefined in inputText");
    return;
  }

  const widgetType = widget.value?.toUpperCase() || "";
  if (node.inputs !== undefined) {
    if (node.inputs.length > 0) {
      if (node.inputs[0].name === "value") {
        node.inputs[0].type = widgetType;
      }
    }
  }
  if (node.outputs !== undefined) {
    node.outputs[0].type = widgetType;
    node.outputs[0].name = widget.value;
  }
};

const nodeWidgetHandlers = {
  signature_input_image: {
    subtype: inputImage,
  },
  signature_input_text: {
    subtype: inputText,
  },
  signature_input_number: {
    subtype: inputNumber,
  },
  signature_input_slider: {
    subtype: inputNumber,
  },
  signature_input_selector: {
    subtype: inputSelector,
  },
  signature_output: {
    subtype: output,
  },
};

// In the main function where widgetLogic is called
const widgetLogic = (node, widget) => {
  // Retrieve the handler for the current node title and widget name
  const handler = nodeWidgetHandlers[node.comfyClass]?.[widget.name];

  if (handler) {
    handler(node, widget);
  }
};

export { NODES, widgetLogic };

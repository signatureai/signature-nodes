import { app } from "../../../scripts/app.js";

const NODES = {
  signature_input_image: "Input Image",
  signature_input_text: "Input Text",
  signature_input_number: "Input Number",
  signature_input_slider: "Input Slider",
  signature_input_boolean: "Input Boolean",
  signature_output: "Output",
};

function output(node, widget) {
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
        // console.log("=======> " + widget.value);
        if (widget.value[0] === undefined) {
          // console.log("=======> undefined $$$");
          break;
        }
        const modStr = widget.value[0].toUpperCase() + widget.value.slice(1);
        w.value = "Output " + modStr;
      }
      break;
    }
  }
}

function inputImage(node, widget) {
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
}

function inputNumber(node, widget) {
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
}

function inputSelector(node, widget) {
  const widgetType = widget.value.toUpperCase();

  const widgets = node.widgets || [];
  let valueWidget = null;
  // check last widget
  last_widget = widgets[widgets.length - 1];
  // if the value is different the ""
  if (last_widget.value !== "") {
    node.addInput("input_" + widgets.length, widgetType);
  }
}

const nodeWidgetHandlers = {
  signature_input_image: {
    subtype: inputImage,
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
function widgetLogic(node, widget) {
  // Retrieve the handler for the current node title and widget name
  const handler = nodeWidgetHandlers[node.comfyClass]?.[widget.name];

  if (handler) {
    handler(node, widget);
  }
}

const ext = {
  name: "signature.platform_io",

  nodeCreated(node) {
    const title = node.comfyClass;
    if (NODES.hasOwnProperty(title)) {
      // node.title = NODES[title];

      node.validateLinks = function () {
        if (node.outputs !== undefined) {
          if (node.outputs[0].type !== "*" && node.outputs[0].links) {
            node.outputs[0].links
              .filter((linkId) => {
                const link = node.graph.links[linkId];
                return link && link.type !== node.outputs[0].type && link.type !== "*";
              })
              .forEach((linkId) => {
                node.graph.removeLink(linkId);
              });
          }
        }
      };

      for (const w of node.widgets || []) {
        let widgetValue = w.value;
        widgetLogic(node, w);
        // Store the original descriptor if it exists
        let originalDescriptor = Object.getOwnPropertyDescriptor(w, "value");

        Object.defineProperty(w, "value", {
          get() {
            // If there's an original getter, use it. Otherwise, return widgetValue.
            let valueToReturn =
              originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(w) : widgetValue;
            return valueToReturn;
          },
          set(newVal) {
            // If there's an original setter, use it. Otherwise, set widgetValue.
            if (originalDescriptor && originalDescriptor.set) {
              originalDescriptor.set.call(w, newVal);
            } else {
              widgetValue = newVal;
            }

            widgetLogic(node, w);
          },
        });
      }
    }
  },
};

app.registerExtension(ext);

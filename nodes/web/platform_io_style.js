import { app } from "../../../scripts/app.js";

const NODES = {
  signature_input_image: "Input Image",
  signature_input_text: "Input Text",
  signature_input_number: "Input Number",
  signature_input_slider: "Input Slider",
  signature_input_boolean: "Input Boolean",
  signature_output: "Output",
};

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

function output(node, widget) {
  setNodeColors(node, COLOR_THEMES["purple"]);
}

function inputImage(node, widget) {
  setNodeColors(node, COLOR_THEMES["pale_blue"]);
}

function inputText(node, widget) {
  const value = widget.value;
  if (value === "string") {
    setNodeColors(node, COLOR_THEMES["yellow"]);
  }

  if (value === "positive_prompt") {
    setNodeColors(node, COLOR_THEMES["green"]);
  }

  if (value === "negative_prompt") {
    setNodeColors(node, COLOR_THEMES["red"]);
  }
}

function inputBoolean(node, widget) {
  setNodeColors(node, COLOR_THEMES["orange"]);
}

function inputNumber(node, widget) {
  setNodeColors(node, COLOR_THEMES["cyan"]);
}

function inputSelector(node, widget) {
  setNodeColors(node, COLOR_THEMES["purple"]);
}

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
  signature_input_boolean: {
    subtype: inputBoolean,
  },
  signature_output: {
    subtype: output,
  },
};

const ext = {
  name: "signature.platform_io",

  nodeCreated(node) {
    const title = node.comfyClass;
    if (NODES.hasOwnProperty(title)) {
      // Apply colors based on node type
      if (nodeWidgetHandlers.hasOwnProperty(title)) {
        const handler = nodeWidgetHandlers[title];
        if (handler.subtype) {
          handler.subtype(node);
        }
      }
    }
  },
};

app.registerExtension(ext);

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

function output(node) {
  setNodeColors(node, COLOR_THEMES["purple"]);
}

function inputImage(node) {
  setNodeColors(node, COLOR_THEMES["pale_blue"]);
}

function inputText(node, widget) {
  if (!widget) {
    return; // Skip styling if no widget is provided
  }

  const value = widget.value;
  if (!value) {
    return; // Skip styling if no value is set
  }

  switch (value.toLowerCase()) {
    case "string":
      setNodeColors(node, COLOR_THEMES["yellow"]);
      break;
    case "positive_prompt":
      setNodeColors(node, COLOR_THEMES["green"]);
      break;
    case "negative_prompt":
      setNodeColors(node, COLOR_THEMES["red"]);
      break;
  }
}

function inputBoolean(node) {
  setNodeColors(node, COLOR_THEMES["orange"]);
}

function inputNumber(node) {
  setNodeColors(node, COLOR_THEMES["cyan"]);
}

function inputSelector(node) {
  setNodeColors(node, COLOR_THEMES["purple"]);
}

const nodeStylingWidgetHandlers = {
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

export const addStyling = (node, title, widget) => {
  if (nodeStylingWidgetHandlers.hasOwnProperty(title)) {
    const handler = nodeStylingWidgetHandlers[title];
    if (handler.subtype) {
      handler.subtype(node, widget);
    }
  }
};

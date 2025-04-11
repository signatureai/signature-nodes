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

const setNodeColors = (node, theme) => {
  if (!theme) {
    return;
  }
  node.shape = "box";
  if (theme.nodeColor && theme.nodeBgColor) {
    node.color = theme.nodeColor;
    node.bgcolor = theme.nodeBgColor;
  }
};

const output = (node) => {
  setNodeColors(node, COLOR_THEMES["purple"]);
};

const inputImage = (node) => {
  setNodeColors(node, COLOR_THEMES["pale_blue"]);
};

const inputText = (node) => {
  setNodeColors(node, COLOR_THEMES["yellow"]);
};

const inputBoolean = (node) => {
  setNodeColors(node, COLOR_THEMES["orange"]);
};

const inputNumber = (node) => {
  setNodeColors(node, COLOR_THEMES["cyan"]);
};

const inputSelector = (node) => {
  setNodeColors(node, COLOR_THEMES["purple"]);
};

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

const addStyling = (node, title) => {
  if (nodeStylingWidgetHandlers.hasOwnProperty(title)) {
    const handler = nodeStylingWidgetHandlers[title];
    if (handler.subtype) {
      handler.subtype(node);
    }
  }
};

export { addStyling };

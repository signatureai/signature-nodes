const setDefaults = (node) => {
  node.flowInput = undefined;
  node.flowOutput = undefined;
  node.end_loop = undefined;

  for (let i = 0; i < node.inputs.length; i++) {
    const input = node.inputs[i];
    if (input.name === "flow") {
      node.flowInput = node.inputs[i];
    }
    if (input.name === "end_loop") {
      node.end_loop = node.inputs[i];
    }
  }
  for (let i = 0; i < node.outputs.length; i++) {
    const input = node.outputs[i];
    if (input.name === "flow") {
      node.flowOutput = node.outputs[i];
    }
  }
  if (node.flowInput !== undefined) {
    node.inputs = [node.flowInput];
  } else {
    node.inputs = [];
  }

  if (node.flowOutput !== undefined) {
    node.outputs = [node.flowOutput];
  } else {
    node.outputs = [];
  }

  if (node.end_loop !== undefined) {
    node.inputs.push(node.end_loop);
  }
  node.addInput("init_value_0", "*");
  node.addOutput("value_0", "*");
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

export { setDefaults, setNodeColors };

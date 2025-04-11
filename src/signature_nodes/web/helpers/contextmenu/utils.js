import { app } from "../../../../scripts/app.js";

const addMenuHandler = (nodeType, cb) => {
  const getOpts = nodeType.prototype.getExtraMenuOptions;
  nodeType.prototype.getExtraMenuOptions = function () {
    const r = getOpts.apply(this, arguments);
    cb.apply(this, arguments);
    return r;
  };
};

const addNode = (name, nextTo, options) => {
  options = { side: "left", select: true, shiftY: 0, shiftX: 0, ...(options || {}) };
  const node = LiteGraph.createNode(name);
  app.graph.add(node);

  node.pos = [
    options.side === "left"
      ? nextTo.pos[0] - (node.size[0] + options.offset)
      : nextTo.pos[0] + nextTo.size[0] + options.offset,

    nextTo.pos[1] + options.shiftY,
  ];
  if (options.select) {
    app.canvas.selectNode(node, false);
  }
  return node;
};

export { addMenuHandler, addNode };

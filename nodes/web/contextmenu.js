import { app } from "../../../scripts/app.js";

function addMenuHandler(nodeType, cb) {
  const getOpts = nodeType.prototype.getExtraMenuOptions;
  nodeType.prototype.getExtraMenuOptions = function () {
    const r = getOpts.apply(this, arguments);
    cb.apply(this, arguments);
    return r;
  };
}

function addNode(name, nextTo, options) {
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
}

app.registerExtension({
  name: "Signature.Contextmenu",
  async beforeRegisterNodeDef(nodeType, nodeData, app) {
    if (nodeData.input && nodeData.input.required) {
      addMenuHandler(nodeType, function (_, options) {
        options.unshift(
          {
            content: "Add SIG Get Node",
            callback: () => {
              addNode("SIG Get Node", this, { side: "left", offset: 30 });
            },
          },
          {
            content: "Add SIG Set Node",
            callback: () => {
              addNode("SIG Set Node", this, { side: "right", offset: 30 });
            },
          }
        );
      });
    }
  },
});

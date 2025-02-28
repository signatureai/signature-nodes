import { app } from "../../../scripts/app.js";

app.registerExtension({
  name: "signature.AllNodes",
  async setup() {
    // to keep Set/Get node virtual connections visible when offscreen
    const originalComputeVisibleNodes = LGraphCanvas.prototype.computeVisibleNodes;
    LGraphCanvas.prototype.computeVisibleNodes = function () {
      const visibleNodesSet = new Set(originalComputeVisibleNodes.apply(this, arguments));
      for (const node of this.graph._nodes) {
        if ((node.type === "SetNode" || node.type === "GetNode") && node.drawConnection) {
          visibleNodesSet.add(node);
        }
      }
      return Array.from(visibleNodesSet);
    };
  },
});

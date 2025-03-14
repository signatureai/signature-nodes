import { app } from "../../../../scripts/app.js";

const LGraphNode = LiteGraph.LGraphNode;

const showAlert = (message) => {
  app.extensionManager.toast.add({
    severity: "warn",
    summary: "SIG Get/Set",
    detail: `${message}. Most likely you're missing custom nodes`,
    life: 5000,
  });
};

export { LGraphNode, showAlert };

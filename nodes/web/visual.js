import { app } from "../../../scripts/app.js";

const ext = {
  name: "signature.visual",

  nodeCreated(node) {
    const className = node.comfyClass;
    let isSignatureNode = className.startsWith("signature_");
    let isOutputNode = isSignatureNode && className.includes("output");
    let isInputNode = isSignatureNode && className.includes("input");
    if (isSignatureNode && !isOutputNode && !isInputNode) {
      const title = node.getTitle();
      if (title.startsWith("SIG ")) {
        node.title = title.replace("SIG ", "🔲  ");
      }
      node.shape = "box";
      node.color = "#36213E";
      node.bgcolor = "#221324";
    }
  },
};

app.registerExtension(ext);

import { app } from "../../../scripts/app.js";

const ext = {
  name: "signature.visual",

  nodeCreated(node) {
    const className = node.comfyClass;
    let isSignatureNode = className.startsWith("signature_");
    let isOutputNode = isSignatureNode && className.includes("output");
    let isInputNode = isSignatureNode && className.includes("input");
    let isLoop = isSignatureNode && className.includes("loop");
    const title = node.getTitle();
    if (isSignatureNode && title.startsWith("SIG ")) {
      node.title = title.replace("SIG ", "");
    }
    if (isSignatureNode && !isOutputNode && !isInputNode && !isLoop) {
      node.shape = "box";
      node.color = "#36213E";
      node.bgcolor = "#221324";
    }
  },
};

app.registerExtension(ext);

import { app } from "../../../scripts/app.js";
import { addUploadWidget, NODES } from "./helpers/file_upload/main.js";

const ext = {
  name: "signature.file_upload",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    const title = nodeData?.name;
    if (NODES.hasOwnProperty(title)) {
      addUploadWidget(nodeType, "value", NODES[title], "*/*");
    }
  },
};

app.registerExtension(ext);

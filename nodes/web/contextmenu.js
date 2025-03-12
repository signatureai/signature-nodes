import { app } from "../../../scripts/app.js";
import { addMenuHandler, addNode } from "./helpers/contextmenu/utils.js";

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

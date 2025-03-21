import { app } from "../../scripts/app.js";
import { createMenuItem, findSignatureMenuList } from "./helpers/global/main.js";

const ext = {
  name: "signature.feature_request",
  async init(app) {
    const menuList = findSignatureMenuList();
    if (menuList) {
      menuList.appendChild(
        createMenuItem("Feature Request", "pi-file-plus", () => {
          window.open("https://signature-ai.atlassian.net/jira/software/c/projects/SIGML/form/70", "_blank");
        })
      );
    }
  },
};
app.registerExtension(ext);

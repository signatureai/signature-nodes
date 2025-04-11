import { app } from "../../scripts/app.js";
import { style } from "./helpers/bug_report/main.js";
import { createMenuItem, findSignatureMenuList } from "./helpers/global/main.js";

// Add the CSS class for the bug icon
document.head.appendChild(style);

const ext = {
  name: "signature.bug_report",
  async init(app) {
    const menuList = findSignatureMenuList();
    if (menuList) {
      menuList.appendChild(
        createMenuItem("Bug Report", "bug-report-icon", () => {
          window.open("https://signature-ai.atlassian.net/jira/software/c/projects/SIGML/form/69", "_blank");
        })
      );
    }
  },
};
app.registerExtension(ext);

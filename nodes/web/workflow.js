import { app } from "../../scripts/app.js";
import {
  $el,
  cleanLocalStorage,
  createMenuItem,
  deleteWorkflowFromStorage,
  findMenuList,
  requiresAuth,
  saveWorkflow,
  showMessage,
  showNodeOrderEditor,
  showWorkflowsList,
} from "./helpers/workflow/main.js";

const setupMenu = async (app) => {
  // Check if menu items are already added
  if (document.querySelector('[data-signature-menu="true"]')) {
    return true;
  }

  // Try to find menu list for up to 10 seconds
  for (let i = 0; i < 20; i++) {
    const menuList = findMenuList();
    if (menuList) {
      // Add separator
      const separator = $el("li", {
        className: "p-menubar-separator",
        role: "separator",
        "data-signature-menu": "true",
      });
      menuList.appendChild(separator);

      // Add Node Order Editor menu item
      const nodeOrderItem = createMenuItem("Edit Node Order", "pi-sort", () => {
        showNodeOrderEditor();
      });
      nodeOrderItem.setAttribute("data-signature-menu", "true");
      menuList.appendChild(nodeOrderItem);

      // Add Open from Signature menu item
      const openItem = createMenuItem("Open from Signature", "pi-cloud-download", async () => {
        try {
          await requiresAuth(app, showWorkflowsList);
        } catch (error) {
          console.error("Error in Open from Signature:", error);
          showMessage("Authentication error", "#ff0000", "Please try logging in again.");
        }
      });
      openItem.setAttribute("data-signature-menu", "true");
      menuList.appendChild(openItem);

      // Add Deploy to Signature menu item
      const deployItem = createMenuItem("Deploy to Signature", "pi-cloud-upload", async () => {
        try {
          await requiresAuth(app, saveWorkflow);
        } catch (error) {
          console.error("Error in Deploy to Signature:", error);
          showMessage("Authentication error", "#ff0000", "Please try logging in again.");
        }
      });
      deployItem.setAttribute("data-signature-menu", "true");
      menuList.appendChild(deployItem);

      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, 500)); // Wait 500ms before retry
  }
  console.warn("Could not find menu list after multiple attempts");
  return false;
};

const ext = {
  name: "signature.workflows",
  async init(app) {
    cleanLocalStorage();

    // Add mutation observer to watch for tab deletions
    const setupTabObserver = () => {
      const tabsContainer = document.querySelector(".workflow-tabs");
      if (tabsContainer) {
        console.log("Setting up tab observer");
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            if (mutation.removedNodes.length > 0) {
              mutation.removedNodes.forEach((node) => {
                // Get all tabs before the removal
                const allTabs = Array.from(tabsContainer.children);
                // Find the index by looking at the previous sibling chain
                let removedIndex = 0;
                let prevSibling = mutation.previousSibling;
                while (prevSibling) {
                  removedIndex++;
                  prevSibling = prevSibling.previousSibling;
                }

                // If we're removing the last tab, use the current length
                if (removedIndex === 0 && mutation.previousSibling === null) {
                  removedIndex = allTabs.length;
                }

                console.log("Tab removed at index:", removedIndex);
                // Delete the workflow from storage for this tab
                deleteWorkflowFromStorage(removedIndex - 1);
              });
            }
          });
        });

        observer.observe(tabsContainer, {
          childList: true,
          subtree: false,
          attributes: false,
        });
        console.log("Observer setup complete");
      } else {
        console.log("Tab container not found, retrying in 1s");
        setTimeout(setupTabObserver, 1000);
      }
    };

    // Start the observer setup
    setupTabObserver();
  },
  async setup(app) {
    if (app.menu) {
      await setupMenu(app);
    }
  },
};

app.registerExtension(ext);

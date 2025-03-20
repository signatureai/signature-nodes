import { app } from "../../scripts/app.js";
import { cleanLocalStorage, deleteWorkflowFromStorage, setupMenu } from "./helpers/workflow/utils.js";

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

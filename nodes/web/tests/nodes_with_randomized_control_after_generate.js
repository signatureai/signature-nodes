import { $el } from "../signature.js";

const findNodesWithRandomizedControlAfterGenerateWidget = async () => {
  const nodes = app.graph._nodes;

  const nodesWithRandomizedControlAfterGenerateWidget = nodes.filter(
    (node) =>
      (node.widgets &&
        node.widgets.some((widget) => widget.name === "control_after_generate" && widget.type === "combo")) ||
      (node.inputs && node.inputs.some((input) => input.name.includes("seed") && input.link === null))
  );
  // Highlight the nodes with red borders
  let removeHighlights = null;
  if (nodesWithRandomizedControlAfterGenerateWidget.length > 0) {
    removeHighlights = highlightNodesWithRandomizedWidgets(nodesWithRandomizedControlAfterGenerateWidget);

    // If there are nodes with randomized widgets, show a warning dialog
    const result = await showRandomizationWarningDialog(nodesWithRandomizedControlAfterGenerateWidget);

    // Remove the highlights after the dialog is closed
    if (removeHighlights) {
      removeHighlights();
    }

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }
  return nodesWithRandomizedControlAfterGenerateWidget;
};

// Function to show a warning dialog about randomized widgets
const showRandomizationWarningDialog = async (nodesWithRandomization) => {
  return new Promise((resolve) => {
    // Create a list of affected nodes
    const nodesList = nodesWithRandomization
      .map(
        (node) => `<li style="margin-left: 20px; margin-bottom: 5px;">${node.title || node.type} (ID: ${node.id})</li>`
      )
      .join("");

    const dialogContent = $el(
      "div",
      {
        style: {
          width: "90vw",
          maxWidth: "600px",
          padding: "20px",
          color: "white",
        },
      },
      [
        $el("h2", {
          style: {
            textAlign: "center",
            marginBottom: "20px",
            color: "#ff9900",
          },
          textContent: "⚠️ Randomization Warning",
        }),
        $el("p", {
          style: { marginBottom: "15px" },
          innerHTML:
            "Your workflow contains nodes with <strong>randomized values</strong> that won't work as expected after submission (highlighted with <span style='color: #ff0000;'>red borders</span>):",
        }),
        $el("ul", {
          style: {
            marginBottom: "20px",
            listStyleType: "disc",
          },
          innerHTML: nodesList,
        }),
        $el("p", {
          style: { marginBottom: "15px" },
          innerHTML:
            "When this workflow is submitted, these randomized values will be <strong>fixed</strong> to their current values and won't randomize for users.",
        }),
        $el("p", {
          style: { marginBottom: "20px" },
          innerHTML:
            "For true randomization in submitted workflows, we recommend using the <strong>Signature Random Number</strong> node connected to your seed inputs.",
        }),
        $el(
          "div",
          {
            style: {
              display: "flex",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "10px",
              marginTop: "30px",
            },
          },
          [
            $el("button", {
              textContent: "Cancel Submission",
              style: {
                padding: "10px 20px",
                backgroundColor: "#666",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                flex: "1",
                minWidth: "150px",
              },
              onclick: () => {
                const modalContent = document.querySelector(".comfy-modal-content");
                if (modalContent) {
                  const closeButton = modalContent.children.item(modalContent.children.length - 1);
                  if (closeButton) {
                    closeButton.style.display = "block";
                  }
                }
                app.ui.dialog.close();
                resolve({ continue: false });
              },
            }),
            $el("button", {
              textContent: "Continue Anyway",
              style: {
                padding: "10px 20px",
                backgroundColor: "#2D9CDB",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                flex: "1",
                minWidth: "150px",
              },
              onclick: () => {
                const modalContent = document.querySelector(".comfy-modal-content");
                if (modalContent) {
                  const closeButton = modalContent.children.item(modalContent.children.length - 1);
                  if (closeButton) {
                    closeButton.style.display = "block";
                  }
                }
                app.ui.dialog.close();
                resolve({ continue: true });
              },
            }),
          ]
        ),
      ]
    );

    app.ui.dialog.show(dialogContent);
    const modalContent = document.querySelector(".comfy-modal-content");
    if (modalContent) {
      const closeButton = modalContent.children.item(modalContent.children.length - 1);
      if (closeButton) {
        closeButton.style.display = "none";
      }
    }
  });
};

// Function to highlight nodes with randomized control_after_generate widgets
const highlightNodesWithRandomizedWidgets = (nodes) => {
  if (!nodes || nodes.length === 0) return;

  // Store original colors to restore later
  const originalColors = new Map();

  // Add red border to each node
  for (const node of nodes) {
    // Store the original border color and width
    originalColors.set(node.id, {
      color: node.color,
      boxShadow: node.boxShadow,
    });

    // Set a red border
    node.color = "#ff0000";
    node.boxShadow = "0 0 10px #ff0000";

    // Force the node to redraw
    if (node.setDirtyCanvas) {
      node.setDirtyCanvas(true, true);
    }
  }

  // Return a function to remove the highlighting
  return function removeHighlights() {
    for (const node of nodes) {
      const original = originalColors.get(node.id);
      if (original) {
        node.color = original.color;
        node.boxShadow = original.boxShadow;

        // Force the node to redraw
        if (node.setDirtyCanvas) {
          node.setDirtyCanvas(true, true);
        }
      }
    }
  };
};

export {
  findNodesWithRandomizedControlAfterGenerateWidget,
  highlightNodesWithRandomizedWidgets,
  showRandomizationWarningDialog,
};

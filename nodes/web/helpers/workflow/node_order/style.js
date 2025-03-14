import { app } from "../../../../../scripts/app.js";
import { $el, findMenuList, showMessage } from "../utils.js";
import { applyNodeOrderChanges, createNodeItem, initDragAndDrop } from "./utils.js";

const showNodeOrderEditor = () => {
  const dropdownMenu = findMenuList();
  if (dropdownMenu) {
    dropdownMenu.style.display = "none";
  }
  const nodes = app.graph._nodes;
  if (!nodes || nodes.length === 0) {
    showMessage("No nodes found in the workflow", "#ff0000");
    return;
  }

  // Filter and sort input and output nodes
  const inputNodes = nodes
    .filter((node) => node.type.includes("signature_input"))
    .sort(
      (a, b) =>
        (a.properties.signature_order !== undefined ? a.properties.signature_order : 0) -
        (b.properties.signature_order !== undefined ? b.properties.signature_order : 0)
    );

  const outputNodes = nodes
    .filter((node) => node.type.includes("signature_output"))
    .sort(
      (a, b) =>
        (a.properties.signature_order !== undefined ? a.properties.signature_order : 0) -
        (b.properties.signature_order !== undefined ? b.properties.signature_order : 0)
    );

  if (inputNodes.length === 0 && outputNodes.length === 0) {
    showMessage("No input or output nodes found in the workflow", "#ff0000");
    return;
  }

  const dialogContent = $el("div", [
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
      },
      textContent: "Node Order Editor",
    }),
    $el("p", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#cccccc",
      },
      textContent: "Drag nodes to change their display order on the platform",
    }),
    $el("div", {
      style: {
        display: "flex",
        justifyContent: "space-between",
        gap: "20px",
        width: "90vw",
        maxWidth: "1000px",
        margin: "0 auto",
      },
      $: (container) => {
        // Create the input nodes column
        const inputColumn = $el(
          "div",
          {
            style: {
              flex: "1",
              maxWidth: "calc(50% - 10px)",
            },
          },
          [
            $el("h3", {
              style: {
                textAlign: "center",
                marginBottom: "15px",
                color: "#4CAF50",
              },
              textContent: "Input Nodes",
            }),
            $el("div", {
              id: "input-nodes-container",
              style: {
                backgroundColor: "#1e1e1e",
                border: "1px solid #444",
                borderRadius: "4px",
                padding: "10px",
                maxHeight: "60vh",
                overflowY: "auto",
              },
              $: (inputContainer) => {
                // Create the sortable list for input nodes
                const inputList = $el("div", {
                  id: "sortable-input-list",
                  style: {
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  },
                });

                // Add each input node as a draggable item
                inputNodes.forEach((node, index) => {
                  const nodeItem = createNodeItem(node, index, "input");
                  inputList.appendChild(nodeItem);
                });

                if (inputNodes.length > 0) {
                  inputContainer.appendChild(inputList);
                } else {
                  inputContainer.appendChild(
                    $el("p", {
                      style: {
                        textAlign: "center",
                        color: "#cccccc",
                      },
                      textContent: "Workflow has no input nodes",
                    })
                  );
                }
                // Initialize drag and drop functionality
                setTimeout(() => {
                  initDragAndDrop(inputList);
                }, 100);
              },
            }),
          ]
        );

        // Create the output nodes column
        const outputColumn = $el(
          "div",
          {
            style: {
              flex: "1",
              maxWidth: "calc(50% - 10px)",
            },
          },
          [
            $el("h3", {
              style: {
                textAlign: "center",
                marginBottom: "15px",
                color: "#FF5722",
              },
              textContent: "Output Nodes",
            }),
            $el("div", {
              id: "output-nodes-container",
              style: {
                backgroundColor: "#1e1e1e",
                border: "1px solid #444",
                borderRadius: "4px",
                padding: "10px",
                maxHeight: "60vh",
                overflowY: "auto",
              },
              $: (outputContainer) => {
                // Create the sortable list for output nodes
                const outputList = $el("div", {
                  id: "sortable-output-list",
                  style: {
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  },
                });

                // Add each output node as a draggable item
                outputNodes.forEach((node, index) => {
                  const nodeItem = createNodeItem(node, index, "output");
                  outputList.appendChild(nodeItem);
                });

                if (outputNodes.length > 0) {
                  outputContainer.appendChild(outputList);
                } else {
                  outputContainer.appendChild(
                    $el("p", {
                      style: {
                        textAlign: "center",
                        color: "#cccccc",
                      },
                      textContent: "Workflow has no output nodes",
                    })
                  );
                }
                // Initialize drag and drop functionality
                setTimeout(() => {
                  initDragAndDrop(outputList);
                }, 100);
              },
            }),
          ]
        );

        container.append(inputColumn, outputColumn);
      },
    }),
    // Apply button
    $el(
      "div",
      {
        style: {
          display: "flex",
          justifyContent: "center",
          marginTop: "20px",
        },
      },
      [
        $el("button", {
          style: {
            padding: "10px 20px",
            backgroundColor: "#2D9CDB",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "16px",
          },
          textContent: "Apply Order Changes",
          onclick: () => {
            applyNodeOrderChanges();
            app.ui.dialog.close();
            showMessage("Node order updated successfully!", "#00ff00");
          },
        }),
      ]
    ),
  ]);

  app.ui.dialog.show(dialogContent);
};

export { showNodeOrderEditor };

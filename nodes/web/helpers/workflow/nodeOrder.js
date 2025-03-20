import { app } from "../../../../scripts/app.js";
import { $el } from "../../signature.js";
import { showMessage } from "../global/main.js";
import { findMenuList } from "./main.js";

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

const createNodeItem = (node, index, nodeType) => {
  const bgColor = nodeType === "input" ? "#1a3a1a" : "#3a1a1a";
  const borderColor = nodeType === "input" ? "#2a5a2a" : "#5a2a2a";

  return $el(
    "div",
    {
      className: `draggable-node-item ${nodeType}-node`,
      "data-node-id": node.id,
      "data-original-index": index,
      "data-original-order": node.properties.order !== undefined ? node.properties.order : "unset",
      "data-node-type": nodeType,
      style: {
        padding: "12px",
        backgroundColor: bgColor,
        border: `1px solid ${borderColor}`,
        borderRadius: "4px",
        cursor: "grab",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        userSelect: "none",
      },
    },
    [
      $el(
        "div",
        {
          style: {
            display: "flex",
            alignItems: "center",
            gap: "10px",
            flex: "1",
            overflow: "hidden",
          },
        },
        [
          // Node type icon or indicator
          $el("div", {
            style: {
              minWidth: "24px",
              height: "24px",
              backgroundColor: node.bgcolor || "#666",
              borderRadius: "4px",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              color: "#fff",
              fontWeight: "bold",
            },
            textContent: node.type.charAt(0).toUpperCase(),
          }),
          // Node title and type
          $el(
            "div",
            {
              style: {
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                flex: "1",
              },
            },
            [
              $el("div", {
                style: {
                  color: "#ffffff",
                  fontWeight: "bold",
                  fontSize: "15px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                },
                title: node.title || node.name || `Node ${node.id}`,
                textContent: node.title || node.name || `Node ${node.id}`,
              }),
              $el("div", {
                style: {
                  color: "#aaaaaa",
                  fontSize: "12px",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                },
                title: `ID: ${node.id} - ${node.widgets.find((widget) => widget.name === "title").value}`,
                textContent: `ID: ${node.id} - ${node.widgets.find((widget) => widget.name === "title").value}`,
              }),
            ]
          ),
        ]
      ),
      // Order display (relative position within group)
      $el("div", {
        className: "node-order-display",
        style: {
          color: "#888888",
          fontSize: "14px",
          minWidth: "140px",
          textAlign: "right",
        },
        innerHTML: `Position: <span class="original-order">${index + 1}</span> → <span class="new-order">${
          index + 1
        }</span>
                   <div style="font-size: 11px; color: #666;">Global: ${
                     node.properties.order !== undefined ? node.properties.order : "unset"
                   }</div>`,
      }),
    ]
  );
};

const updateOrderDisplay = () => {
  // Update input nodes
  const inputList = document.getElementById("sortable-input-list");
  if (inputList) {
    const inputItems = inputList.querySelectorAll(".draggable-node-item");
    inputItems.forEach((item, index) => {
      updateNodeOrderDisplay(item, index);
    });
  }

  // Update output nodes
  const outputList = document.getElementById("sortable-output-list");
  if (outputList) {
    const outputItems = outputList.querySelectorAll(".draggable-node-item");
    outputItems.forEach((item, index) => {
      updateNodeOrderDisplay(item, index);
    });
  }
};

const updateNodeOrderDisplay = (item, index) => {
  const orderDisplay = item.querySelector(".node-order-display");
  if (orderDisplay) {
    const originalIndex = parseInt(item["data-original-index"]);
    const newOrderSpan = orderDisplay.querySelector(".new-order");

    if (newOrderSpan) {
      newOrderSpan.textContent = index + 1; // Display 1-based position for user friendliness
    }

    // Highlight changed orders
    if (originalIndex !== index) {
      newOrderSpan.style.color = "#4CAF50";
      newOrderSpan.style.fontWeight = "bold";
    } else {
      newOrderSpan.style.color = "#888888";
      newOrderSpan.style.fontWeight = "normal";
    }
  }
};

const processNodeItems = (items) => {
  const newItems = items.map((item, index) => {
    let nodeId = item["data-node-id"] || item.id;
    if (!nodeId) {
      console.warn("No node ID found for item:", item);
      return;
    }

    const node = app.graph.getNodeById(parseInt(nodeId));

    if (node) {
      // Store in properties for serialization - this is crucial for saving to workflow.json
      if (!node.properties) {
        node.properties = {};
      }
      node.properties.signature_order = index;
    } else {
      console.warn(`Node with ID ${nodeId} not found in graph`);
    }
    return node;
  });

  return newItems;
};

const applyNodeOrderChanges = () => {
  const allNodes = app.graph._nodes;
  const newOrder = [];
  const regularNodes = allNodes.filter(
    (node) => !node.type.includes("signature_input") && !node.type.includes("signature_output")
  );

  newOrder.push(...regularNodes);

  // Process input nodes - they always come first
  const inputList = document.getElementById("sortable-input-list");
  if (inputList) {
    // Fix: Use querySelectorAll to get all items properly
    const inputItems = inputList.childNodes;
    newOrder.push(...inputItems);
  }

  // Process output nodes - they always come last
  const outputList = document.getElementById("sortable-output-list");
  if (outputList) {
    // Fix: Use querySelectorAll to get all items properly
    const outputItems = outputList.childNodes;
    newOrder.push(...outputItems);
  }

  const newNodesOrder = processNodeItems(newOrder);
  app.graph._nodes = newNodesOrder;

  app.graph.setDirtyCanvas(true, true);

  app.graph.change();
};

const initDragAndDrop = (container) => {
  const items = container.querySelectorAll(".draggable-node-item");
  let draggedItem = null;

  items.forEach((item) => {
    // Make item draggable
    item.setAttribute("draggable", "true");

    // Add drag start event
    item.addEventListener("dragstart", function (e) {
      draggedItem = item;
      setTimeout(() => {
        item.style.opacity = "0.5";
      }, 0);
    });

    // Add drag end event
    item.addEventListener("dragend", function () {
      if (draggedItem) {
        draggedItem.style.opacity = "1";
        draggedItem = null;

        // Update the order display on all items
        updateOrderDisplay();
      }
    });

    // Add dragover event
    item.addEventListener("dragover", function (e) {
      e.preventDefault();
      if (this !== draggedItem && draggedItem) {
        const rect = this.getBoundingClientRect();
        const midpoint = (rect.top + rect.bottom) / 2;

        if (e.clientY < midpoint) {
          // Insert before
          if (this.previousElementSibling !== draggedItem) {
            container.insertBefore(draggedItem, this);
          }
        } else {
          // Insert after
          if (this.nextElementSibling !== draggedItem) {
            container.insertBefore(draggedItem, this.nextElementSibling);
          }
        }
      }
    });

    // Add drop event to ensure proper handling
    item.addEventListener("drop", function (e) {
      e.preventDefault();
      // The actual reordering is handled in dragover
    });
  });

  // Add dragover and drop handlers to the container itself
  container.addEventListener("dragover", function (e) {
    e.preventDefault();
  });

  container.addEventListener("drop", function (e) {
    e.preventDefault();
    if (draggedItem) {
      draggedItem.style.opacity = "1";
      updateOrderDisplay();
      draggedItem = null;
    }
  });
};

export {
  applyNodeOrderChanges,
  createNodeItem,
  initDragAndDrop,
  processNodeItems,
  showNodeOrderEditor,
  updateNodeOrderDisplay,
  updateOrderDisplay,
};

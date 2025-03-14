import { getWorkflowById, getWorkflowsListForForm, getWorkflowVersions } from "../../../signature_api/main.js";
import { $el, getTotalTabs, showMessage } from "../utils.js";

const showWorkflowsList = () => {
  let isLoading = true;
  let lastPageReached = false;
  let page = 0;
  let limit = 100;
  let searchQuery = null;
  let searchTimeout = null;

  const dialogContent = $el("div", [
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "100%",
        maxWidth: "full",
      },
      textContent: "Available Workflows",
    }),
    $el("div", {
      id: "workflows-container",
      style: {
        width: "90vw",
        maxWidth: "800px",
        margin: "0 auto",
      },
      $: async (container) => {
        // Create search container with input and buttons
        const searchContainer = $el("div", {
          style: {
            display: "flex",
            gap: "8px",
            marginBottom: "10px",
          },
        });

        // Add search input
        const searchInput = $el("input", {
          type: "text",
          placeholder: "Search workflows... (min 3 characters)",
          style: {
            flex: 1,
            padding: "8px",
            backgroundColor: "#2d2d2d",
            border: "1px solid #444",
            borderRadius: "4px",
            color: "white",
          },
          oninput: async (e) => {
            const inputValue = e.target.value;
            searchQuery = inputValue.length === 0 ? null : inputValue;

            if (searchTimeout) {
              clearTimeout(searchTimeout);
            }

            if (inputValue.length >= 3 || inputValue.length === 0) {
              // Show loading state
              resultsContainer.innerHTML = loadingHTML;

              // Reset pagination state
              page = 0;
              lastPageReached = false;

              searchTimeout = setTimeout(async () => {
                await loadWorkflows();
              }, 1000);
            }
          },
        });

        // Add clear button
        const clearButton = $el("button", {
          textContent: "Clear",
          style: {
            padding: "8px 16px",
            backgroundColor: "#666",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          },
          onclick: async () => {
            searchInput.value = "";
            searchQuery = null;
            if (searchTimeout) {
              clearTimeout(searchTimeout);
            }

            // Reset pagination state
            page = 0;
            lastPageReached = false;

            // Show loading state
            resultsContainer.innerHTML = loadingHTML;

            await loadWorkflows();
          },
        });

        searchContainer.append(searchInput, clearButton);

        // Create a fixed height results container
        const resultsContainer = $el("div", {
          id: "workflows-results",
          style: {
            height: "400px", // Fixed height
            overflowY: "auto",
            border: "1px solid #444",
            borderRadius: "4px",
            backgroundColor: "#1e1e1e",
            position: "relative", // For absolute positioning of loader
          },
        });

        // Loading HTML to display during searches
        const loadingHTML = `
          <div style="
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            width: 100%;
            background-color: #1e1e1e;
          ">
            <div style="
              width: 40px;
              height: 40px;
              border: 3px solid #2D9CDB;
              border-radius: 50%;
              border-top-color: transparent;
              animation: spin 1s linear infinite;
              margin-bottom: 15px;
            "></div>
            <div style="color: #ffffff;">Loading workflows...</div>
          </div>
        `;

        // Function to load workflows
        const loadWorkflows = async () => {
          if (isLoading && page > 0) return; // Prevent multiple simultaneous loads

          isLoading = true;

          try {
            const workflows = await getWorkflowsListForForm($el, page * limit, limit, searchQuery);

            // If this is the first page, clear the container
            if (page === 0) {
              resultsContainer.innerHTML = "";
            } else {
              // Remove loading trigger if it exists
              const existingTrigger = document.getElementById("workflows-loading-trigger");
              if (existingTrigger) {
                existingTrigger.remove();
              }
            }

            if (workflows.length === 0 && page === 0) {
              // Show no results message
              resultsContainer.innerHTML = `
                <div style="
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  height: 100%;
                  color: #888;
                ">
                  No workflows found
                </div>
              `;
              return;
            }

            // Add workflow elements to results container
            addWorkflowsToContainer(workflows);

            // Check if we've reached the last page
            if (workflows.length < limit) {
              lastPageReached = true;
            } else {
              // Add a loading trigger for infinite scroll
              addLoadingTrigger();
            }
          } catch (error) {
            console.error("Error loading workflows:", error);
            if (page === 0) {
              resultsContainer.innerHTML = `
                <div style="
                  display: flex;
                  justify-content: center;
                  align-items: center;
                  height: 100%;
                  color: #ff5555;
                ">
                  Error loading workflows: ${error.message}
                </div>
              `;
            }
          } finally {
            isLoading = false;
          }
        };

        // Helper function to add workflows to the container
        const addWorkflowsToContainer = (workflows) => {
          const workflowElements = workflows.map((workflow) =>
            $el(
              "div",
              {
                style: {
                  padding: "15px",
                  marginBottom: "10px",
                  backgroundColor: "#1e1e1e",
                  border: "1px solid #444",
                  borderRadius: "4px",
                  cursor: "pointer",
                  transition: "background-color 0.2s",
                },
                onmouseover: (e) => (e.target.style.backgroundColor = "#2a2a2a"),
                onmouseout: (e) => (e.target.style.backgroundColor = "#1e1e1e"),
                onclick: async () => {
                  const workflowData = await getWorkflowById(workflow.value);
                  if (workflowData) {
                    app.ui.dialog.close();
                    showWorkflowVersions(workflowData);
                  }
                },
              },
              [
                $el(
                  "div",
                  {
                    style: {
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "8px",
                    },
                  },
                  [
                    $el("span", {
                      style: {
                        fontSize: "16px",
                        fontWeight: "bold",
                        color: "#ffffff",
                      },
                      textContent: workflow.textContent,
                    }),
                    $el("span", {
                      style: {
                        fontSize: "14px",
                        color: "#888888",
                      },
                      textContent: workflow.type || "Standard",
                    }),
                  ]
                ),
              ]
            )
          );

          resultsContainer.append(...workflowElements);
        };

        // Helper function to add loading trigger
        const addLoadingTrigger = () => {
          // Remove any existing loading trigger first
          const existingTrigger = document.getElementById("workflows-loading-trigger");
          if (existingTrigger) {
            existingTrigger.remove();
          }

          // Don't add trigger if we've reached the last page
          if (lastPageReached) return;

          const loadingTrigger = $el("div", {
            id: "workflows-loading-trigger",
            style: {
              padding: "15px",
              textAlign: "center",
              color: "#888",
              marginTop: "10px",
            },
            innerHTML: `
              <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #888;
                          border-radius: 50%; border-top-color: transparent;
                          animation: spin 1s linear infinite;">
              </div>
              <div style="margin-top: 10px;">Loading more workflows...</div>
            `,
          });

          resultsContainer.appendChild(loadingTrigger);

          // Set up the intersection observer for this trigger
          if (observer) {
            observer.disconnect(); // Disconnect any existing observations
            observer.observe(loadingTrigger);
          }
        };

        // Create a style for the spinner animation if it doesn't exist
        if (!document.getElementById("workflow-spinner-style")) {
          const style = document.createElement("style");
          style.id = "workflow-spinner-style";
          style.textContent = `
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `;
          document.head.appendChild(style);
        }

        // Add elements to container
        container.append(searchContainer);
        container.append(resultsContainer);

        // Show loading state initially
        resultsContainer.innerHTML = loadingHTML;

        // Create the observer at a higher scope so it's accessible
        let observer;

        // Initial load of workflows
        await loadWorkflows();

        // Set up Intersection Observer to detect when loading trigger is visible
        setTimeout(() => {
          observer = new IntersectionObserver(
            async (entries) => {
              const entry = entries[0];

              if (entry.isIntersecting && !isLoading && !lastPageReached) {
                page++;
                await loadWorkflows();
              }
            },
            {
              root: resultsContainer,
              rootMargin: "100px",
              threshold: 0.1,
            }
          );

          // Set up the initial observation if we have a loading trigger
          const loadingTrigger = document.getElementById("workflows-loading-trigger");
          if (loadingTrigger) {
            observer.observe(loadingTrigger);
          }

          // Clean up observer when dialog closes
          const originalOnClose = app.ui.dialog.onClose;
          app.ui.dialog.onClose = () => {
            if (typeof originalOnClose === "function") {
              originalOnClose();
            }
            if (observer) {
              observer.disconnect();
            }
          };
        }, 500); // Give time for dialog to render
      },
    }),
  ]);

  app.ui.dialog.show(dialogContent);
  return dialogContent;
};

const showWorkflowVersions = (workflowData) => {
  const versionsDialog = $el("div", [
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "100%",
      },
      textContent: `Versions of "${workflowData.name}"`,
    }),
    $el("div", {
      style: {
        width: "90vw",
        maxWidth: "1000px",
        margin: "0 auto",
        maxHeight: "70vh",
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
        gap: "15px",
        padding: "10px",
      },
      $: async (container) => {
        let limit = 100;
        let page = 0;
        let lastPageReached = false;
        let isLoading = false;

        const loadVersions = async () => {
          if (isLoading) {
            return [];
          }

          try {
            isLoading = true;
            const response = await getWorkflowVersions(workflowData.uuid, page * limit, limit);
            const workflow_versions = response.data;
            if (workflow_versions.length === 0 || workflow_versions.length < limit) {
              lastPageReached = true;
            }

            return workflow_versions.map((workflow_version) => {
              const card = $el(
                "div",
                {
                  className: "workflow-version-card",
                  style: {
                    backgroundColor: "#1e1e1e",
                    borderRadius: "8px",
                    padding: "15px",
                    cursor: "pointer",
                    transition: "background-color 0.2s",
                  },
                  onclick: async () => {
                    app.ui.dialog.close();

                    try {
                      app.graph.clear();
                      app.loadGraphData(workflow_version.workflow);

                      const totalTabs = getTotalTabs();
                      localStorage.setItem(`workflow - ${totalTabs}`, workflow_version.uuid);

                      showMessage("Workflow loaded successfully!", "#00ff00");
                    } catch (error) {
                      console.error("Error loading workflow:", error);
                      showMessage("Failed to load workflow", "#ff0000", error.message);
                    }
                  },
                },
                [
                  // Cover image preview
                  $el(
                    "div",
                    {
                      style: {
                        width: "100%",
                        height: "150px",
                        marginBottom: "10px",
                        borderRadius: "4px",
                        overflow: "hidden",
                        backgroundColor: "#2a2a2a",
                      },
                    },
                    [
                      $el("img", {
                        src: workflow_version.coverImageUrl || "",
                        style: {
                          width: "100%",
                          height: "100%",
                          objectFit: "cover",
                        },
                        onerror: (e) => {
                          e.target.src =
                            "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23666' d='M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z'/%3E%3C/svg%3E";
                          e.target.style.padding = "40px";
                          e.target.style.boxSizing = "border-box";
                        },
                      }),
                    ]
                  ),
                  // Version info
                  $el(
                    "div",
                    {
                      style: {
                        fontSize: "14px",
                        color: "#ffffff",
                      },
                    },
                    [
                      $el("div", {
                        style: {
                          fontWeight: "bold",
                          marginBottom: "5px",
                        },
                        textContent: `Version ${workflow_version.version}`,
                      }),
                      $el("div", {
                        style: {
                          color: "#888888",
                          fontSize: "12px",
                        },
                        textContent: `Name: ${workflow_version.name}`,
                      }),
                      $el("div", {
                        style: {
                          color: "#888888",
                          fontSize: "12px",
                        },
                        textContent: `Created: ${new Date(workflow_version.createdAt).toLocaleString()}`,
                      }),
                      $el("div", {
                        style: {
                          color: "#888888",
                          fontSize: "12px",
                        },
                        textContent: `Updated: ${new Date(workflow_version.updatedAt).toLocaleString()}`,
                      }),
                    ]
                  ),
                ]
              );

              // Add hover events to the card
              card.addEventListener("mouseover", () => {
                card.style.backgroundColor = "#2a2a2a";
              });
              card.addEventListener("mouseout", () => {
                card.style.backgroundColor = "#1e1e1e";
              });

              return card;
            });
          } catch (error) {
            console.error("Error loading workflow versions:", error);
            container.appendChild(
              $el("div", {
                style: {
                  padding: "15px",
                  backgroundColor: "#ff000033",
                  color: "white",
                  marginBottom: "10px",
                  gridColumn: "1 / -1",
                },
                textContent: `Error: ${error.message}`,
              })
            );
            return [];
          } finally {
            isLoading = false;
          }
        };

        // Initial load
        const initialVersions = await loadVersions();
        container.append(...initialVersions);

        // Add a loading indicator at the bottom that also serves as a trigger
        const loadingTrigger = $el("div", {
          id: "versions-loading-trigger",
          style: {
            padding: "15px",
            textAlign: "center",
            color: "#888",
            display: lastPageReached ? "none" : "block",
            marginTop: "20px",
            gridColumn: "1 / -1",
          },
          innerHTML: `
            <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #888;
                        border-radius: 50%; border-top-color: transparent;
                        animation: spin 1s linear infinite;">
            </div>
            <div style="margin-top: 10px;">Loading more versions...</div>
          `,
        });
        container.appendChild(loadingTrigger);

        // Create a style for the spinner animation if it doesn't exist
        if (!document.getElementById("workflow-spinner-style")) {
          const style = document.createElement("style");
          style.id = "workflow-spinner-style";
          style.textContent = `
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `;
          document.head.appendChild(style);
        }

        // Set up Intersection Observer to detect when loading trigger is visible
        setTimeout(() => {
          const observer = new IntersectionObserver(
            async (entries) => {
              const entry = entries[0];

              if (entry.isIntersecting && !isLoading && !lastPageReached) {
                page++;
                const nextVersions = await loadVersions();

                if (nextVersions.length > 0) {
                  // Insert new versions before the loading trigger
                  nextVersions.forEach((version) => {
                    container.insertBefore(version, loadingTrigger);
                  });
                }

                // Hide loading trigger if we've reached the last page
                if (lastPageReached) {
                  loadingTrigger.style.display = "none";
                }
              }
            },
            {
              root: document.querySelector(".p-dialog-content"),
              rootMargin: "100px",
              threshold: 0.1,
            }
          );

          observer.observe(loadingTrigger);

          // Clean up observer when dialog closes
          const originalOnClose = app.ui.dialog.onClose;
          app.ui.dialog.onClose = () => {
            if (typeof originalOnClose === "function") {
              originalOnClose();
            }
            observer.disconnect();
          };
        }, 500); // Give time for dialog to render
      },
    }),
  ]);

  app.ui.dialog.show(versionsDialog);
};

export { showWorkflowsList };

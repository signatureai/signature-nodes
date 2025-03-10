import { app } from "../../scripts/app.js";
import {
  bypassNodes,
  checkNodeGroupPresence,
  findNodesWithRandomizedControlAfterGenerateWidget,
} from "./quality_checks/main.js";
import { $el, cleanLocalStorage, createMenuItem, requiresAuth, showMessage } from "./signature.js";
import { getWorkflowById, getWorkflowsListForForm, getWorkflowVersions } from "./signature_api/main.js";

const getTotalTabs = () => {
  const workflowTabs = document.querySelector(".workflow-tabs");
  if (!workflowTabs) return 1; // Default to 1 if no tabs container found

  const tabElements = workflowTabs.querySelectorAll(".workflow-tab");
  return tabElements.length || 1; // Return count of tabs, minimum 1
};

const populateSubmitForm = async (workflowId) => {
  const workflow = await getWorkflowById(workflowId);

  if (workflow) {
    const formContainer = document.getElementById("signature-workflow-submission-form");
    const nameInput = formContainer.querySelector('input[type="text"]');
    const descriptionInput = formContainer.querySelector("textarea");
    const typeSelect = formContainer.querySelector("select");
    const preview = document.getElementById("image-preview");
    const fileInput = formContainer.querySelector('input[type="file"]');

    // Update text fields and select
    if (nameInput && workflow.name) nameInput.value = workflow.name;
    if (descriptionInput && workflow.description) descriptionInput.value = workflow.description;
    if (typeSelect && workflow.type) {
      const type = workflow.type.toLowerCase();
      if (Array.from(typeSelect.options).some((opt) => opt.value === type)) {
        typeSelect.value = type;
      }
    }
    if (workflow.coverImageUrl) {
      preview.src = workflow.coverImageUrl;
      preview.style.display = "block";
      fileInput.value = "";
    }
  }
};

// Add a utility function for the spinner
function getLoadingSpinner(color) {
  if (!document.querySelector("#spinner-animation")) {
    const style = document.createElement("style");
    style.id = "spinner-animation";
    style.textContent = `
      @keyframes spin {
        to { transform: rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
  }

  return `
    <span class="loading-spinner" style="
      display: block;
      width: 80px;
      height: 80px;
      border: 3px solid ${color};
      border-radius: 50%;
      border-top-color: transparent;
      animation: spin 1s linear infinite;
    "></span>
  `;
}

async function getManifest(workflow) {
  try {
    const url = window.location.href + "flow/create_manifest";

    console.log("url", url);
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workflow: workflow,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error getting manifest:", errorText);
      throw new Error(`Failed to get manifest: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error in getManifest:", error);
    throw error;
  }
}

async function getApiFromUpdatedWorkflow(workflowData) {
  // Save current graph state
  const currentGraph = app.graph.serialize();

  try {
    // Clear the current graph
    app.graph.clear();

    // Instead of using app.loadGraphData, use LiteGraph's configure method directly
    // This loads the graph data without triggering UI-related actions like tab creation
    app.graph.configure(workflowData);

    // Generate API representation
    const graph_api = await app.graphToPrompt();

    return graph_api["output"];
  } catch (error) {
    console.error("Error generating API from workflow:", error);
    return null;
  }
}

const validateWorkflow = async (app) => {
  try {
    const initial_workflow = app.graph.serialize();

    const input_nodes_types = ["signature_input_image", "signature_input_text"];
    const output_nodes_types = ["signature_output"];
    const nodes_to_bypass = ["PreviewImage", "LoadImage", "signature_mask_preview", "signature_text_preview"];

    // Check for nodes with randomized control_after_generate widgets
    const nodesWithControlWidget = await findNodesWithRandomizedControlAfterGenerateWidget();

    if (nodesWithControlWidget && nodesWithControlWidget.cancelled) {
      // Don't proceed to the next dialog
      return { cancelled: true };
    }

    // Bypass the nodes of the list above and generate a new workflow
    const { workflow } = await bypassNodes(initial_workflow, nodes_to_bypass);
    // Change the displayed graph to the one generated above and create a new workflow api
    const workflow_api = await getApiFromUpdatedWorkflow(workflow);

    // Check if the workflow has the required nodes
    const input_nodes_presence = await checkNodeGroupPresence(workflow_api, workflow, input_nodes_types);

    if (input_nodes_presence.cancelled) {
      return { cancelled: true };
    }

    const output_nodes_presence = await checkNodeGroupPresence(workflow_api, workflow, output_nodes_types);

    if (output_nodes_presence.cancelled) {
      return { cancelled: true };
    }

    return { cancelled: false };
  } catch (error) {
    console.error("Error in validateWorkflow:", error);
    showMessage("An error occurred while validating the workflow", "#ff0000");
  }
};

async function saveWorkflow(app) {
  try {
    const validationResult = await validateWorkflow(app);

    if (validationResult && validationResult.cancelled) {
      return;
    }

    const form = await showForm();
    const submitButton = form.querySelector('a[href="#"]');

    submitButton.onclick = async (e) => {
      try {
        e.preventDefault();
        const workflowIdSelectedDiv = form.querySelector('div[data-selected="true"]');
        const workflowId = workflowIdSelectedDiv ? workflowIdSelectedDiv.getAttribute("data-workflow-id") : "";

        const formData = {
          baseWorkflowId: workflowId || "",
          name: form.querySelector('input[type="text"]').value,
          description: form.querySelector("textarea").value,
          type: form.querySelector("select").value,
          coverImage: form.querySelector('input[type="file"]').files[0],
          coverImageUrl: form.querySelector("#image-preview").src,
        };
        app.ui.dialog.close();

        showMessage("Generating manifest...", "#ffffff", null, "#00000000", getLoadingSpinner("#00ff00"));
        // Get manifest and check for missing dependencies
        const manifestResponse = await getManifest(workflow_api);
        const manifestData = JSON.parse(manifestResponse);

        if (manifestData.missing_nodes?.length || manifestData.missing_models?.length) {
          let errorMessage = "Cannot submit workflow due to missing dependencies:\n\n";
          let detailedInfo = "";

          if (manifestData.missing_nodes?.length) {
            detailedInfo += "Missing Nodes:\n- " + manifestData.missing_nodes.join("\n- ") + "\n\n";
          }

          if (manifestData.missing_models?.length) {
            detailedInfo += "Missing Models:\n- " + manifestData.missing_models.join("\n- ");
          }
          showMessage(errorMessage, "#ff0000", detailedInfo);
          return;
        }

        const submitData = new FormData();
        submitData.append("workflowUUID", formData.baseWorkflowId);
        submitData.append("workflowName", formData.name);
        submitData.append("workflowDescription", formData.description);
        submitData.append("workflowType", formData.type.toLowerCase());
        if (!formData.coverImage && formData.coverImageUrl) {
          submitData.append("coverImageUrl", formData.coverImageUrl);
        } else {
          submitData.append(
            "coverImage",
            formData.coverImage || new File([new Blob([""], { type: "image/png" })], "default.png")
          );
        }

        const workflowString = JSON.stringify(workflow, null, 2);
        const workflowBlob = new Blob([workflowString], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("workflowJson", workflowBlob, "workflow.json");

        const workflowApiString = JSON.stringify(workflow_api, null, 2);
        const workflowApiBlob = new Blob([workflowApiString], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("workflowApi", workflowApiBlob, "workflow-api.json");

        const manifest = await getManifest(workflow_api);
        const manifestBlob = new Blob([manifest], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("manifest", manifestBlob, "manifest.json");

        const url = window.location.href + "flow/submit_workflow";

        const response = await fetch(url, {
          method: "POST",
          body: submitData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`${response.status} - ${errorText}`);
        }

        showMessage("Workflow submitted successfully!", "#00ff00");
      } catch (error) {
        console.error("Error submitting workflow:", error);
        showMessage(error.message, "#ff0000");
      }
    };
  } catch (error) {
    console.error("Error in saveWorkflow:", error);
    showMessage("An error occurred while submitting the workflow", "#ff0000ff", error.message);
  }
}

function showForm() {
  const formContent = $el("div", { id: "signature-workflow-submission-form" }, [
    // Add title
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "100%",
        maxWidth: "full",
      },
      textContent: "Workflow Submission",
    }),
    $el(
      "div",
      {
        style: {
          width: "90vw",
          maxWidth: "800px",
          margin: "0 auto",
        },
      },
      [
        // Base Workflow ID field
        $el("div", { style: { marginBottom: "clamp(10px, 2vw, 20px)" } }, [
          $el("label", {
            style: {
              display: "block",
              marginBottom: "5px",
              fontSize: "clamp(14px, 2vw, 16px)",
              color: "white",
            },
            textContent: "Workflow",
          }),
          $el("div", {
            id: "workflow-selection-container",
            style: {
              width: "100%",
            },
            $: async (container) => {
              let limit = 100;
              let offset = 0;
              let isLoading = false;
              let hasMore = true;
              let searchQuery = null;
              let searchTimeout = null;

              // Create the options list container
              const optionsListContainer = $el("div", {
                id: "workflow-options-list",
                style: {
                  width: "100%",
                  maxHeight: "clamp(80px, 15vh, 120px)",
                  overflowY: "auto",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                  backgroundColor: "#1e1e1e",
                },
              });

              // Create the "Choose another option" button
              const changeButton = $el("button", {
                textContent: "Choose another option",
                style: {
                  width: "100%",
                  padding: "8px",
                  backgroundColor: "#2D9CDB",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  display: "none", // Hidden by default
                },
                onclick: () => {
                  changeButton.style.display = "none";
                  optionsListContainer.style.display = "block";
                },
              });

              container.append(changeButton, optionsListContainer);

              const initialOptions = [
                $el("option", { value: "", textContent: "Create new workflow" }),
                ...(await getWorkflowsListForForm($el, offset, limit, searchQuery)),
              ];

              optionsListContainer.append(
                ...initialOptions.map((opt, index) =>
                  $el("div", {
                    textContent: opt.textContent,
                    style: {
                      padding: "5px",
                      color: "white",
                      cursor: "pointer",
                      backgroundColor: index === 0 ? "#2D9CDB" : "transparent",
                    },
                    $: (el) => {
                      el.setAttribute("data-workflow-id", opt.value || "");
                      const currentTab = localStorage.getItem("Comfy.ActiveWorkflowIndex");
                      const currentWorkflow = localStorage.getItem(`workflow - ${currentTab}`);

                      if (index === 0) {
                        el.style.backgroundColor = "#2D9CDB";
                        el.setAttribute("data-selected", "true");
                      }

                      if (currentWorkflow) {
                        if (currentWorkflow === opt.value) {
                          el.style.backgroundColor = "#2D9CDB";
                          el.setAttribute("data-selected", "true");
                          populateSubmitForm(opt.value);

                          // If this is not the first option, hide the list and show the button
                          if (index > 0) {
                            optionsListContainer.style.display = "none";
                            changeButton.style.display = "block";
                            changeButton.textContent = `Current: ${opt.textContent}`;
                          }
                        } else {
                          el.style.backgroundColor = "transparent";
                          el.removeAttribute("data-selected");
                        }
                      }
                    },
                    onclick: async (e) => {
                      optionsListContainer.querySelectorAll("div").forEach((div) => {
                        div.style.backgroundColor = "transparent";
                        div.removeAttribute("data-selected");
                      });
                      e.target.style.backgroundColor = "#2D9CDB";
                      e.target.setAttribute("data-selected", "true");
                      const workflowId = e.target.getAttribute("data-workflow-id");

                      // If not selecting "Create new workflow", hide list and show button
                      if (workflowId) {
                        optionsListContainer.style.display = "none";
                        changeButton.style.display = "block";
                        changeButton.textContent = `Current: ${e.target.textContent}`;
                      } else {
                        changeButton.style.display = "none";
                        optionsListContainer.style.display = "block";
                      }

                      // Populate form fields with workflow data
                      populateSubmitForm(workflowId);
                    },
                  })
                )
              );

              // Existing scroll event listener code...
              optionsListContainer.addEventListener("scroll", async () => {
                console.log("isLoading", isLoading);
                console.log("hasMore", hasMore);
                if (isLoading || !hasMore) return;

                const scrolledToBottom =
                  optionsListContainer.scrollHeight - optionsListContainer.scrollTop <=
                  optionsListContainer.clientHeight + 50;

                if (scrolledToBottom) {
                  try {
                    isLoading = true;
                    offset += limit;

                    const nextOptions = await getWorkflowsListForForm($el, offset, limit, searchQuery);

                    if (nextOptions.length < limit) {
                      hasMore = false;
                    }

                    if (nextOptions.length > 0) {
                      optionsListContainer.append(
                        ...nextOptions.map((opt) =>
                          $el("div", {
                            textContent: opt.textContent,
                            style: {
                              padding: "5px",
                              color: "white",
                              cursor: "pointer",
                            },
                            $: (el) => {
                              el.setAttribute("data-workflow-id", opt.value || "");
                            },
                            onclick: (e) => {
                              optionsListContainer.querySelectorAll("div").forEach((div) => {
                                div.style.backgroundColor = "transparent";
                                div.removeAttribute("data-selected");
                              });
                              e.target.style.backgroundColor = "#2D9CDB";
                              e.target.setAttribute("data-selected", "true");
                              const workflowId = e.target.getAttribute("data-workflow-id");

                              // Hide list and show button when selecting an option
                              optionsListContainer.style.display = "none";
                              changeButton.style.display = "block";
                              changeButton.textContent = `Current: ${e.target.textContent}`;

                              populateSubmitForm(workflowId);
                            },
                          })
                        )
                      );
                    }
                  } catch (error) {
                    console.error("Error loading more workflows:", error);
                  } finally {
                    isLoading = false;
                  }
                }
              });
            },
          }),
        ]),
        // Name field
        $el("div", { style: { marginBottom: "clamp(10px, 2vw, 20px)" } }, [
          $el("label", {
            style: {
              display: "block",
              marginBottom: "5px",
              fontSize: "clamp(14px, 2vw, 16px)",
              color: "white",
            },
            textContent: "Name",
          }),
          $el("input", {
            type: "text",
            style: {
              width: "100%",
              padding: "clamp(5px, 1vw, 8px)",
              borderRadius: "4px",
              border: "1px solid #ccc",
              fontSize: "clamp(14px, 2vw, 16px)",
            },
          }),
        ]),
        // Description field
        $el("div", { style: { marginBottom: "clamp(10px, 2vw, 20px)" } }, [
          $el("label", {
            style: {
              display: "block",
              marginBottom: "5px",
              fontSize: "clamp(14px, 2vw, 16px)",
              color: "white",
            },
            textContent: "Description",
          }),
          $el("textarea", {
            style: {
              width: "100%",
              padding: "clamp(5px, 1vw, 8px)",
              borderRadius: "4px",
              border: "1px solid #ccc",
              minHeight: "clamp(100px, 20vh, 150px)",
              fontSize: "clamp(14px, 2vw, 16px)",
            },
          }),
        ]),
        // Type field
        $el("div", { style: { marginBottom: "clamp(10px, 2vw, 20px)" } }, [
          $el("label", {
            style: {
              display: "block",
              marginBottom: "5px",
              fontSize: "clamp(14px, 2vw, 16px)",
              color: "white",
            },
            textContent: "Type",
          }),
          $el(
            "select",
            {
              style: {
                width: "100%",
                padding: "clamp(5px, 1vw, 8px)",
                borderRadius: "4px",
                border: "1px solid #ccc",
                backgroundColor: "#1e1e1e",
                color: "white",
                height: "clamp(32px, 5vh, 40px)",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
            },
            [
              $el("option", { value: "standard", textContent: "Standard" }),
              $el("option", { value: "training", textContent: "Training" }),
            ]
          ),
        ]),
        // Cover Image field
        $el("div", { style: { marginBottom: "clamp(10px, 2vw, 20px)" } }, [
          $el("label", {
            style: {
              display: "block",
              marginBottom: "5px",
              fontSize: "clamp(14px, 2vw, 16px)",
              color: "white",
            },
            textContent: "Cover Image",
          }),
          $el("div", { style: { marginBottom: "10px" } }, [
            $el("input", {
              type: "file",
              accept: "image/png, image/jpeg, image/jpg",
              style: {
                width: "100%",
                padding: "clamp(5px, 1vw, 8px)",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
              onchange: function (e) {
                const file = e.target.files[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = function (e) {
                    const preview = document.getElementById("image-preview");
                    if (preview) {
                      preview.src = e.target.result;
                      preview.style.display = "block";
                    }
                  };
                  reader.readAsDataURL(file);
                }
              },
            }),
            $el("img", {
              id: "image-preview",
              style: {
                display: "none",
                maxWidth: "200px",
                maxHeight: "200px",
                marginTop: "10px",
                borderRadius: "4px",
                objectFit: "contain",
              },
            }),
          ]),
        ]),
        // Submit button
        $el("div", {
          innerHTML: `
          <a href="#"
             style="
               display: flex;
               align-items: center;
               gap: clamp(8px, 1vw, 12px);
               margin: clamp(10px, 2vw, 15px);
               padding: clamp(12px, 2vw, 16px) clamp(24px, 4vw, 32px);
               background-color: #2D9CDB;
               color: white;
               border: none;
               border-radius: 6px;
               cursor: pointer;
               text-decoration: none;
               font-size: clamp(14px, 2vw, 16px);
               transition: background-color 0.2s ease;
               justify-content: center;
               width: fit-content;
               margin-left: auto;
               margin-right: auto;
             "
             onmouseover="this.style.backgroundColor='#2486BE'"
             onmouseout="this.style.backgroundColor='#2D9CDB'"
          >
            <div style="text-align: center">Submit</div>
          </a>
        `,
        }),
      ]
    ),
  ]);

  // Don't convert to HTML string, just show the element directly
  app.ui.dialog.show(formContent);
  // Return the form content element directly
  return formContent;
}

function showWorkflowsList() {
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
}

// New function to show workflow versions with infinite scroll
async function showWorkflowVersions(workflowData) {
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
}

function deleteWorkflowFromStorage(tabIndex) {
  // Delete the workflow at the current index
  const currentKey = `workflow - ${tabIndex}`;
  localStorage.removeItem(currentKey);

  // Shift down indices for all subsequent workflows
  let nextIndex = tabIndex + 1;
  let nextKey = `workflow - ${nextIndex}`;

  while (localStorage.getItem(nextKey) !== null) {
    // Get the workflow from the next index
    const workflowData = localStorage.getItem(nextKey);
    // Move it to the previous index
    localStorage.setItem(`workflow - ${nextIndex - 1}`, workflowData);
    // Remove the old entry
    localStorage.removeItem(nextKey);

    // Move to next index
    nextIndex++;
    nextKey = `workflow - ${nextIndex}`;
  }
}

const findMenuList = () => {
  // Try different possible menu list IDs
  const possibleMenuLists = [
    "#pv_id_9_0_list",
    "#pv_id_10_0_list",
    ".p-menubar-root-list", // Backup selector
  ];

  for (const selector of possibleMenuLists) {
    const menuList = document.querySelector(selector);
    if (menuList) return menuList;
  }
  return null;
};

async function setupMenu(app) {
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
}

// New function to show node order editor dialog
function showNodeOrderEditor() {
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

                console.log("inputList", inputList.length);
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
}

// Helper function to create a node item
function createNodeItem(node, index, nodeType) {
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
}

// Update the order display on all items
function updateOrderDisplay() {
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
}

// Helper function to update a single node's order display
function updateNodeOrderDisplay(item, index) {
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
}

// Helper function to process node items and update their order
function processNodeItems(items) {
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
}

// Apply the new order to the actual nodes
function applyNodeOrderChanges() {
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
}

// Initialize drag and drop functionality
function initDragAndDrop(container) {
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
}

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

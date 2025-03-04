import { app } from "../../scripts/app.js";
import { $el, cleanLocalStorage, createMenuItem, requiresAuth, showMessage } from "./signature.js";
import { getWorkflowById, getWorkflowsListForForm, getWorkflowVersions } from "./signature_api/main.js";
import { checkNodesPresence } from "./tests/main.js";

const getTotalTabs = () => {
  const workflowTabs = document.querySelector(".workflow-tabs");
  if (!workflowTabs) return 1; // Default to 1 if no tabs container found

  const tabElements = workflowTabs.querySelectorAll(".workflow-tab");
  return tabElements.length || 1; // Return count of tabs, minimum 1
};

const populateSubmitForm = async (workflowId) => {
  const workflow = await getWorkflowById(workflowId);

  // Populate form fields with workflow data
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

async function saveWorkflow(app) {
  try {
    const workflow = app.graph.serialize();
    const graph_api = await app.graphToPrompt();
    const workflow_api = graph_api["output"];

    const form = await showForm();
    const submitButton = form.querySelector('a[href="#"]');
    // Check if the workflow has the required nodes
    await checkNodesPresence(workflow_api, workflow, ["signature_input", "signature_output"]);
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
              const limit = 100;
              let offset = 0;
              let isLoading = false;
              let hasMore = true;

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
                ...(await getWorkflowsListForForm($el, offset, limit)),
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
                if (isLoading || !hasMore) return;

                const scrolledToBottom =
                  optionsListContainer.scrollHeight - optionsListContainer.scrollTop <=
                  optionsListContainer.clientHeight + 50;

                if (scrolledToBottom) {
                  try {
                    isLoading = true;
                    offset += limit;

                    const nextOptions = await getWorkflowsListForForm($el, offset, limit);

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
        let limit = 100;
        let page = 0;
        let lastPageReached = false;
        let isLoading = false;

        const loadWorkflows = async () => {
          if (isLoading) {
            return [];
          }

          try {
            isLoading = true;
            const workflows = await getWorkflowsListForForm($el, page * limit, limit);

            if (workflows.length === 0 || workflows.length < limit) {
              lastPageReached = true;
            }

            return workflows.map((workflow) =>
              $el(
                "div",
                {
                  style: {
                    padding: "15px",
                    marginBottom: "10px",
                    backgroundColor: "#1e1e1e",
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
          } catch (error) {
            console.error("Error loading workflows:", error);
            container.appendChild(
              $el("div", {
                style: {
                  padding: "15px",
                  backgroundColor: "#ff000033",
                  color: "white",
                  marginBottom: "10px",
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
        const initialWorkflows = await loadWorkflows();
        container.append(...initialWorkflows);

        // Add a loading indicator at the bottom that also serves as a trigger
        const loadingTrigger = $el("div", {
          id: "workflows-loading-trigger",
          style: {
            padding: "15px",
            textAlign: "center",
            color: "#888",
            display: lastPageReached ? "none" : "block",
            marginTop: "20px",
          },
          innerHTML: `
            <div style="display: inline-block; width: 20px; height: 20px; border: 2px solid #888;
                        border-radius: 50%; border-top-color: transparent;
                        animation: spin 1s linear infinite;">
            </div>
            <div style="margin-top: 10px;">Loading more workflows...</div>
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
                const nextWorkflows = await loadWorkflows();

                if (nextWorkflows.length > 0) {
                  // Insert new workflows before the loading trigger
                  nextWorkflows.forEach((workflow) => {
                    container.insertBefore(workflow, loadingTrigger);
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

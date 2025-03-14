import { getWorkflowsListForForm } from "../../../signature_api/main.js";
import { $el } from "../utils.js";
import { populateSubmitForm } from "./utils.js";

const showForm = () => {
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
};

export { showForm };

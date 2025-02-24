import { app } from "../../scripts/app.js";
import {
  deleteAuthTokens,
  getAccessToken,
  getRefreshToken,
  getWorkflowById,
  getWorkflowsListForForm,
  loginRequest,
  refreshTokenRequest,
} from "./signature_api/main.js";

function showMessage(message, color, detailedInfo = null, backgroundColor = "#00000000", extraBody = null) {
  let dialogContent = `
      <div style="
        text-align: center;
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        width: 100%;
      ">
        <div style="
          display: flex;
          align-items: center;
          gap: 20px;
        ">
          ${extraBody || ""}
          <p style="
            color: ${color};
            font-size: 20px;
            margin: 0;
            text-align: center;
            background-color: ${backgroundColor};
          ">
            ${message}
          </p>
        </div>
        ${
          detailedInfo
            ? `
          <pre style="
            text-align: left;
            white-space: pre-wrap;
            margin: 0;
            background-color: rgba(0, 0, 0, 0.3);
            padding: 10px;
            border-radius: 4px;
            width: 100%;
          ">${detailedInfo}</pre>
        `
            : ""
        }
      </div>`;

  app.ui.dialog.show(dialogContent);
}

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

// Wraps the next function in an auth check
async function requiresAuth(app, next) {
  try {
    const dropdownMenu = document.querySelector("#pv_id_9_0_list");
    dropdownMenu.style.display = "none";
    // Try to get tokens
    let refreshToken = getRefreshToken();
    let accessToken = getAccessToken();
    if (refreshToken) {
      console.log("Trying to refresh token");
      try {
        const refreshTokenResponse = await refreshTokenRequest();
        if (refreshTokenResponse.success) {
          console.log("refreshTokenResponse", refreshTokenResponse);
          accessToken = refreshTokenResponse.accessToken;
          refreshToken = refreshTokenResponse.refreshToken;
          next(app);
          console.log("Token refreshed successfully");
        } else {
          throw new Error("Refresh token failed, success was false");
        }
      } catch (error) {
        console.error("Invalid refresh token, showing login form", error);
        deleteAuthTokens();
      }
    } else {
      console.log("Access token is invalid, showing login form");
      deleteAuthTokens();
      const loginForm = await showLoginForm();
      const loginButton = loginForm.querySelector('a[href="#"]');
      loginButton.onclick = async (e) => {
        e.preventDefault();
        const email = loginForm.querySelector("input[type='text']").value;
        const password = loginForm.querySelector("input[type='password']").value;
        try {
          const loginResponse = await loginRequest(email, password);
          if (loginResponse.success) {
            app.ui.dialog.close();
            next(app);
          } else {
            deleteAuthTokens();
            throw new Error("Login failed, success was false");
          }
        } catch (error) {
          console.error("Error in login:", error);
          deleteAuthTokens();
          showMessage("Login failed, please try again", "#ff0000");
        }
      };
    }

    // Re-check tokens after potential refresh
  } catch (error) {
    console.error("Auth error:", error);
    deleteAuthTokens();
    showMessage("Authentication failed", "#ff0000", error.message);
  }
}

async function saveWorkflow(app) {
  try {
    const workflow = app.graph.serialize();
    const graph_api = await app.graphToPrompt();
    const workflow_api = graph_api["output"];

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

function $el(tag, propsOrChildren, children) {
  const split = tag.split(".");
  const element = document.createElement(split.shift());
  if (split.length > 0) {
    element.classList.add(...split);
  }
  if (propsOrChildren) {
    if (typeof propsOrChildren === "string") {
      propsOrChildren = { textContent: propsOrChildren };
    } else if (propsOrChildren instanceof Element) {
      propsOrChildren = [propsOrChildren];
    }
    if (Array.isArray(propsOrChildren)) {
      element.append(...propsOrChildren);
    } else {
      const { parent, $: cb, dataset, style, ...rest } = propsOrChildren;
      if (rest.for) {
        element.setAttribute("for", rest.for);
      }
      if (style) {
        Object.assign(element.style, style);
      }
      if (dataset) {
        Object.assign(element.dataset, dataset);
      }
      Object.assign(element, rest);
      if (children) {
        element.append(...(Array.isArray(children) ? children : [children]));
      }
      if (parent) {
        parent.append(element);
      }
      if (cb) {
        cb(element);
      }
    }
  }
  return element;
}

function cleanLocalStorage() {
  const keysToRemove = [];
  // Iterate through all keys in session storage
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);

    // Check if the key is related to workflow data
    if (key.startsWith("Comfy.PreviousWorkflow") || key.startsWith("workflow")) {
      keysToRemove.push(key);
    }
  }

  // Remove the identified keys
  keysToRemove.forEach((key) => {
    localStorage.removeItem(key);
    // localStorage.setItem(key, cleanWorkflow)
  });
}

function showIframe(url, width = "1400px", height = "1400px", padding = "0px") {
  app.ui.dialog.show(
    $el("div", [
      $el("div", {
        style: {
          padding: padding,
          maxWidth: width,
          maxHeight: height,
          overflow: "hidden",
          backgroundColor: "rgba(0,0,0,0.2)",
        },
        innerHTML: `
            <iframe
              src="${url}"
              style="
                width: ${width};
                height: ${height};
                border: none;
                border-radius: 4px;
              "
            ></iframe>
          `,
      }),
    ]).outerHTML
  );
}

function showLoginForm() {
  const formContent = $el("div", [
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "100%",
        maxWidth: "500px",
      },
      textContent: "Login",
    }),
    $el(
      "div",
      {
        style: {
          width: "90vw",
          maxWidth: "500px",
          margin: "0 auto",
        },
      },
      [
        // Email field
        $el(
          "div",
          {
            style: {
              marginBottom: "10px",
            },
          },
          [
            $el("label", {
              style: {
                display: "block",
                marginBottom: "5px",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
              textContent: "Email",
            }),
            $el("input", {
              type: "text",
              placeholder: "Email",
              style: {
                width: "100%",
                padding: "clamp(4px, 1vw, 8px)",
                borderRadius: "4px",
                border: "1px solid #ccc",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
            }),
          ]
        ),
        // Password field
        $el(
          "div",
          {
            style: {
              marginBottom: "10px",
            },
          },
          [
            $el("label", {
              style: {
                display: "block",
                marginBottom: "5px",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
              textContent: "Password",
            }),
            $el("input", {
              type: "password",
              placeholder: "Password",
              style: {
                width: "100%",
                padding: "clamp(4px, 1vw, 8px)",
                borderRadius: "4px",
                border: "1px solid #ccc",
                fontSize: "clamp(14px, 2vw, 16px)",
              },
            }),
          ]
        ),
        // Login button
        $el("div", {
          innerHTML: `
          <a href="#"
             style="
               display: flex;
               align-items: center;
               gap: 8px;
               margin: clamp(8px, 2vw, 10px);
               padding: clamp(10px, 2vw, 12px) clamp(20px, 4vw, 24px);
               background-color: #2D9CDB;
               color: white;
               border: none;
               border-radius: 6px;
               cursor: pointer;
               text-decoration: none;
               font-size: clamp(14px, 2vw, 16px);
               transition: background-color 0.2s ease;
               justify-content: center;
               min-width: 120px;
               max-width: 100%;
             "
             onmouseover="this.style.backgroundColor='#2486BE'"
             onmouseout="this.style.backgroundColor='#2D9CDB'"
          >
            <div style="text-align: center">Login</div>
          </a>
        `,
        }),
      ]
    ),
  ]);

  app.ui.dialog.show(formContent);
  return formContent;
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
            style: {
              width: "100%",
              maxHeight: "clamp(80px, 15vh, 120px)",
              overflowY: "auto",
              border: "1px solid #ccc",
              borderRadius: "4px",
              backgroundColor: "#1e1e1e",
            },
            $: async (container) => {
              let limit = 100;
              let page = 0;
              let lastPageReached = false;
              const initialOptions = [
                $el("option", { value: "", textContent: "Create new workflow" }),
                ...(await getWorkflowsListForForm($el, page, limit)),
              ];
              container.append(
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
                      if (index === 0) el.setAttribute("data-selected", "true");
                    },
                    onclick: async (e) => {
                      container.querySelectorAll("div").forEach((div) => {
                        div.style.backgroundColor = "transparent";
                        div.removeAttribute("data-selected");
                      });
                      e.target.style.backgroundColor = "#2D9CDB";
                      e.target.setAttribute("data-selected", "true");
                      const workflowId = e.target.getAttribute("data-workflow-id");
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
                    },
                  })
                )
              );

              container.addEventListener("scroll", async (e) => {
                if (container.scrollHeight - container.scrollTop === container.clientHeight && !lastPageReached) {
                  console.log("Loading next workflows page");
                  // Load more items
                  page++;
                  const nextOptions = await getWorkflowsListForForm($el, page, limit);
                  if (nextOptions.length === 0 || nextOptions.length < limit) {
                    lastPageReached = true;
                  }
                  container.append(
                    ...nextOptions.map((opt, index) =>
                      $el("div", {
                        textContent: opt.textContent,
                        style: {
                          padding: "5px",
                          color: "white",
                          cursor: "pointer",
                        },
                        $: (el) => {
                          el.setAttribute("data-workflow-id", opt.value || "");
                          if (index === 0) el.setAttribute("data-selected", "true");
                        },
                        onclick: (e) => {
                          container.querySelectorAll("div").forEach((div) => {
                            div.style.backgroundColor = "transparent";
                            div.removeAttribute("data-selected");
                          });
                          e.target.style.backgroundColor = "#2D9CDB";
                          e.target.setAttribute("data-selected", "true");
                        },
                      })
                    )
                  );
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

function createMenuItem(label, iconClass, onClick) {
  const menuItem = $el(
    "li",
    {
      className: "p-menubar-item relative",
      role: "menuitem",
      "aria-label": label,
    },
    [
      $el("div", { className: "p-menubar-item-content" }, [
        $el(
          "a",
          {
            className: "p-menubar-item-link",
            "data-v-6fecd137": "",
            onclick: (event) => {
              event.preventDefault();
              event.stopPropagation();
              onClick();
            },
          },
          [
            $el("span", { className: `p-menubar-item-icon pi ${iconClass}` }),
            $el("span", { className: "p-menubar-item-label", textContent: label }),
          ]
        ),
      ]),
    ]
  );
  return menuItem;
}

const ext = {
  // Unique name for the extension
  name: "signature.bridge",
  async init(app) {
    cleanLocalStorage();
  },
  async setup(app) {
    if (app.menu) {
      // Find the menu list
      const menuList = document.querySelector("#pv_id_9_0_list");

      if (menuList) {
        // Add separator
        menuList.appendChild(
          $el("li", {
            className: "p-menubar-separator",
            role: "separator",
          })
        );

        // Add Open from Signature menu item
        menuList.appendChild(
          createMenuItem("Open from Signature", "pi-cloud-download", () => console.log("open from signature"))
        );

        // Add Deploy to Signature menu item
        menuList.appendChild(
          createMenuItem("Deploy to Signature", "pi-cloud-upload", () => requiresAuth(app, saveWorkflow))
        );
      }
    }
  },
};

app.registerExtension(ext);

import { app } from "../../scripts/app.js";

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
  // Tokens are stored in cookies
  let accessToken = document.cookie.match(/accessToken=([^;]+)/)?.[1];
  let refreshToken = document.cookie.match(/refreshToken=([^;]+)/)?.[1];

  if (refreshToken !== undefined && refreshToken !== null && refreshToken !== "") {
    console.log("Trying to refresh token");
    try {
      const refreshTokenResponse = await refreshTokenRequest();
      if (refreshTokenResponse.success) {
        accessToken = refreshTokenResponse.result.accessToken;
        accessTokenExpiresAt = refreshTokenResponse.result.expiresAt;
        refreshToken = refreshTokenResponse.result.refreshToken;

        document.cookie = `accessToken=${accessToken}; expires=${accessTokenExpiresAt}; path=/`;
        document.cookie = `refreshToken=${refreshToken}; path=/`;
        console.log("Token refreshed successfully");
      } else {
        throw new Error("Refresh token failed, success was false");
      }
    } catch (error) {
      console.error("Invalid refresh token, showing login form", error);
      accessToken = undefined;
      refreshToken = undefined;
      document.cookie = `accessToken=; path=/`;
      document.cookie = `refreshToken=; path=/`;
    }
  }

  if (!accessToken || !refreshToken) {
    console.log("Access token is invalid, showing login form");
    const loginForm = await showLoginForm();
    const loginButton = loginForm.querySelector('a[href="#"]');
    loginButton.onclick = async (e) => {
      e.preventDefault();
      const username = loginForm.querySelector("input[type='text']").value;
      const password = loginForm.querySelector("input[type='password']").value;
      try {
        const loginResponse = await loginRequest(username, password);
        if (loginResponse.success) {
          accessToken = loginResponse.result.accessToken;
          refreshToken = loginResponse.result.refreshToken;
          if (!accessToken || !refreshToken) {
            throw new Error("Login failed, access token or refresh token was not set");
          }
          document.cookie = `accessToken=${accessToken}; path=/`;
          document.cookie = `refreshToken=${refreshToken}; path=/`;
          app.ui.dialog.close();
          next(app);
        } else {
          throw new Error("Login failed, success was false");
        }
      } catch (error) {
        console.error("Error in login:", error);
        showMessage("Login failed, please try again", "#ff0000");
      }
    };
  } else {
    next(app);
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
        submitData.append(
          "coverImage",
          formData.coverImage || new File([new Blob([""], { type: "image/png" })], "default.png")
        );

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

const signatureApiBaseUrl = "https://signature-api-qa.signature-eks-staging.signature.ai";

async function loginRequest(email, password) {
  const url = `${signatureApiBaseUrl}/api/v1/user/login`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error(`Failed to login: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

async function refreshTokenRequest() {
  const refreshToken = document.cookie.match(/refreshToken=([^;]+)/)?.[1];

  const url = `${signatureApiBaseUrl}/api/v1/user/refresh-token`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${refreshToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to refresh token: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

function showLoginForm() {
  const formContent = $el("div", [
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "500px",
      },
      textContent: "Login",
    }),
    $el(
      "div",
      {
        style: {
          width: "500px",
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
              style: { display: "block", marginBottom: "5px" },
              textContent: "Email",
            }),
            $el("input", {
              type: "text",
              placeholder: "Email",
              style: {
                width: "100%",
                padding: "5px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              },
            }),
          ]
        ),
        $el(
          "div",
          {
            style: {
              marginBottom: "10px",
            },
          },
          [
            $el("label", {
              style: { display: "block", marginBottom: "5px" },
              textContent: "Password",
            }),
            $el("input", {
              type: "password",
              placeholder: "Password",
              style: {
                width: "100%",
                padding: "5px",
                borderRadius: "4px",
                border: "1px solid #ccc",
              },
            }),
          ]
        ),
        $el("div", {
          innerHTML: `
          <a href="#"
             style="
               display: flex;
               align-items: center;
               gap: 8px;
               margin: 10px;
               padding: 12px 24px;
               background-color: #2D9CDB;
               color: white;
               border: none;
               border-radius: 6px;
               cursor: pointer;
               text-decoration: none;
               font-size: 16px;
               transition: background-color 0.2s ease;
               justify-content: center;
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

async function getWorkflowsListForForm(page = 0, limit = 100) {
  const offset = page * limit;
  const accessToken = document.cookie.match(/accessToken=([^;]+)/)?.[1];
  const url = `${signatureApiBaseUrl}/api/v1_management/workflow?offset=${offset}&limit=${limit}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get workflows: ${response.status} ${response.statusText}`);
  }

  const parsedResponse = await response.json();
  if (parsedResponse.result && parsedResponse.result.data && parsedResponse.result.data.length !== 0) {
    return parsedResponse.result.data.map((workflow) => {
      return $el("option", { value: workflow.uuid, textContent: `${workflow.name} (${workflow.uuid})` });
    });
  } else {
    return [];
  }
}

function showForm() {
  const formContent = $el("div", [
    // Add title
    $el("h2", {
      style: {
        textAlign: "center",
        marginBottom: "20px",
        color: "#ffffff",
        width: "500px",
      },
      textContent: "Workflow Submission",
    }),
    $el(
      "div",
      {
        style: {
          width: "800px",
        },
      },
      [
        // Base Workflow ID field (new)
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Workflow",
          }),
          $el("div", {
            style: {
              width: "100%",
              maxHeight: "80px",
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
                ...(await getWorkflowsListForForm(page, limit)),
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

              container.addEventListener("scroll", async (e) => {
                console.log("scroll");
                if (container.scrollHeight - container.scrollTop === container.clientHeight && !lastPageReached) {
                  console.log("Loading next workflows page");
                  // Load more items
                  page++;
                  const nextOptions = await getWorkflowsListForForm(page, limit);
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
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Name",
          }),
          $el("input", {
            type: "text",
            style: {
              width: "100%",
              padding: "5px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            },
          }),
        ]),
        // Description field
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Description",
          }),
          $el("textarea", {
            style: {
              width: "100%",
              padding: "5px",
              borderRadius: "4px",
              border: "1px solid #ccc",
              minHeight: "100px",
            },
          }),
        ]),
        // Type field
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Type",
          }),
          $el(
            "select",
            {
              style: {
                width: "100%",
                padding: "5px",
                borderRadius: "4px",
                border: "1px solid #ccc",
                backgroundColor: "#1e1e1e",
                color: "white",
                height: "32px",
              },
            },
            [
              $el("option", { value: "standard", textContent: "Standard" }),
              $el("option", { value: "training", textContent: "Training" }),
            ]
          ),
        ]),
        // Cover Image field
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Cover Image",
          }),
          $el("input", {
            type: "file",
            accept: "image/*",
            style: {
              width: "100%",
              padding: "5px",
            },
          }),
        ]),
        // Submit button
        $el("div", {
          innerHTML: `
          <a href="#"
             style="
               display: flex;
               align-items: center;
               gap: 8px;
               margin: 10px;
               padding: 12px 24px;
               background-color: #2D9CDB;
               color: white;
               border: none;
               border-radius: 6px;
               cursor: pointer;
               text-decoration: none;
               font-size: 16px;
               transition: background-color 0.2s ease;
               justify-content: center;
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
      const menuList = document.querySelector("#pv_id_8_0_list");

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

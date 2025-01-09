import { app } from "../../scripts/app.js";

const urlParams = new URLSearchParams(window.location.search);
const env = urlParams.get("env");
const workflow_id = urlParams.get("workflow_id");
const token = urlParams.get("token");

const isInvalid = !env || !workflow_id || !token;
if (isInvalid) {
  console.log(
    "Signature Bridge: Missing required URL parameters (env, workflow_id, token). Extension not loaded.",
  );
}
let main_url = "https://api.signature.ai/api/v1";
if (env === "staging") {
  main_url = "https://api-staging.signature.ai/api/v1";
}
const url = main_url + `/workflows/${workflow_id}`;
const headers = getHeaders(token);

function getHeaders(token) {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  headers.append("Access-Control-Allow-Origin", "*");
  headers.append("Authorization", `Bearer ${token}`);
  return headers;
}

function showMessage(
  message,
  color,
  detailedInfo = null,
  backgroundColor = "#00000000",
  extraBody = null,
) {
  let dialogContent = `
      <div style="
        text-align: center;
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 20px;
        width: 100%;
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
        ${detailedInfo || ""}
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

async function loadWorkflow(app, url) {
  if (isInvalid) {
    return;
  }
  try {
    const response = await fetch(url, {
      method: "GET",
      headers: headers,
    });

    // Parse the workflow
    const get_workflow = await response.json();
    const get_workflow_data = JSON.parse(get_workflow["workflow"]);
    if (
      get_workflow_data &&
      get_workflow_data.version &&
      get_workflow_data.nodes &&
      get_workflow_data.extra
    ) {
      await app.loadGraphData(get_workflow_data, true, true);
    }
  } catch (error) {
    showMessage(
      "An Error occurred while loading the workflow from Signature",
      "#ff0000ff",
    );
  }
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
      throw new Error(
        `Failed to get manifest: ${response.status} ${response.statusText}`,
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error in getManifest:", error);
    throw error;
  }
}

async function getIO(workflow) {
  try {
    const url = window.location.href + "flow/workflow_data";
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
      console.error("Error getting IO:", errorText);
      throw new Error(`Failed to get IO: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    // Parse the JSON strings back into objects
    return data;
  } catch (error) {
    console.error("Error in getIO:", error);
    throw error;
  }
}

async function saveWorkflow(app) {
  try {
    const workflow = app.graph.serialize();
    const workflow_api = await app.graphToPrompt();

    const form = await showForm();
    // Update to find the submit button using a more reliable selector
    const submitButton = form.querySelector('a[href="#"]');
    submitButton.onclick = async (e) => {
      try {
        e.preventDefault();
        const formData = {
          name: form.querySelector('input[type="text"]').value,
          description: form.querySelector("textarea").value,
          type: form.querySelector("select").value,
          coverImage: form.querySelector('input[type="file"]').files[0],
        };
        app.ui.dialog.close();

        showMessage(
          "Generating manifest...",
          "#ffffff",
          null,
          "#00000000",
          getLoadingSpinner("#00ff00"),
        );

        const submitData = new FormData();
        submitData.append("workflowName", formData.name);
        submitData.append("workflowDescription", formData.description);
        submitData.append("workflowType", formData.type.toLowerCase());
        submitData.append(
          "coverImage",
          formData.coverImage ||
            new File([new Blob([""], { type: "image/png" })], "default.png"),
        );

        const workflowBlob = new Blob([JSON.stringify(workflow)], {
          type: "application/json",
        });
        submitData.append("workflowJson", workflowBlob, "workflow.json");

        const workflowApiBlob = new Blob([JSON.stringify(workflow_api)], {
          type: "application/json",
        });
        submitData.append("workflowApi", workflowApiBlob, "workflow-api.json");

        const manifest = await getManifest(workflow);
        const manifestBlob = new Blob([manifest], {
          type: "application/json",
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
    showMessage(
      "An error occurred while submitting the workflow",
      "#ff0000ff",
      error.message,
    );
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

function deleteElement(name) {
  const element = document.getElementsByClassName(name);
  // Check if any elements were found
  if (element.length > 0) {
    // Loop through each element and remove it from the DOM
    Array.from(element).forEach((el) => el.remove());
  }
}

function getCleanWorkflow() {
  const jsonString = `{
        "last_node_id": 0,
        "last_link_id": 0,
        "nodes": [],
        "links": [],
        "groups": [],
        "config": {},
        "extra": {
          "ds": {
          "scale": 0.5644739300537778,
          "offset": [
            581.6344764174625,
            97.05710697162648
          ]
          }
        },
        "version": 0.4
        }`;

  return JSON.stringify(JSON.parse(jsonString));
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
    ]).outerHTML,
  );
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
          width: "500px",
        },
      },
      [
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
            ],
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
      ],
    ),
  ]);

  // Don't convert to HTML string, just show the element directly
  app.ui.dialog.show(formContent);
  // Return the form content element directly
  return formContent;
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
        // First add a separator
        const separator = document.createElement("li");
        separator.className = "p-menubar-separator";
        separator.setAttribute("role", "separator");
        menuList.appendChild(separator);

        // Create "Open from Signature" menu item
        const openMenuItem = document.createElement("li");
        openMenuItem.className = "p-menubar-item relative";
        openMenuItem.setAttribute("role", "menuitem");
        openMenuItem.setAttribute("aria-label", "Open from Signature");

        const openItemContent = document.createElement("div");
        openItemContent.className = "p-menubar-item-content";

        const openItemLink = document.createElement("a");
        openItemLink.className = "p-menubar-item-link";
        openItemLink.setAttribute("data-v-6fecd137", "");

        const openIcon = document.createElement("span");
        openIcon.className = "p-menubar-item-icon pi pi-cloud-download";

        const openLabel = document.createElement("span");
        openLabel.className = "p-menubar-item-label";
        openLabel.textContent = "Open from Signature";

        openItemLink.appendChild(openIcon);
        openItemLink.appendChild(openLabel);
        openItemContent.appendChild(openItemLink);
        openMenuItem.appendChild(openItemContent);

        // Add click handler for Open
        openItemLink.onclick = async function (event) {
          event.preventDefault();
          event.stopPropagation();
          console.log("open from signature");
        };

        // Add Open menu item
        menuList.appendChild(openMenuItem);

        // Create Deploy menu item
        const newMenuItem = document.createElement("li");
        newMenuItem.className = "p-menubar-item relative";
        newMenuItem.setAttribute("role", "menuitem");
        newMenuItem.setAttribute("aria-label", "Deploy to Signature");

        const itemContent = document.createElement("div");
        itemContent.className = "p-menubar-item-content";

        const itemLink = document.createElement("a");
        itemLink.className = "p-menubar-item-link";
        itemLink.setAttribute("data-v-6fecd137", "");

        const icon = document.createElement("span");
        icon.className = "p-menubar-item-icon pi pi-cloud-upload";

        const label = document.createElement("span");
        label.className = "p-menubar-item-label";
        label.textContent = "Deploy to Signature";

        // Assemble the Deploy menu item
        itemLink.appendChild(icon);
        itemLink.appendChild(label);
        itemContent.appendChild(itemLink);
        newMenuItem.appendChild(itemContent);

        // Add click handler for Deploy
        itemLink.onclick = async function (event) {
          event.preventDefault();
          event.stopPropagation();
          await saveWorkflow(app);
        };

        // Add Deploy menu item
        menuList.appendChild(newMenuItem);
      }
    }
  },
};

app.registerExtension(ext);

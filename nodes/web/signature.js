import { app } from "../../scripts/app.js";

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
        ${detailedInfo
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
        const formData = {
          baseWorkflowId: form.querySelectorAll('input[type="text"]')[0].value,
          name: form.querySelectorAll('input[type="text"]')[1].value,
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
        // Get manifest and check for missing dependencies
        const manifestResponse = await getManifest(workflow_api);
        const manifestData = JSON.parse(manifestResponse);

        if (manifestData.missing_nodes?.length || manifestData.missing_models?.length) {
          let errorMessage = "Cannot submit workflow due to missing dependencies:\n\n";
          let detailedInfo = "";

          if (manifestData.missing_nodes?.length) {
            detailedInfo +=
              "Missing Nodes:\n- " + manifestData.missing_nodes.join("\n- ") + "\n\n";
          }

          if (manifestData.missing_models?.length) {
            detailedInfo +=
              "Missing Models:\n- " + manifestData.missing_models.join("\n- ");
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

        const manifest = await getManifest(workflow_api);
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
        // Base Workflow ID field (new)
        $el("div", { style: { marginBottom: "10px" } }, [
          $el("label", {
            style: { display: "block", marginBottom: "5px" },
            textContent: "Base Workflow ID",
          }),
          $el("input", {
            type: "text",
            style: {
              width: "100%",
              padding: "5px",
              borderRadius: "4px",
              border: "1px solid #ccc",
            },
            placeholder: "Optional: Enter base workflow ID",
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
          ],
        ),
      ]),
    ],
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
          }),
        );

        // Add Open from Signature menu item
        menuList.appendChild(
          createMenuItem("Open from Signature", "pi-cloud-download", () =>
            console.log("open from signature"),
          ),
        );

        // Add Deploy to Signature menu item
        menuList.appendChild(
          createMenuItem("Deploy to Signature", "pi-cloud-upload", () =>
            saveWorkflow(app),
          ),
        );
      }
    }
  },
};

app.registerExtension(ext);

import { app } from "../scripts/app.js";

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
) {
  let dialogContent = `
      <div>
        <p style="padding: 0px; color: ${color}; style="text-align: center": font-size: 20px; max-height: 50vh; overflow: auto; background-color:${backgroundColor};">
          ${message}
        </p>`;

  if (detailedInfo) {
    dialogContent += detailedInfo;
  }

  dialogContent += "</div>";
  app.ui.dialog.show(dialogContent);
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
    // Save the workflow

    const workflow = app.graph.serialize();

    console.log("Serialized workflow:", workflow);

    // showIframe("https://platform.signature.ai/org");
    showMessage("Generating Manifest", "#ffffffff");
    // // Get the IO
    // const io = await getIO(workflow_api);
    // console.log("Generated IO:", io);

    // Get the manifest
    const manifest = await getManifest(workflow);
    console.log("Generated manifest:", manifest);

    // let output_data = {
    //   workflow: workflow,
    //   workflow_api: workflow_api,
    //   manifest: JSON.parse(manifest),
    //   io: io,
    // };

    const dataStr = encodeURIComponent(manifest);
    const dialogContent = `
        <a href="data:application/json;charset=utf-8,${dataStr}"
           download="workflow-details.json"
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
           "
           onmouseover="this.style.backgroundColor='#2486BE'"
           onmouseout="this.style.backgroundColor='#2D9CDB'"
        >
          <div style="text-align: center">Download Details</div>
        </a>`;

    showMessage("Manifest generated", "#00ff00ff", dialogContent);

    // const data = {
    //   workflow: JSON.stringify(workflow),
    //   workflow_api: JSON.stringify(workflow_api["output"]),
    //   manifest: manifest
    // };

    // const response = await fetch(url, {
    //   method: "PUT",
    //   headers: headers,
    //   body: JSON.stringify(data),
    // });

    // if (response.ok) {
    //   showMessage("Workflow deployed to Signature", "#00ff00ff");
    // } else {
    //   showMessage(
    //     "An Error occurred while deploying the workflow to Signature",
    //     "#ff0000ff",
    //   );
    // }
  } catch (error) {
    console.error("Error in saveWorkflow:", error);
    showMessage(
      "An Error occurred while deploying the workflow to Signature",
      "#ff0000ff",
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

const ext = {
  // Unique name for the extension
  name: "signature.bridge",
  async init(app) {
    cleanLocalStorage();
    deleteElement("comfyui-logo");
  },
  async setup(app) {
    // await instance.loadGraphData(empty_workflow, true, true);
    // await loadWorkflow(app, url);
    if (app.menu) {
      // Ensure the ComfyAppMenu is available
      if (app.bodyTop) {
        const menuItems =
          app.bodyTop.children[0].children[0].children[1].children[0].children[1]
            .children;
        for (let i = 0; i < menuItems.length; i++) {
          const element = menuItems[i];
          if (
            element.ariaLabel === "Save As" ||
            element.innerText === "Browse Templates"
          ) {
            element.parentNode.removeChild(element);
          }
          // if (element.ariaLabel === 'Open') {
          //   const link = element.children[0].children[0];
          //   const label = link.children[1];
          //   label.textContent = "Open from Signature";
          //   link.onclick = async function (event) {
          //     event.preventDefault();
          //     event.stopPropagation();
          //     console.log("open workflow");
          //     // await saveWorkflow(app);
          //   };
          // }
          if (element.ariaLabel === "Save") {
            const link = element.children[0].children[0];
            const icon = link.children[0];
            const label = link.children[1];
            icon.className = "p-menubar-item-icon pi pi-upload";
            label.textContent = "Publish to Signature";

            link.onclick = async function (event) {
              event.preventDefault();
              event.stopPropagation();
              console.log("save workflow");
              await saveWorkflow(app);
            };
          }
        }
      }
      if (app.bodyLeft) {
        const menuItems = app.bodyLeft.children[0].children;
        for (let i = 0; i < menuItems.length; i++) {
          const element = menuItems[i];
          if (element.ariaLabel === "Workflows") {
            element.parentNode.removeChild(element);
            break;
          }
        }
      }
    }
  },
};

app.registerExtension(ext);

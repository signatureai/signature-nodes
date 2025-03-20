import { app } from "../../../../scripts/app.js";
import {
  deleteAuthTokens,
  getAccessToken,
  getRefreshToken,
  loginRequest,
  refreshTokenRequest,
} from "../../signature_api/main.js";
import { saveWorkflow } from "./form/main.js";
import { showWorkflowsList } from "./list/main.js";
import { showNodeOrderEditor } from "./node_order/main.js";

import { $el, createMenuItem, findMenuList } from "../global/main.js";

const showMessage = (message, color, detailedInfo = null, backgroundColor = "#00000000", extraBody = null) => {
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
};

const getTotalTabs = () => {
  const workflowTabs = document.querySelector(".workflow-tabs");
  if (!workflowTabs) return 1; // Default to 1 if no tabs container found

  const tabElements = workflowTabs.querySelectorAll(".workflow-tab");
  return tabElements.length || 1; // Return count of tabs, minimum 1
};

const getLoadingSpinner = (color) => {
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
};

const deleteWorkflowFromStorage = (tabIndex) => {
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
};

const cleanLocalStorage = () => {
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
};

const showIframe = (url, width = "1400px", height = "1400px", padding = "0px") => {
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
};

const showLoginForm = () => {
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
};

const requiresAuth = async (app, next) => {
  try {
    // Try to get tokens
    let refreshToken = getRefreshToken();
    let accessToken = getAccessToken();
    if (refreshToken) {
      try {
        const refreshTokenResponse = await refreshTokenRequest();
        if (refreshTokenResponse.success) {
          accessToken = refreshTokenResponse.accessToken;
          refreshToken = refreshTokenResponse.refreshToken;
          next(app);
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
};

const setupMenu = async (app) => {
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
};

export {
  $el,
  cleanLocalStorage,
  createMenuItem,
  deleteWorkflowFromStorage,
  findMenuList,
  getLoadingSpinner,
  getTotalTabs,
  requiresAuth,
  setupMenu,
  showIframe,
  showLoginForm,
  showMessage,
};

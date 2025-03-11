import { app } from "../../scripts/app.js";
import { showMessage } from "./helpers/global/main.js";
import {
  deleteAuthTokens,
  getAccessToken,
  getRefreshToken,
  loginRequest,
  refreshTokenRequest,
} from "./signature_api/main.js";

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

async function requiresAuth(app, next) {
  try {
    const dropdownMenu = document.querySelector("#pv_id_9_0_list") || document.querySelector("#pv_id_10_0_list");
    dropdownMenu.style.display = "none";
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
}

// Export the functions needed by workflows.js
export { $el, cleanLocalStorage, createMenuItem, requiresAuth, showIframe, showLoginForm, showMessage };

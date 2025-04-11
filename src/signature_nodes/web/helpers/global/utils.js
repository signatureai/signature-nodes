const $el = (tag, propsOrChildren, children) => {
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
};

const createMenuItem = (label, iconClass, onClick) => {
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
};

const addSignatureMenu = () => {
  const menuList = document.querySelector(".p-menubar-root-list");

  // Create main menu item
  const signatureMenu = $el("li", {
    className: "p-menubar-item relative",
    role: "menuitem",
    "aria-label": "Signature",
    "aria-expanded": "false",
    "aria-haspopup": "true",
    id: "signature-menu",
  });

  // Create dropdown content
  const dropdownContent = $el("ul", {
    className: "p-menubar-submenu dropdown-direction-down",
    role: "menu",
    style: {
      display: "none",
    },
  });

  // Create the main menu button
  const menuButton = $el("div", {
    className: "p-menubar-item-content",
    "data-pc-section": "itemcontent",
  });

  // Create the menu link with click handler
  const menuLink = $el("a", {
    className: "p-menubar-item-link",
    "data-pc-section": "itemlink",
    href: "#",
    onclick: (e) => {
      e.preventDefault();
      e.stopPropagation();

      // Close any other open menus first
      document
        .querySelectorAll('.p-menubar-item[aria-expanded="true"]')
        .forEach((menu) => menu.setAttribute("aria-expanded", "false"));

      // Toggle this menu
      const isExpanded = signatureMenu.getAttribute("aria-expanded") === "true";
      signatureMenu.setAttribute("aria-expanded", !isExpanded);
      dropdownContent.style.display = isExpanded ? "none" : "flex";
    },
  });

  const menuLabel = $el("span", {
    className: "p-menubar-item-label",
  });
  menuLabel.textContent = "Signature";

  // Assemble the menu
  menuLink.appendChild(menuLabel);
  menuButton.appendChild(menuLink);
  signatureMenu.appendChild(menuButton);
  signatureMenu.appendChild(dropdownContent);

  // Close menu when clicking outside
  document.addEventListener("click", (e) => {
    if (!signatureMenu.contains(e.target)) {
      signatureMenu.setAttribute("aria-expanded", "false");
      dropdownContent.style.display = "none";
    }
  });

  // Handle escape key to close dropdown
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && signatureMenu.getAttribute("aria-expanded") === "true") {
      signatureMenu.setAttribute("aria-expanded", "false");
      dropdownContent.style.display = "none";
    }
  });

  menuList.insertBefore(signatureMenu, menuList.children[2]);
};

// Call the function to add the menu
addSignatureMenu();

const findSignatureMenuList = () => {
  const menuList = document.querySelector("#signature-menu");

  const signatureMenu = Array.from(menuList.children).find((child) => child.localName === "ul");

  if (signatureMenu) return signatureMenu;
  return null;
};

export { $el, createMenuItem, findSignatureMenuList };

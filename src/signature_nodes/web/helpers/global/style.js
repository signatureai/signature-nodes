import { $el } from "./utils.js";

const dropdownMenuSeparator = $el("li", {
  className: "p-menubar-separator",
  role: "separator",
  "data-signature-menu": "true",
});

export { dropdownMenuSeparator };

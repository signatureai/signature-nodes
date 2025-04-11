import { app } from "../../../../scripts/app.js";
import { $el, createMenuItem, findSignatureMenuList, preventDefaultDrag } from "./helpers/global/main.js";
import {
  buttonsContainer,
  dropArea,
  dropText,
  fileInput,
  fileLabel,
  form,
  modalContent,
  MODEL_TYPES,
  selectedFileName,
  statusMessage,
  title,
  typeLabel,
  typeSelect,
  uploadButton,
} from "./helpers/upload_local_model/main.js";

const createUploadModal = () => {
  MODEL_TYPES.forEach((type) => {
    const option = $el("option", {
      value: type,
      textContent: type.charAt(0).toUpperCase() + type.slice(1).replace(/_/g, " "),
    });
    typeSelect.appendChild(option);
  });

  dropArea.appendChild(dropText);
  dropArea.appendChild(selectedFileName);
  dropArea.appendChild(fileInput);

  // Add drag and drop events
  dropArea.addEventListener("dragenter", (e) => {
    preventDefaultDrag(e);
    dropArea.style.borderColor = "#64B5F6";
    dropArea.style.backgroundColor = "#363636";
  });

  dropArea.addEventListener("dragover", (e) => {
    preventDefaultDrag(e);
    dropArea.style.borderColor = "#64B5F6";
    dropArea.style.backgroundColor = "#363636";
  });

  dropArea.addEventListener("dragleave", (e) => {
    preventDefaultDrag(e);
    dropArea.style.borderColor = "#444";
    dropArea.style.backgroundColor = "#2b2b2b";
  });

  dropArea.addEventListener("drop", (e) => {
    preventDefaultDrag(e);
    dropArea.style.borderColor = "#444";
    dropArea.style.backgroundColor = "#2b2b2b";

    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      selectedFileName.textContent = e.dataTransfer.files[0].name;
      selectedFileName.style.display = "block";
    }
  });

  // Handle click to select file
  dropArea.addEventListener("click", () => {
    fileInput.click();
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files.length) {
      selectedFileName.textContent = fileInput.files[0].name;
      selectedFileName.style.display = "block";
    }
  });

  buttonsContainer.append(uploadButton);
  form.append(typeLabel, typeSelect, fileLabel, dropArea, buttonsContainer);
  modalContent.append(title, form, statusMessage);

  app.ui.dialog.show(modalContent);
};

// Add menu item
const menuList = findSignatureMenuList();
if (menuList) {
  // Create the menu item with icon and click handler
  const uploadModelItem = createMenuItem("Upload Local Model", "pi-upload", createUploadModal);

  // Add divider after the menu item
  const divider = $el("li", {
    className: "p-menubar-separator",
    role: "separator",
    "data-signature-menu": "true",
  });

  // Insert both at the beginning of the menu
  menuList.insertBefore(divider, menuList.firstChild);
  menuList.insertBefore(uploadModelItem, menuList.firstChild);
}

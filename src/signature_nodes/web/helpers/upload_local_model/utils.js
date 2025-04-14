import { $el, preventDefaultDrag } from "../global/utils.js";
import {
  buttonsContainerStyle,
  dropAreaStyle,
  dropTextStyle,
  fileInputStyle,
  fileLabelStyle,
  formStyle,
  modalContentStyle,
  refreshDialogStyle,
  refreshLaterButtonStyle,
  refreshMessageStyle,
  refreshNowButtonStyle,
  refreshTitleStyle,
  selectedFileNameStyle,
  statusMessageStyle,
  titleStyle,
  typeLabelStyle,
  typeSelectStyle,
  uploadButtonStyle,
} from "./style.js";

// Define supported model types
const MODEL_TYPES = [
  "checkpoints", // Base models
  "vae", // VAE models
  "loras", // LoRA models
  "controlnet", // ControlNet models
  "upscale_models", // Upscale models
  "clip_vision", // CLIP Vision models
  "style_models", // Style models
  "embeddings", // Textual inversion embeddings
  "hypernetworks", // Hypernetworks
  "diffusion_models", // UNET models
];

const modalContent = $el("div", {
  style: modalContentStyle,
  ondragenter: preventDefaultDrag,
  ondragover: preventDefaultDrag,
  ondrop: preventDefaultDrag,
});

const title = $el("h3", {
  textContent: "Upload Local Model",
  style: titleStyle,
});

const statusMessage = $el("div", {
  style: statusMessageStyle,
});

const form = $el("form", {
  style: formStyle,
  ondragenter: preventDefaultDrag,
  ondragover: preventDefaultDrag,
  ondrop: preventDefaultDrag,
});

// Model type dropdown
const typeLabel = $el("label", {
  textContent: "Model Type:",
  style: typeLabelStyle,
});

const typeSelect = $el("select", {
  style: typeSelectStyle,
});

// File input area
const fileLabel = $el("label", {
  textContent: "Model File:",
  style: fileLabelStyle,
});

const dropArea = $el("div", {
  style: dropAreaStyle,
  ondragenter: preventDefaultDrag,
  ondragover: preventDefaultDrag,
  ondrop: preventDefaultDrag,
});

const fileInput = $el("input", {
  type: "file",
  accept: ".ckpt,.safetensors,.pt,.pth,.bin",
  style: fileInputStyle,
});

const dropText = $el("div", {
  textContent: "Drop your model file here or click to select",
  style: dropTextStyle,
});

const selectedFileName = $el("div", {
  style: selectedFileNameStyle,
});
// Create refresh dialog
const refreshDialog = $el("div", {
  style: refreshDialogStyle,
});

const refreshTitle = $el("h3", {
  textContent: "Model Uploaded Successfully",
  style: refreshTitleStyle,
});

const refreshMessage = $el("div", {
  textContent: "Please refresh the page to use the uploaded model",
  style: refreshMessageStyle,
});

const buttonsContainer = $el("div", {
  style: buttonsContainerStyle,
});

const refreshNowButton = $el("button", {
  textContent: "Refresh Now",
  onclick: () => {
    window.location.reload();
  },
  style: refreshNowButtonStyle,
  onmouseenter: (e) => {
    e.target.style.backgroundColor = "#1976d2";
  },
  onmouseleave: (e) => {
    e.target.style.backgroundColor = "#4CAF50";
  },
});

const refreshLaterButton = $el("button", {
  textContent: "Refresh Later",
  onclick: () => {
    app.ui.dialog.close();
  },
  style: refreshLaterButtonStyle,
  onmouseenter: (e) => {
    e.target.style.backgroundColor = "#555";
  },
  onmouseleave: (e) => {
    e.target.style.backgroundColor = "#444";
  },
});

const showStatus = (message, type) => {
  statusMessage.textContent = message;
  statusMessage.style.display = "block";

  if (type === "success") {
    statusMessage.style.backgroundColor = "#43a047";
    statusMessage.style.color = "white";

    buttonsContainer.innerHTML = [];
    buttonsContainer.append(refreshNowButton, refreshLaterButton);
    refreshDialog.append(refreshTitle, refreshMessage, buttonsContainer);

    // Close the upload dialog and show the refresh dialog
    app.ui.dialog.close();
    app.ui.dialog.show(refreshDialog);
  } else if (type === "error") {
    statusMessage.style.backgroundColor = "#d32f2f";
    statusMessage.style.color = "white";
  } else if (type === "progress") {
    statusMessage.style.backgroundColor = "#1e88e5";
    statusMessage.style.color = "white";
  }
};

const uploadButton = $el("button", {
  textContent: "Upload",
  onclick: async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
      showStatus("Please select a file to upload", "error");
      return;
    }

    const file = fileInput.files[0];
    const modelType = typeSelect.value;

    try {
      showStatus("Uploading model...", "progress");
      uploadButton.disabled = true;
      uploadButton.style.opacity = "0.7";
      uploadButton.style.cursor = "not-allowed";

      // Create FormData
      const formData = new FormData();
      formData.append("file", file);
      formData.append("type", modelType);
      formData.append("overwrite", "true");

      try {
        const response = await fetch("/upload/local-model", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(errorText || `HTTP ${response.status}`);
        }

        const result = await response.json();
        showStatus("Model uploaded successfully!", "success");
      } catch (error) {
        showStatus(error.message || "Failed to upload model", "error");
      }
    } catch (error) {
      showStatus(`Error uploading model: ${error.message}`, "error");
    } finally {
      uploadButton.disabled = false;
      uploadButton.style.opacity = "1";
      uploadButton.style.cursor = "pointer";
    }
  },
  style: uploadButtonStyle,
  onmouseenter: (e) => {
    if (!e.target.disabled) {
      e.target.style.backgroundColor = "#1976d2";
    }
  },
  onmouseleave: (e) => {
    if (!e.target.disabled) {
      e.target.style.backgroundColor = "#1e88e5";
    }
  },
});

export {
  buttonsContainer,
  dropArea,
  dropText,
  fileInput,
  fileLabel,
  form,
  modalContent,
  MODEL_TYPES,
  refreshDialog,
  refreshLaterButton,
  refreshMessage,
  refreshNowButton,
  refreshTitle,
  selectedFileName,
  showStatus,
  statusMessage,
  title,
  typeLabel,
  typeSelect,
  uploadButton,
};

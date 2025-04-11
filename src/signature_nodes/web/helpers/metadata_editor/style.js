const dialog = document.createElement("div");
dialog.className = "dialog-edit-metadata";
dialog.style.position = "fixed";
dialog.style.top = "50%";
dialog.style.left = "50%";
dialog.style.transform = "translate(-50%, -50%)";
dialog.style.backgroundColor = "#333";
dialog.style.padding = "20px";
dialog.style.borderRadius = "5px";
dialog.style.zIndex = "1000";
dialog.style.minWidth = "500px";

// Create title
const title = document.createElement("h3");
title.textContent = "Edit Node Metadata";
title.style.marginTop = "0";

// Create save and cancel buttons
const buttonContainer = document.createElement("div");
buttonContainer.style.marginTop = "20px";
buttonContainer.style.display = "flex";
buttonContainer.style.justifyContent = "space-between";

// Create metadata editor
const metadataContainer = document.createElement("div");
metadataContainer.style.marginBottom = "20px";

const saveButton = document.createElement("button");
saveButton.textContent = "Save";
saveButton.style.backgroundColor = "#4CAF50";
saveButton.style.color = "white";
saveButton.style.border = "none";
saveButton.style.padding = "10px 20px";
saveButton.style.cursor = "pointer";

const cancelButton = document.createElement("button");
cancelButton.textContent = "Cancel";
cancelButton.style.backgroundColor = "#f44336";
cancelButton.style.color = "white";
cancelButton.style.border = "none";

export { buttonContainer, cancelButton, dialog, metadataContainer, saveButton, title };

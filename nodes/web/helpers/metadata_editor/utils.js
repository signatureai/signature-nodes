import { buttonContainer, cancelButton, dialog, metadataContainer, saveButton, title } from "./style.js";

const genericMetadataFields = [
  {
    name: "tooltip",
    type: "string",
  },
  {
    name: "hide_on_null_id",
    type: "string",
  },
  {
    name: "hide",
    type: "boolean",
  },
];

const metadataDefaultValues = {
  signature_input_text: {
    type: "keep one: models or models_object",
  },
  signature_input_number: {
    clamp: "{ min: number, max: number }",
  },
};
const metadataFields = {
  signature_input_text: [
    {
      name: "type",
      type: "string",
      default: metadataDefaultValues.signature_input_text.type,
    },
    ...genericMetadataFields,
  ],
  signature_input_number: [
    {
      name: "clamp",
      type: "string",
      default: metadataDefaultValues.signature_input_number.clamp,
    },
    ...genericMetadataFields,
  ],
  signature_input_image: [
    {
      name: "mask_id",
      type: "string",
    },
    ...genericMetadataFields,
  ],
  signature_output: genericMetadataFields,
  signature_input_boolean: genericMetadataFields,
};

const nodeTypesWithMetada = [
  "signature_input_boolean",
  "signature_input_text",
  "signature_input_number",
  "signature_input_image",
  "signature_output",
];

const getNodeMetadataWidget = (node) => {
  const metadata_widget = node.widgets.find((widget) => widget.name === "metadata");
  const parsed_metadata_widget = JSON.parse(metadata_widget.value);
  const signature_metadata = node.properties.signature_metadata;
  return { metadata_widget, parsed_metadata_widget, signature_metadata };
};

const removeMetadataContainer = () => {
  const rows = metadataContainer.querySelectorAll(".metadata-row");
  rows.forEach((row) => row.remove());
  document.body.removeChild(dialog);
};

// Function to handle the metadata editing
const editNodeMetadata = (node) => {
  // Create a modal dialog for editing metadata

  dialog.appendChild(title);

  let fieldsToShow = [];
  const nodeType = node.type;

  if (!nodeTypesWithMetada.includes(nodeType)) {
    return;
  }

  // If node has no signature_metadata, initialize it
  if (!node.properties.signature_metadata) {
    node.properties.signature_metadata = {};
  }

  // Get the appropriate metadata fields for this node type

  if (metadataFields[nodeType]) {
    fieldsToShow = metadataFields[nodeType];
  }

  // Handle the case where fieldsToShow is not an array (like in "signature_input_image")
  if (!Array.isArray(fieldsToShow)) {
    fieldsToShow = [fieldsToShow]; // Convert to array with single item
  }

  const { metadata_widget, parsed_metadata_widget, signature_metadata } = getNodeMetadataWidget(node);
  // Create inputs for metadata fields
  fieldsToShow.forEach((field) => {
    const row = createMetadataFieldRow(
      field,
      signature_metadata[field.name] || parsed_metadata_widget[field.name] || field.default || ""
    );

    metadataContainer.appendChild(row);
  });

  dialog.appendChild(metadataContainer);

  saveButton.onclick = function () {
    // Save metadata from inputs
    const rows = metadataContainer.querySelectorAll(".metadata-row");
    rows.forEach((row) => {
      const fieldName = row.dataset.fieldName;
      const valueInput = row.querySelector(".value-input");
      const fieldType = row.dataset.fieldType;

      let value = valueInput.value;

      // Convert value based on field type
      if (fieldType === "boolean") {
        value = valueInput.checked;
      } else if (fieldType === "number") {
        value = parseFloat(value) || 0;
      }

      // Save or delete metadata both on the metadata_widget and signature_metadata
      if (
        value &&
        (!metadataDefaultValues[nodeType] ||
          (metadataDefaultValues[nodeType] && !Object.values(metadataDefaultValues[nodeType]).includes(value)))
      ) {
        parsed_metadata_widget[fieldName] = value;
        signature_metadata[fieldName] = value;
      } else {
        delete parsed_metadata_widget[fieldName];
        delete signature_metadata[fieldName];
      }
      metadata_widget.value = JSON.stringify(parsed_metadata_widget);
    });

    removeMetadataContainer();
  };

  cancelButton.onclick = function () {
    removeMetadataContainer();
  };

  buttonContainer.appendChild(cancelButton);
  buttonContainer.appendChild(saveButton);
  dialog.appendChild(buttonContainer);

  // Add dialog to body
  document.body.appendChild(dialog);
};

// Helper function to create a metadata field row based on field definition
const createMetadataFieldRow = (field, value) => {
  const row = document.createElement("div");
  row.className = "metadata-row";
  row.style.display = "flex";
  row.style.marginBottom = "10px";
  row.style.alignItems = "center";
  row.dataset.fieldName = field.name;
  row.dataset.fieldType = field.type;

  // Create label for the field
  const label = document.createElement("label");
  label.textContent = field.name;
  label.style.width = "120px";
  label.style.marginRight = "10px";

  // Create input based on field type
  let valueInput;

  if (field.type === "boolean") {
    valueInput = document.createElement("input");
    valueInput.type = "checkbox";
    valueInput.className = "value-input";
    valueInput.checked = value === true;
  } else if (field.type === "number") {
    valueInput = document.createElement("input");
    valueInput.type = "number";
    valueInput.className = "value-input";
    valueInput.value = value || 0;
    valueInput.style.flex = "1";
  } else {
    // Default to string input
    valueInput = document.createElement("input");
    valueInput.type = "text";
    valueInput.className = "value-input";
    valueInput.value = value || "";
    valueInput.style.flex = "1";
  }

  row.appendChild(label);
  row.appendChild(valueInput);

  return row;
};

export { editNodeMetadata, nodeTypesWithMetada };

import { editNodeMetadata, nodeTypesWithMetada } from "./helpers/metadata_editor/main.js";

// Modify initialization function
const initMetadataEditor = () => {
  // Wait for LiteGraph to be fully loaded
  if (typeof LGraphCanvas === "undefined") {
    setTimeout(initMetadataEditor, 500);
    return;
  }

  // Store original onAdded function if it exists
  const originalOnAdded = LGraphNode.prototype.onAdded;

  LGraphNode.prototype.onAdded = function () {
    if (originalOnAdded) {
      originalOnAdded.call(this);
    }

    // Add widget only to specified node types
    if (nodeTypesWithMetada.includes(this.type)) {
      this.addWidget(
        "button",
        "Edit Metadata",
        null,
        function (value, widget, node) {
          editNodeMetadata(node);
        },
        { width: 30 }
      );
    }
  };

  console.log("Metadata editor initialized");
};

// Start initialization
initMetadataEditor();

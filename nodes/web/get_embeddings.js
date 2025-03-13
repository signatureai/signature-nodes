import { app } from "../../../scripts/app.js";
import { updateInputsOutputs } from "./helpers/get_embeddings/utils.js";

app.registerExtension({
  name: "signature.GetEmbeddings",

  async nodeCreated(node) {
    if (node.comfyClass !== "signature_get_embeddings") return;

    const widgetMetadata = node.widgets.find((w) => w.name === "sig_additional_metadata");
    let metadata = {};
    if (widgetMetadata) {
      metadata = JSON.parse(widgetMetadata.value || "{}");
      node.widgets.splice(node.widgets.indexOf(widgetMetadata), 1);
    }

    for (const w of node.widgets || []) {
      if (w.name !== "model") continue;

      let widgetValue = w.value;
      updateInputsOutputs(node, widgetValue, metadata);
      let originalDescriptor = Object.getOwnPropertyDescriptor(w, "value");
      Object.defineProperty(w, "value", {
        get() {
          let valueToReturn =
            originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(w) : widgetValue;
          return valueToReturn;
        },
        set(newVal) {
          const oldVal = widgetValue;

          if (originalDescriptor && originalDescriptor.set) {
            originalDescriptor.set.call(w, newVal);
          } else {
            widgetValue = newVal;
          }

          if (oldVal !== newVal) {
            updateInputsOutputs(node, newVal, metadata);
          }
        },
      });
    }
  },
});

import { app } from "../../../scripts/app.js";
import { handleNumSlots, widgetLogic } from "./helpers/json_schema_builder/main.js";

const ext = {
  name: "signature.json_schema_builder",

  async nodeCreated(node) {
    const className = node.comfyClass;
    if (className === "signature_json_schema_builder") {
      for (const w of node.widgets || []) {
        let widgetValue = w.value;
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
              widgetLogic(node, w);
            }
          },
        });
      }

      const numSlotsWidget = node.widgets.find((w) => w.name === "num_fields");
      if (numSlotsWidget) {
        handleNumSlots(node, numSlotsWidget);
      }
    }
  },
};

app.registerExtension(ext);

import { app } from "../../../scripts/app.js";
import { handleMode, handleNumSlots, widgetLogic } from "./helpers/lora/main.js";

const ext = {
  name: "signature.lora_stacker",

  nodeCreated(node) {
    const className = node.comfyClass;
    if (className === "signature_lora_stacker") {
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

      const numSlotsWidget = node.widgets.find((w) => w.name === "num_slots");
      const modeWidget = node.widgets.find((w) => w.name === "mode");

      if (numSlotsWidget) {
        handleNumSlots(node, numSlotsWidget);
      }
      if (modeWidget) {
        handleMode(node, modeWidget);
      }
    }
  },
};

app.registerExtension(ext);

import { app } from "../../../scripts/app.js";
import {
  classNames,
  extNames,
  handleNumSlots,
  updateTypesBasedOnConnection,
  widgetLogic,
} from "./helpers/dynamic_input_amount/main.js";

extNames.forEach((name) => {
  const ext = {
    name: name,

    async beforeRegisterNodeDef(nodeType) {
      const className = nodeType.comfyClass;
      if (classNames.includes(className)) {
        // Ensure the prototype exists
        if (!nodeType.prototype) {
          nodeType.prototype = {};
        }

        nodeType.prototype.onConnectionsChange = function (index) {
          const slot = this.inputs[index];
          if (!slot) return;
          updateTypesBasedOnConnection(this);
        };
      }
    },

    async nodeCreated(node) {
      const className = node.comfyClass;
      if (classNames.includes(className)) {
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
        if (numSlotsWidget) {
          handleNumSlots(node, numSlotsWidget);
        }
      }
    },
  };
  app.registerExtension(ext);
});

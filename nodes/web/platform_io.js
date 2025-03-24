import { app } from "../../../scripts/app.js";
import { addStyling, NODES, widgetLogic } from "./helpers/platform_io/main.js";

const ext = {
  name: "signature.platform_io",

  nodeCreated(node) {
    const title = node.comfyClass;

    if (NODES.hasOwnProperty(title)) {
      // Only set initial shape, don't try to style yet
      node.shape = "box";

      node.validateLinks = function () {
        if (node.outputs !== undefined) {
          if (node.outputs[0].type !== "*" && node.outputs[0].links) {
            node.outputs[0].links
              .filter((linkId) => {
                const link = node.graph.links[linkId];
                return link && link.type !== node.outputs[0].type && link.type !== "*";
              })
              .forEach((linkId) => {
                node.graph.removeLink(linkId);
              });
          }
        }
      };

      for (const w of node.widgets || []) {
        let widgetValue = w.value;
        widgetLogic(node, w);

        // Check if the widget already has a value property descriptor
        const descriptor = Object.getOwnPropertyDescriptor(w, "value");

        // Only add our custom getter/setter if there isn't already one
        if (!descriptor || (!descriptor.get && !descriptor.set)) {
          // Store the actual value in a separate property
          w._value = widgetValue;

          try {
            Object.defineProperty(w, "value", {
              get() {
                return w._value;
              },
              set(newVal) {
                w._value = newVal;
                widgetLogic(node, w);
              },
              configurable: true, // Allow property to be redefined if needed
            });
          } catch (error) {
            console.warn("Could not define custom property for widget:", error);
            // Fallback: just set the value and run widget logic
            w.value = widgetValue;
            widgetLogic(node, w);
          }
        }
      }
      addStyling(node, title);
    }
  },
};

app.registerExtension(ext);

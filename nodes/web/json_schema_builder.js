import { app } from "../../../scripts/app.js";

function handleNumSlots(node, widget) {
  const numSlots = parseInt(widget.value);

  if (!node.widgetsHidden) {
    node.widgetsHidden = [];
  }

  for (let i = 1; i <= 10; i++) {
    const widgets = [...node.widgets, ...node.widgetsHidden].filter((w) => w.name.endsWith(`_${i}`));

    widgets.forEach((w) => {
      if (i <= numSlots) {
        const hiddenIndex = node.widgetsHidden.indexOf(w);
        const widgetIndex = node.widgets.indexOf(w);
        if (hiddenIndex !== -1 && widgetIndex === -1) {
          node.widgets.push(w);
          node.widgetsHidden.splice(hiddenIndex, 1);
        }
      } else {
        const widgetIndex = node.widgets.indexOf(w);
        if (widgetIndex !== -1) {
          node.widgetsHidden.push(w);
          node.widgets.splice(widgetIndex, 1);
        }
      }
    });
  }

  node.setSize(node.computeSize());
}

const nodeWidgetHandlers = {
  num_fields: handleNumSlots,
};

function widgetLogic(node, widget, isInitial = false) {
  const handler = nodeWidgetHandlers[widget.name];
  if (handler && !isInitial) {
    handler(node, widget);
  }
}

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

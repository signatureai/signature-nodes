const handleNumSlots = (node, widget) => {
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

  handleMode(node, undefined);
};

const handleMode = (node) => {
  const modeWidget = node.widgets.find((w) => w.name === "mode");
  if (!modeWidget) return;

  if (!node.widgetsHiddenModes) {
    node.widgetsHiddenModes = [];
  }

  const isSimple = modeWidget.value === "Simple";
  const allWidgets = [...node.widgets, ...node.widgetsHiddenModes];

  allWidgets.forEach((w) => {
    const isWeightWidget = w.name.startsWith("weight_");
    const isAdvancedWidget = w.name.startsWith("model_weight_") || w.name.startsWith("clip_weight_");

    if (isSimple) {
      if (isWeightWidget) {
        const slotNum = w.name.replace("weight_", "");
        const loraNameWidget = node.widgets.findIndex((widget) => widget.name === `lora_name_${slotNum}`);

        if (loraNameWidget !== -1) {
          const hiddenIndex = node.widgetsHiddenModes.indexOf(w);
          const widgetIndex = node.widgets.indexOf(w);
          if (hiddenIndex !== -1 && widgetIndex === -1) {
            node.widgets.splice(loraNameWidget + 1, 0, w);
            node.widgetsHiddenModes.splice(hiddenIndex, 1);
          }
        }
      }
      if (isAdvancedWidget) {
        const widgetIndex = node.widgets.indexOf(w);
        if (widgetIndex !== -1) {
          node.widgetsHiddenModes.push(w);
          node.widgets.splice(widgetIndex, 1);
        }
      }
    } else {
      if (isWeightWidget) {
        const widgetIndex = node.widgets.indexOf(w);
        if (widgetIndex !== -1) {
          node.widgetsHiddenModes.push(w);
          node.widgets.splice(widgetIndex, 1);
        }
      }
      if (isAdvancedWidget) {
        const slotNum = w.name.replace("model_weight_", "").replace("clip_weight_", "");
        const loraNameWidget = node.widgets.findIndex((widget) => widget.name === `lora_name_${slotNum}`);

        if (loraNameWidget !== -1) {
          const hiddenIndex = node.widgetsHiddenModes.indexOf(w);
          const widgetIndex = node.widgets.indexOf(w);
          if (hiddenIndex !== -1 && widgetIndex === -1) {
            node.widgets.splice(loraNameWidget + 1, 0, w);
            node.widgetsHiddenModes.splice(hiddenIndex, 1);
          }
        }
      }
    }
  });

  node.setSize(node.computeSize());
};

const nodeWidgetHandlers = {
  num_slots: handleNumSlots,
  mode: handleMode,
};

const widgetLogic = (node, widget, isInitial = false) => {
  const handler = nodeWidgetHandlers[widget.name];
  if (handler && !isInitial) {
    handler(node, widget);
  }
};

export { handleMode, handleNumSlots, widgetLogic };

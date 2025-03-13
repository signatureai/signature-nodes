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

  node.setSize(node.computeSize());
};

const nodeWidgetHandlers = {
  num_fields: handleNumSlots,
};

const widgetLogic = (node, widget, isInitial = false) => {
  const handler = nodeWidgetHandlers[widget.name];
  if (handler && !isInitial) {
    handler(node, widget);
  }
};

export { handleNumSlots, widgetLogic };

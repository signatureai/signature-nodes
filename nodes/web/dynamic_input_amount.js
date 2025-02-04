import { app } from "../../../scripts/app.js";

const extNames = ["signature.batch_builder", "signature.list_builder", "signature.math_operator"]

const classNames = ["signature_list_builder", "signature_batch_builder", "signature_math_operator"]

function updateTypesBasedOnConnection(node) {
  // Find if there's at least one connected input among visible and hidden inputs
  const allInputs = [...node.inputs, ...(node.inputsHidden || [])];
  const connectedInput = allInputs.find((input) => input.link);

  let typeToUse = "*";
  if (connectedInput) {
    // Get the connected node's output type
    typeToUse = app.graph.getNodeById(app.graph.links[connectedInput.link].origin_id)
      .outputs[app.graph.links[connectedInput.link].origin_slot].type;
  }

  // Update all inputs (visible and hidden) with the same type and name
  allInputs.forEach((input) => {
    input.type = typeToUse;
  });

  const allOutputs = [...node.outputs, ...(node.outputsHidden || [])];
  allOutputs[0].type = typeToUse;
  allOutputs[0].name = typeToUse === "*" ? "ANY" : typeToUse;
  allOutputs[0].localized_name = typeToUse === "*" ? "ANY" : typeToUse;
}

function handleNumSlots(node, widget) {
  const numSlots = parseInt(widget.value);

  if (!node.inputsHidden) {
    node.inputsHidden = [];
  }

  for (let i = 1; i <= 10; i++) {
    // Find inputs with either numeric suffix (_1, _2...) or alphabetic name (a, b...)
    const inputs = [...node.inputs, ...node.inputsHidden].filter((input) =>
      input.name.endsWith(`_${i}`) || 
      input.name === String.fromCharCode(96 + i)  // a = 97, b = 98, etc.
    );

    // Group inputs by their base name (removing the _N suffix for numeric ones)
    const inputsByName = {};
    inputs.forEach((input) => {
      // For alphabetic inputs (a, b, c...), use the full name as base name
      // For numeric suffix inputs (test_1, test_2...), remove the suffix
      const baseName = input.name.match(/^[a-z]$/) ? 
        input.name : 
        input.name.replace(/_\d+$/, "");

      if (!inputsByName[baseName]) {
        inputsByName[baseName] = [];
      }
      inputsByName[baseName].push(input);
    });

    // Process each group of inputs separately
    Object.values(inputsByName).forEach((sameNameInputs) => {
      if (sameNameInputs.length === 0) return;
  
      const input = sameNameInputs[0];
  
      if (i <= numSlots) {
        // Move to visible inputs if not already there
        const hiddenIndex = node.inputsHidden.indexOf(input);
        const inputIndex = node.inputs.indexOf(input);
        if (hiddenIndex !== -1 && inputIndex === -1) {
          // Find the index of the "value" input
          const valueInputIndex = node.inputs.findIndex(input => input.name === "value");
          // Insert before "value" input if it exists, otherwise append to end
          const insertIndex = valueInputIndex !== -1 ? valueInputIndex : node.inputs.length;
          node.inputs.splice(insertIndex, 0, input);
          node.inputsHidden.splice(hiddenIndex, 1);
        }
      } else {
        // Move to hidden inputs if not already there
        const inputIndex = node.inputs.indexOf(input);
        if (inputIndex !== -1) {
          node.inputsHidden.push(input);
          node.inputs.splice(inputIndex, 1);
        }
      }

      // Remove any duplicate inputs with the same base name
      const duplicates = sameNameInputs.slice(1);
      duplicates.forEach((duplicate) => {
        const hiddenIndex = node.inputsHidden.indexOf(duplicate);
        const inputIndex = node.inputs.indexOf(duplicate);
        if (hiddenIndex !== -1) node.inputsHidden.splice(hiddenIndex, 1);
        if (inputIndex !== -1) node.inputs.splice(inputIndex, 1);
      });
    });
  }

  node.setSize(node.computeSize());
}

const nodeWidgetHandlers = {
  num_slots: handleNumSlots,
};

function widgetLogic(node, widget, isInitial = false) {
  const handler = nodeWidgetHandlers[widget.name];
  if (handler && !isInitial) {
    handler(node, widget);
  }
}

extNames.forEach((name) => {
  const ext = {
    name: name,
  
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
      const className = nodeType.comfyClass;
      if (classNames.includes(className)) {
        // Ensure the prototype exists
        if (!nodeType.prototype) {
          nodeType.prototype = {};
        }
  
        nodeType.prototype.onConnectionsChange = function (
          type,
          index,
          connected,
          link_info,
        ) {
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
                originalDescriptor && originalDescriptor.get
                  ? originalDescriptor.get.call(w)
                  : widgetValue;
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
})

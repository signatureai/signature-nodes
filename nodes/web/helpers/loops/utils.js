import { app } from "../../../../scripts/app.js";

const excludeLoops = [
  "signature_do_while_loop_start",
  "signature_do_while_loop_end",
  "signature_for_loop_start",
  "signature_for_loop_end",
];

const updateInputsOutputs = (node, numSlots, startIndex) => {
  node.inputsHidden ||= [];
  node.outputsHidden ||= [];

  for (let i = startIndex; i < 10; i++) {
    if (i < numSlots + startIndex) {
      // Move to visible inputs if not already there
      const hiddenInputindex = node.inputsHidden.findIndex((input) => input.name === `init_value_${i}`);
      const inputIndex = node.inputs.findIndex((input) => input.name === `init_value_${i}`);
      if (hiddenInputindex !== -1 && inputIndex === -1) {
        const numSlotInputIndex = node.inputs.findIndex(
          (input) => input.name === "num_slot" || input.name === "end_loop" || input.name === "iterations"
        );
        // Insert before "num_slot" or "end_loop" input if it exists, otherwise append to end
        const insertIndex = numSlotInputIndex !== -1 ? numSlotInputIndex : node.inputs.length;
        node.inputs.splice(insertIndex, 0, node.inputsHidden[hiddenInputindex]);
        node.inputsHidden.splice(hiddenInputindex, 1);
      }
    } else {
      // Move to hidden inputs if not already there
      const inputIndex = node.inputs.findIndex((input) => input.name === `init_value_${i}`);
      if (inputIndex !== -1) {
        const input = node.inputs[inputIndex];
        // Disconnect the input if it has a link
        if (input.link) {
          const link = app.graph.links[input.link];
          if (link) {
            node.disconnectInput(inputIndex);
          }
        }
        node.inputsHidden.push(input);
        node.inputs.splice(inputIndex, 1);
      }
    }
  }

  node.outputsHidden = [];
  for (let i = startIndex; i < 10; i++) {
    if (i >= numSlots + 1) {
      node.outputsHidden.push(`value_${i}`);
    }
  }

  node.setSize(node.computeSize());
};

export { excludeLoops, updateInputsOutputs };

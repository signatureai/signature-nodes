import { app } from "../../../scripts/app.js";

const NODE_COLORS = { nodeColor: "#2a363b", nodeBgColor: "#3f5159" };

function updateInputsOutputs(node, numSlots, startIndex) {
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
}

app.registerExtension({
  name: "signature.DoWhileLoopStart",

  async nodeCreated(node) {
    if (
      node.comfyClass !== "signature_do_while_loop_start" &&
      node.comfyClass !== "signature_do_while_loop_end" &&
      node.comfyClass !== "signature_for_loop_start" &&
      node.comfyClass !== "signature_for_loop_end"
    )
      return;

    node.shape = "box";
    node.color = NODE_COLORS.nodeColor;
    node.bgcolor = NODE_COLORS.nodeBgColor;

    let startIndex = 0;
    if (node.comfyClass === "signature_for_loop_start" || node.comfyClass === "signature_for_loop_end") {
      startIndex = 1;
    }

    const widgetNumSlots = node.widgets.find((w) => w.name === "num_slots");
    let widgetValue = widgetNumSlots.value;
    updateInputsOutputs(node, parseInt(widgetValue), startIndex);
    let originalDescriptor = Object.getOwnPropertyDescriptor(widgetNumSlots, "value");
    Object.defineProperty(widgetNumSlots, "value", {
      get() {
        let valueToReturn =
          originalDescriptor && originalDescriptor.get ? originalDescriptor.get.call(widgetNumSlots) : widgetValue;
        return valueToReturn;
      },
      set(newVal) {
        const oldVal = widgetValue;

        if (originalDescriptor && originalDescriptor.set) {
          originalDescriptor.set.call(widgetNumSlots, newVal);
        } else {
          widgetValue = newVal;
        }

        if (oldVal !== newVal) {
          updateInputsOutputs(node, parseInt(newVal), startIndex);
        }
      },
    });

    const originalDrawForeground = node.onDrawForeground;
    node.onDrawForeground = function (ctx) {
      originalDrawForeground?.apply?.(this, arguments);

      for (const outputName of node.outputsHidden) {
        const slotOutput = node.findOutputSlot(outputName);
        if (slotOutput < 0) continue;
        const pos = node.getConnectionPos(false, slotOutput);

        pos[0] -= node.pos[0] - 10;
        pos[1] -= node.pos[1];

        ctx.beginPath();
        ctx.strokeStyle = "red";
        ctx.lineWidth = 4;
        ctx.moveTo(pos[0] - 5, pos[1] - 5);
        ctx.lineTo(pos[0] + 5, pos[1] + 5);
        ctx.moveTo(pos[0] + 5, pos[1] - 5);
        ctx.lineTo(pos[0] - 5, pos[1] + 5);
        ctx.stroke();
      }
    };
  },
});

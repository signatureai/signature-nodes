import { app } from "../../../scripts/app.js";

const tasksWithTextPrompt = [
  "CAPTION_TO_PHRASE_GROUNDING",
  "REFERRING_EXPRESSION_SEGMENTATION",
  "OPEN_VOCABULARY_DETECTION",
  "REGION_TO_SEGMENTATION",
  "REGION_TO_CATEGORY",
  "REGION_TO_DESCRIPTION",
];

function updateInputsOutputs(node, newVal) {
  console.log(node);
  console.log("updateInputsOutputs", newVal);
  if (tasksWithTextPrompt.includes(newVal)) {
    const slotIndexInputText = node.findInputSlot("text_prompt");
    const widgetText = node.widgets.find((w) => w.name === "text_prompt");
    if (slotIndexInputText < 0 && !widgetText) {
      // TODO: Add multine widget here
      node.addWidget("STRING", "text_prompt", "", "text_prompt", {
        multiline: true,
      });
    }
  } else {
    const slotIndexInputText = node.findInputSlot("text_prompt");
    if (slotIndexInputText >= 0) {
      node.removeInput(slotIndexInputText);
    }
    const widgetText = node.widgets.find((w) => w.name === "text_prompt");
    if (widgetText) {
      node.widgets.splice(node.widgets.indexOf(widgetText), 1);
    }
  }
}

app.registerExtension({
  name: "signature.Florence",

  async nodeCreated(node) {
    if (node.comfyClass !== "signature_florence") return;
    for (const w of node.widgets || []) {
      if (w.name !== "task_token") continue;

      let widgetValue = w.value;
      updateInputsOutputs(node, widgetValue);
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
            updateInputsOutputs(node, newVal);
          }
        },
      });
    }
  },
});

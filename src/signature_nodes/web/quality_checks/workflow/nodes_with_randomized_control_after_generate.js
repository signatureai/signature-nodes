import { highlightNodes } from "../../helpers/global/main.js";
import { showWarningDialog } from "./warning_dialogue.js";

const findNodesWithRandomizedControlAfterGenerateWidget = async () => {
  const nodes = app.graph._nodes;

  const nodesWithRandomizedControlAfterGenerateWidget = nodes.filter(
    (node) =>
      (node.mode !== 4 &&
        node.widgets &&
        node.widgets.some((widget) => widget.name === "control_after_generate" && widget.type === "combo")) ||
      (node.mode !== 4 &&
        node.inputs &&
        node.inputs.some((input) => input.name.includes("seed") && input.link === null))
  );
  // Highlight the nodes with red borders
  let removeHighlights = null;
  if (nodesWithRandomizedControlAfterGenerateWidget.length > 0) {
    removeHighlights = highlightNodes(nodesWithRandomizedControlAfterGenerateWidget);

    // If there are nodes with randomized widgets, show a warning dialog
    const result = await showWarningDialog(nodesWithRandomizedControlAfterGenerateWidget, {
      dialogueTitle: "⚠️ Randomization Warning",
      dialogueMessage1:
        "Your workflow contains nodes with <strong>randomized values</strong> that won't work as expected after submission (highlighted with <span style='color: #ff0000;'>red borders</span>):",
      dialogueMessage2:
        "When this workflow is submitted, these randomized values will be <strong>fixed</strong> to their current values and won't randomize for users.",
      dialogueMessage3:
        "For true randomization in submitted workflows, we recommend using the <strong>Signature Random Number</strong> node connected to your seed inputs.",
    });

    // Remove the highlights after the dialog is closed
    if (removeHighlights) {
      removeHighlights();
    }

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }
  return nodesWithRandomizedControlAfterGenerateWidget;
};

export { findNodesWithRandomizedControlAfterGenerateWidget };

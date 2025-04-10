import { blacklistedNodes } from "../../helpers/workflow/form/utils.js";
import { showWarningDialog } from "./warning_dialogue.js";

const checkBlacklistNodes = async (workflow) => {
  if (!workflow) {
    console.log("No workflow provided");
    const result = await showWarningDialog([], {
      dialogueTitle: "⚠️ Workflow Error",
      dialogueMessage1: "Workflow with active nodes is required",
    });

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }

  const workflow_nodes = workflow.nodes;
  const blacklistedNodesFound = [];

  // Check each node in the workflow against the blacklist
  workflow_nodes.forEach((node) => {
    if (blacklistedNodes[node.type]) {
      blacklistedNodesFound.push({
        node,
        replacement: blacklistedNodes[node.type],
      });
    }
  });

  // If blacklisted nodes are found, show warning dialog
  if (blacklistedNodesFound.length > 0) {
    const result = await showWarningDialog(
      blacklistedNodesFound.map((item) => item.node),
      {
        dialogueTitle: "⚠️ Blacklisted Nodes Found",
        dialogueMessage1: "Your workflow contains nodes that are blacklisted:",
        dialogueMessage2: blacklistedNodesFound
          .map((item) => `- "${item.node.type}" should be replaced with "${item.replacement}"`)
          .join("\n"),
        dialogueMessage3: "Please replace these nodes with their recommended alternatives before proceeding.",
      },
      false
    );

    if (!result.continue) {
      return { cancelled: true };
    }
  }

  return { cancelled: false };
};

export { checkBlacklistNodes };

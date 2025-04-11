import { showWarningDialog } from "./warning_dialogue.js";

const bypassNodes = async (workflow, nodes_to_bypass) => {
  if (!workflow) {
    const result = await showWarningDialog([], {
      dialogueTitle: "⚠️ Workflow Error",
      dialogueMessage1: "Workflow with active nodes is required",
    });

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }

  const workflow_nodes = workflow.nodes;

  const workflow_desired_nodes = workflow_nodes.map((node) => {
    if (nodes_to_bypass.includes(node.type)) {
      // Change mode to 4 since it's the mode that sets the node as bypassed
      return { ...node, mode: 4 };
    }
    return node;
  });

  return {
    workflow: { ...workflow, nodes: workflow_desired_nodes },
  };
};

export { bypassNodes };

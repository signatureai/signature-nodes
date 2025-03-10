import { showWarningDialog } from "../main.js";

const checkNodeGroupPresence = async (workflow_api, workflow, nodes_to_check) => {
  if (!workflow_api) {
    const result = await showWarningDialog([], {
      dialogueTitle: "⚠️ Workflow Error",
      dialogueMessage1: "Workflow with avaliable nodes is required",
    });

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }
  const workflow_api_nodes = Object.values(workflow_api);

  const workflowApiHasActiveInputNodes = workflow_api_nodes.some((node) => nodes_to_check.includes(node.class_type));

  const workflow_nodes = workflow.nodes;

  const workflow_desired_nodes = workflow_nodes.filter((node) => nodes_to_check.includes(node.type));

  if (!workflowApiHasActiveInputNodes && workflow_desired_nodes.length) {
    await showWarningDialog(
      workflow_desired_nodes,
      {
        dialogueTitle: "⚠️ Workflow Error",
        dialogueMessage1: `Workflow must have at least one active node of the following types: ${nodes_to_check.join(
          ", "
        )}, but it has ${workflow_desired_nodes.length} inactive ${
          workflow_desired_nodes.length > 1 ? "nodes" : "node"
        }:`,
      },
      false
    );

    return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
  }

  if (!workflowApiHasActiveInputNodes) {
    await showWarningDialog(
      [],
      {
        dialogueTitle: "⚠️ Workflow Error",
        dialogueMessage1: `Workflow must have at least one active node of the following types: ${nodes_to_check.join(
          ", "
        )}`,
      },
      false
    );
    return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
  }

  return { cancelled: false };
};

export { checkNodeGroupPresence };

import { showWarningDialog } from "./warning_dialogue.js";

const checkUnlinkedNodes = async (workflow) => {
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

  // Find completely disconnected nodes (no inputs and no outputs linked)
  const disconnectedNodes = workflow_nodes.filter((node) => {
    // Check if node has any linked inputs
    const hasLinkedInputs = node.inputs && node.inputs.some((input) => input.link !== null);

    // Check if node has any linked outputs
    const hasLinkedOutputs =
      node.outputs &&
      node.outputs.some((output) => output.links && Array.isArray(output.links) && output.links.length > 0);

    // A node is disconnected if it has no linked inputs and no linked outputs
    return !hasLinkedInputs && !hasLinkedOutputs;
  });

  if (disconnectedNodes.length > 0) {
    const nodeIds = disconnectedNodes.map((node) => node.id).join(", ");
    const result = await showWarningDialog([], {
      dialogueTitle: "⚠️ Workflow Error",
      dialogueMessage1: `Your workflow contains <strong>disconnected nodes</strong>:`,
      dialogueMessage2: `These nodes (IDs: ${nodeIds}) have no connections to other nodes and should be either connected or removed from the workflow.`,
      dialogueMessage3: `<span style="color: #ff0000; font-weight: bold;">WARNING:</span> Continuing will <strong>permanently remove</strong> these nodes from the workflow.`,
    });

    if (!result.continue) {
      return { cancelled: true }; // Return an object with cancelled flag to signal cancellation
    }
  }

  // Return the workflow with the disconnected nodes removed
  if (disconnectedNodes.length > 0) {
    // Create a new workflow object with the disconnected nodes removed
    const filteredNodes = workflow_nodes.filter(
      (node) => !disconnectedNodes.some((disconnectedNode) => disconnectedNode.id === node.id)
    );

    return {
      workflow: {
        ...workflow,
        nodes: filteredNodes,
      },
      cancelled: false,
    };
  }

  return { workflow, cancelled: false };
};

export { checkUnlinkedNodes };

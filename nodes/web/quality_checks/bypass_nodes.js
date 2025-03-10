const bypassNodes = async (workflow, nodes_to_bypass) => {
  if (!workflow) {
    throw new Error("Workflow with nodes is required");
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

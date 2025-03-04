const checkNodeGroupPresence = async (workflow_api, workflow, nodes_to_check) => {
  if (!workflow_api) {
    throw new Error("Workflow with avaliable nodes is required");
  }

  const workflow_api_nodes = Object.values(workflow_api);

  const workflowApiHasActiveInputNodes = workflow_api_nodes.some((node) => nodes_to_check.includes(node.class_type));

  const workflow_nodes = workflow.nodes;

  const workflow_desired_nodes = workflow_nodes.filter((node) => nodes_to_check.includes(node.type));

  if (!workflowApiHasActiveInputNodes && workflow_desired_nodes.length) {
    const listOfDesiredNodes = workflow_desired_nodes.map((node) => `Type: ${node.type} (title: ${node.title})`);
    throw new Error(
      `Workflow must have at least one active node of the following types: ${nodes_to_check.join(", ")}, but it has ${
        workflow_desired_nodes.length
      } inactive ${workflow_desired_nodes.length > 1 ? "nodes" : "node"}: ${listOfDesiredNodes.join(", ")}`
    );
  }

  if (!workflowApiHasActiveInputNodes) {
    throw new Error(`Workflow must have at least one active node of the following types: ${nodes_to_check.join(", ")}`);
  }

  return true;
};

export { checkNodeGroupPresence };

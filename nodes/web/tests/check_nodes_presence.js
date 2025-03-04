const checkNodesPresence = async (workflow_api, workflow, nodes_to_check = []) => {
  if (!workflow_api) {
    throw new Error("Workflow with avaliable nodes is required");
  }

  nodes_to_check.forEach((node_name) => {
    const workflow_api_nodes = Object.values(workflow_api);

    const workflowApiHasActiveInputNodes = workflow_api_nodes.some((node) => node.class_type.includes(node_name));

    const workflow_nodes = workflow.nodes;

    const workflow_input_nodes = workflow_nodes.filter((node) => node.type.includes(node_name));

    if (!workflowApiHasActiveInputNodes && workflow_input_nodes.length) {
      const listOfDesiredNodes = workflow_input_nodes.map((node) => `Title:${node.title} type:${node.type}`);
      throw new Error(
        `Workflow must have at least one active ${node_name} node, but it has ${
          workflow_input_nodes.length
        } inactive ${node_name} ${workflow_input_nodes.length > 1 ? "nodes" : "node"}: ${listOfDesiredNodes}`
      );
    }

    if (!workflowApiHasActiveInputNodes) {
      throw new Error(`Workflow must have at least one active ${node_name} node`);
    }
  });
  return true;
};

export { checkNodesPresence };

import { showWarningDialog } from "./warning_dialogue.js";

const blacklistedNodes = {
  "ImageListToBatch+": ["signature_image_list_batch"],
  "ImageBatchToList+": ["signature_image_batch_list"],
  InvertMask: ["signature_mask_invert"],
  ImageScaleToTotalPixels: ["signature_resize_with_megapixels"],
  ImageResizeKJ: ["signature_resize"],
  GrowMaskWithBlur: ["signature_mask_grow_with_blur"],
  "SimpleMath+": ["signature_math_operator"],
};

// Function to handle node styling based on highlight state
const updateNodeStyle = (node, isHighlighted) => {
  if (isHighlighted) {
    // Store original styling if not already stored
    if (!node._originalStyle) {
      node._originalStyle = {
        color: node.color,
        bgcolor: node.bgcolor,
        shape: node.shape,
      };
    }

    // Apply highlight styling
    Object.assign(node, {
      color: "#00ff00",
      bgcolor: "#224422",
      shape: "box",
    });

    // Add custom draw method to add glow
    node.onDrawBackground = function (ctx) {
      if (this.flags.collapsed) {
        return;
      }

      ctx.shadowColor = "#00ff00";
      ctx.shadowBlur = 15;
      ctx.strokeStyle = "#00ff00";
      ctx.lineWidth = 2;
      ctx.strokeRect(0, 0, this.size[0], this.size[1]);
      ctx.shadowBlur = 0;
    };
  } else {
    // Restore original style or apply signature style
    Object.assign(node, {
      color: "#36213E",
      bgcolor: "#221324",
      shape: "box",
    });

    // Remove custom draw method
    node.onDrawBackground = null;
  }

  // Force a redraw
  if (app.graph) {
    console.log("Forcing canvas redraw");
    app.graph.setDirtyCanvas(true, true);
  }
};

// Function to spawn replacement nodes near blacklisted nodes
const spawnReplacementNodes = (blacklistedNodesFound) => {
  blacklistedNodesFound.forEach((item) => {
    const node = item.node;
    const replacement = item.replacement[0]; // Get first replacement from array

    // Create the replacement node
    const newNode = LiteGraph.createNode(replacement);
    if (!newNode) {
      console.error(`Failed to create node of type: ${replacement}`);
      return;
    }

    // Add the node to the graph
    app.graph.add(newNode);

    // Position the new node to the right of the blacklisted node
    newNode.pos = [
      node.pos[0] + node.size[0] + 50, // 50 pixels to the right
      node.pos[1], // Same vertical position
    ];

    // Set initial highlight state
    newNode.isHighlighted = true;

    // Create a function to switch to signature styling
    const applySignatureStyling = () => {
      if (newNode.isHighlighted) {
        // Only apply if still highlighted
        newNode.isHighlighted = false;
        updateNodeStyle(newNode, false);

        // Remove our event handlers
        if (newNode.graph && newNode.graph.canvas) {
          newNode.graph.canvas.off("nodeMoved", applySignatureStyling);
        }
        newNode.onConnectionsChange = null;
        newNode.onMouseDown = null;
      }
    };

    // Add event handlers
    if (newNode.graph && newNode.graph.canvas) {
      newNode.graph.canvas.on("nodeMoved", applySignatureStyling);
    }
    newNode.onConnectionsChange = applySignatureStyling;
    newNode.onMouseDown = applySignatureStyling;

    // Apply initial highlight after a short delay to ensure node is fully initialized
    setTimeout(() => {
      updateNodeStyle(newNode, true);
    }, 50);

    // Select the new node
    app.canvas.selectNode(newNode, false);
  });

  // Return the updated workflow
  return app.graph.serialize();
};

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
          .map((item) => `- "${item.node.type}" should be replaced with "${item.replacement[0]}"`)
          .join("\n"),
        dialogueMessage3: "Please replace these nodes with their recommended alternatives before proceeding.",
      },
      false,
      true // Enable the spawn replacement nodes button
    );

    if (result.spawnReplacementNodes) {
      const updatedWorkflow = spawnReplacementNodes(blacklistedNodesFound);
      return { cancelled: true, workflow: updatedWorkflow };
    }

    if (!result.continue) {
      return { cancelled: true };
    }
  }

  return { cancelled: false, workflow: workflow };
};

export { checkBlacklistNodes };

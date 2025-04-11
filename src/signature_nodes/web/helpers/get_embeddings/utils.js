const updateInputsOutputs = (node, newVal, additionalMetadata) => {
  if (additionalMetadata[newVal].showText) {
    const slotIndexInputText = node.findInputSlot("text");
    const widgetText = node.widgets.find((w) => w.name === "text");
    if (slotIndexInputText < 0 && !widgetText) {
      node.addWidget("STRING", "text", "", "text");
    }

    const slotIndexOutputTextEmbeddings = node.findOutputSlot("text_embeddings");
    if (slotIndexOutputTextEmbeddings < 0) {
      node.addOutput("text_embeddings", "LIST");
    }
  } else {
    const slotIndexInputText = node.findInputSlot("text");
    if (slotIndexInputText >= 0) {
      node.removeInput(slotIndexInputText);
    }
    const widgetText = node.widgets.find((w) => w.name === "text");
    if (widgetText) {
      node.widgets.splice(node.widgets.indexOf(widgetText), 1);
    }

    const slotIndexOutputTextEmbeddings = node.findOutputSlot("text_embeddings");
    if (slotIndexOutputTextEmbeddings >= 0) {
      node.removeOutput(slotIndexOutputTextEmbeddings);
    }
  }

  if (additionalMetadata[newVal].showImage) {
    const slotIndexInputImage = node.findInputSlot("image");
    if (slotIndexInputImage < 0) {
      node.addInput("image", "IMAGE");
    }

    const slotIndexOutputImageEmbeddings = node.findOutputSlot("image_embeddings");
    if (slotIndexOutputImageEmbeddings < 0) {
      node.addOutput("image_embeddings", "LIST");

      // If there is already a text_embedding output we need to re-create it in the second slot with all its links
      // I found no other (easier) way to keep any working link between the output and a target node
      const existingTextOutput = node.outputs.find((o) => o.name === "text_embeddings");
      if (existingTextOutput) {
        let storedLinks = [];
        if (existingTextOutput.links) {
          storedLinks = existingTextOutput.links.map((l) => node.graph.links[l]);
        }
        const slotIndex = node.findOutputSlot("text_embeddings");
        node.removeOutput(slotIndex);
        node.addOutput("text_embeddings", "LIST");
        const newOutput = node.findOutputSlot("text_embeddings");
        for (const link of storedLinks) {
          const targetNode = node.graph.nodes.find((n) => n.id === link.target_id);
          if (targetNode) {
            node.connect(newOutput, targetNode, link.target_slot);
          }
        }
      }
    }
  } else {
    const slotIndexInputImage = node.findInputSlot("image");
    if (slotIndexInputImage >= 0) {
      node.removeInput(slotIndexInputImage);
    }

    const slotIndexOutputImageEmbeddings = node.findOutputSlot("image_embeddings");
    if (slotIndexOutputImageEmbeddings >= 0) {
      node.removeOutput(slotIndexOutputImageEmbeddings);
    }
  }
};

export { updateInputsOutputs };

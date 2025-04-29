import {
  bypassNodes,
  checkBlacklistNodes,
  checkNodeGroupPresence,
  checkUnlinkedNodes,
  findNodesWithRandomizedControlAfterGenerateWidget,
} from "../../../quality_checks/main.js";
import { getManifest, getWorkflowById } from "../../../signature_api/main.js";
import { getLoadingSpinner, showMessage } from "../utils.js";
import { showForm } from "./style.js";

const populateSubmitForm = async (workflowId) => {
  const workflow = await getWorkflowById(workflowId);

  // Populate form fields with workflow data
  if (workflow) {
    const formContainer = document.getElementById("signature-workflow-submission-form");
    const nameInput = formContainer.querySelector('input[type="text"]');
    const descriptionInput = formContainer.querySelector("textarea");
    const typeSelect = formContainer.querySelector("select");
    const preview = document.getElementById("image-preview");
    const fileInput = formContainer.querySelector('input[type="file"]');

    // Update text fields and select
    if (nameInput && workflow.name) nameInput.value = workflow.name;
    if (descriptionInput && workflow.description) descriptionInput.value = workflow.description;
    if (typeSelect && workflow.type) {
      const type = workflow.type.toLowerCase();
      if (Array.from(typeSelect.options).some((opt) => opt.value === type)) {
        typeSelect.value = type;
      }
    }
    if (workflow.coverImageUrl) {
      preview.src = workflow.coverImageUrl;
      preview.style.display = "block";
      fileInput.value = "";
    }
  }
};

const getApiFromUpdatedWorkflow = async (workflowData) => {
  // Save current graph state
  const currentGraph = app.graph.serialize();

  try {
    // Clear the current graph
    app.graph.clear();

    // Instead of using app.loadGraphData, use LiteGraph's configure method directly
    // This loads the graph data without triggering UI-related actions like tab creation
    app.graph.configure(workflowData);

    // Generate API representation
    const graph_api = await app.graphToPrompt();

    return graph_api["output"];
  } catch (error) {
    console.error("Error generating API from workflow:", error);
    return null;
  }
};

const validateWorkflow = async (app) => {
  try {
    const initial_workflow = app.graph.serialize();

    const input_nodes_types = ["signature_input_image", "signature_input_text"];
    const output_nodes_types = ["signature_output"];
    const nodes_to_bypass = ["PreviewImage", "LoadImage", "signature_mask_preview", "signature_text_preview"];

    // Check for unlinked nodes first
    const { workflow: workflow_with_unlinked_nodes_removed, cancelled: check_unlinked_nodes_cancelled } =
      await checkUnlinkedNodes(initial_workflow);
    if (check_unlinked_nodes_cancelled) {
      return { cancelled: true };
    }

    // Then check for blacklisted nodes
    const { cancelled: blacklist_check_cancelled, workflow: workflow_after_blacklist_check } =
      await checkBlacklistNodes(workflow_with_unlinked_nodes_removed);
    if (blacklist_check_cancelled) {
      return { cancelled: true };
    }

    const nodesWithControlWidget = await findNodesWithRandomizedControlAfterGenerateWidget();
    if (nodesWithControlWidget.cancelled) {
      return { cancelled: true };
    }

    // Bypass the nodes of the list above and generate a new workflow
    const { workflow } = await bypassNodes(workflow_after_blacklist_check, nodes_to_bypass);
    // Change the displayed graph to the one generated above and create a new workflow api
    const workflow_api = await getApiFromUpdatedWorkflow(workflow);

    // Check if the workflow has the required nodes
    const input_nodes_presence = await checkNodeGroupPresence(workflow_api, workflow, input_nodes_types);

    if (input_nodes_presence.cancelled) {
      return { cancelled: true };
    }

    const output_nodes_presence = await checkNodeGroupPresence(workflow_api, workflow, output_nodes_types);

    if (output_nodes_presence.cancelled) {
      return { cancelled: true };
    }

    return { cancelled: false, workflow: workflow, workflow_api: workflow_api };
  } catch (error) {
    console.error("Error in validateWorkflow:", error);
    showMessage("An error occurred while validating the workflow", "#ff0000");
  }
};

const uploadModelToS3 = async (modelName, modelData) => {
  try {
    const formData = new FormData();
    // Send the path and checksum, not the file blob
    formData.append("model_path", modelData.path);
    formData.append("checksum", modelData.checksum);
    formData.append("filename", modelName); // Also send the original filename
    formData.append("type", "model"); // Keep type if needed by backend logic

    console.log(`Uploading model: ${modelName} from path: ${modelData.path} with checksum: ${modelData.checksum}`);

    const response = await fetch("/upload/s3-model", {
      method: "POST",
      body: formData, // Sending as form data
    });

    // Check if the response indicates an error
    if (!response.ok) {
      // Specifically handle the 409 Conflict for name mismatch
      if (response.status === 409) {
        try {
          const errorResult = await response.json(); // Parse the detailed error from backend
          return errorResult; // Return the structured error object
        } catch (parseError) {
          // Fallback if JSON parsing fails
          const errorText = await response.text(); // Read text as fallback
          throw new Error(`Failed to upload model ${modelName}: ${response.status} - ${errorText}`);
        }
      } else {
        // Handle other non-OK responses
        const errorText = await response.text();
        throw new Error(`Failed to upload model ${modelName}: ${errorText}`); // Throw generic error
      }
    }

    // If response is OK, parse the success/exists JSON
    const result = await response.json();
    console.log(`Upload check successful for ${modelName}:`, result);
    return result;
  } catch (error) {
    // Catch network errors or errors thrown above
    console.error(`Error processing model ${modelName} for S3:`, error);
    // Ensure the error propagated retains useful info if possible, otherwise re-throw
    throw error;
  }
};

const uploadModelsToS3 = async (models) => {
  const uploadResults = [];
  for (const [modelName, modelData] of Object.entries(models)) {
    try {
      const result = await uploadModelToS3(modelName, modelData);
      // Backend now returns different statuses
      if (result.status === "success") {
        uploadResults.push({ modelName, success: true, status: "uploaded", result });
      } else if (result.status === "exists") {
        uploadResults.push({ modelName, success: true, status: "exists", result });
      } else if (result.status === "error" && result.error_type === "name_mismatch") {
        uploadResults.push({ modelName, success: false, status: "name_mismatch", error: result });
      } else {
        // Handle unexpected backend responses
        uploadResults.push({ modelName, success: false, status: "unknown_error", error: result });
      }
    } catch (error) {
      // Catch fetch errors or errors thrown by uploadModelToS3
      uploadResults.push({ modelName, success: false, status: "fetch_error", error });
    }
  }
  return uploadResults; // Return detailed results
};

const saveWorkflow = async (app) => {
  try {
    const { cancelled, workflow, workflow_api } = await validateWorkflow(app);

    if (cancelled) {
      return;
    }

    const form = await showForm();
    const submitButton = form.querySelector('a[href="#"]');

    submitButton.onclick = async (e) => {
      try {
        e.preventDefault();
        const workflowIdSelectedDiv = form.querySelector('div[data-selected="true"]');
        const workflowId = workflowIdSelectedDiv ? workflowIdSelectedDiv.getAttribute("data-workflow-id") : "";

        // Get form elements
        const nameInput = form.querySelector('input[type="text"]');
        const descriptionInput = form.querySelector("textarea");
        const coverImageInput = form.querySelector('input[type="file"]');
        const imagePreview = form.querySelector("#image-preview");

        // Remove any existing error messages
        const existingErrors = form.querySelectorAll(".error-message");
        existingErrors.forEach((error) => error.remove());

        // Reset any previous error styling
        nameInput.style.border = "1px solid #ccc";
        descriptionInput.style.border = "1px solid #ccc";
        coverImageInput.style.border = "1px solid #ccc";

        // Validate mandatory fields
        let hasErrors = false;

        // Function to add error message below an element
        const addErrorMessage = (element, message) => {
          const errorDiv = document.createElement("div");
          errorDiv.className = "error-message";
          errorDiv.style.color = "#ff0000";
          errorDiv.style.fontSize = "12px";
          errorDiv.style.marginTop = "5px";
          errorDiv.style.marginBottom = "10px";
          errorDiv.textContent = message;

          // Insert after the element
          element.parentNode.insertBefore(errorDiv, element.nextSibling);
        };

        if (!nameInput.value.trim()) {
          nameInput.style.border = "1px solid #ff0000";
          hasErrors = true;
          addErrorMessage(nameInput, "Name is required");
        }

        if (!descriptionInput.value.trim()) {
          descriptionInput.style.border = "1px solid #ff0000";
          hasErrors = true;
          addErrorMessage(descriptionInput, "Description is required");
        }

        if (!coverImageInput.files[0] && (!imagePreview.src || imagePreview.src === "")) {
          coverImageInput.style.border = "1px solid #ff0000";
          hasErrors = true;
          addErrorMessage(coverImageInput, "Cover Image is required");
        }

        if (hasErrors) {
          return;
        }

        const formData = {
          baseWorkflowId: workflowId || "",
          name: nameInput.value,
          description: descriptionInput.value,
          type: form.querySelector("select").value,
          coverImage: coverImageInput.files[0],
          coverImageUrl: imagePreview.src,
        };
        app.ui.dialog.close();

        showMessage("Generating manifest...", "#ffffff", null, "#00000000", getLoadingSpinner("#00ff00"));
        // Get manifest and check for missing dependencies
        const manifestResponse = await getManifest(workflow_api);
        const manifestData = JSON.parse(manifestResponse);

        if (manifestData.missing_nodes?.length || manifestData.missing_models?.length) {
          let errorMessage = "Cannot submit workflow due to missing dependencies:\n\n";
          let detailedInfo = "";

          if (manifestData.missing_nodes?.length) {
            detailedInfo += "Missing Nodes:\n- " + manifestData.missing_nodes.join("\n- ") + "\n\n";
          }

          if (manifestData.missing_models?.length) {
            detailedInfo += "Missing Models:\n- " + manifestData.missing_models.join("\n- ");
          }
          showMessage(errorMessage, "#ff0000", detailedInfo);
          return;
        }

        if (manifestData.models && Object.keys(manifestData.models).length > 0) {
          showMessage("Checking models in S3...", "#ffffff", null, "#00000000", getLoadingSpinner("#00ff00"));

          const uploadResults = await uploadModelsToS3(manifestData.models);
          const errors = uploadResults.filter((result) => !result.success);
          const successfulOps = uploadResults.filter((result) => result.success);

          if (errors.length > 0) {
            let errorTitle = "Model Errors Found:";
            let detailedErrorMessages = "";

            errors.forEach((err) => {
              if (err.status === "name_mismatch") {
                detailedErrorMessages += `- ${err.modelName}: Has incorrect name. Expected: ${err.error.expected_name}\n`;
              } else if (err.status === "fetch_error") {
                detailedErrorMessages += `- ${err.modelName}: Upload failed (${
                  err.error.message || "Network error"
                })\n`;
              } else {
                detailedErrorMessages += `- ${err.modelName}: Unknown error during processing (${JSON.stringify(
                  err.error
                )})\n`;
              }
            });

            showMessage(errorTitle, "#ff0000", detailedErrorMessages);
            return; // Stop the process if there are errors
          }

          // Report success (including existing files)
          const uploadedCount = successfulOps.filter((r) => r.status === "uploaded").length;
          const existedCount = successfulOps.filter((r) => r.status === "exists").length;
          showMessage(`Model check complete. Uploaded: ${uploadedCount}, Already Existed: ${existedCount}`, "#00ff00");
        } else {
          console.log("No models found in manifest to upload.");
        }

        const submitData = new FormData();
        submitData.append("workflowUUID", formData.baseWorkflowId);
        submitData.append("workflowName", formData.name);
        submitData.append("workflowDescription", formData.description);
        submitData.append("workflowType", formData.type.toLowerCase());
        if (!formData.coverImage && formData.coverImageUrl) {
          submitData.append("coverImageUrl", formData.coverImageUrl);
        } else {
          submitData.append(
            "coverImage",
            formData.coverImage || new File([new Blob([""], { type: "image/png" })], "default.png")
          );
        }

        const workflowString = JSON.stringify(workflow, null, 2);
        const workflowBlob = new Blob([workflowString], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("workflowJson", workflowBlob, "workflow.json");

        const workflowApiString = JSON.stringify(workflow_api, null, 2);
        const workflowApiBlob = new Blob([workflowApiString], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("workflowApi", workflowApiBlob, "workflow-api.json");

        const manifestBlob = new Blob([manifestResponse], {
          type: "application/json;charset=UTF-8",
        });
        submitData.append("manifest", manifestBlob, "manifest.json");

        const url = window.location.href + "flow/submit_workflow";

        const response = await fetch(url, {
          method: "POST",
          body: submitData,
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`${response.status} - ${errorText}`);
        }

        showMessage("Workflow submitted successfully!", "#00ff00");
      } catch (error) {
        console.error("Error submitting workflow:", error);
        showMessage(error.message, "#ff0000");
      }
    };
  } catch (error) {
    console.error("Error in saveWorkflow:", error);
    showMessage("An error occurred while submitting the workflow", "#ff0000ff", error.message);
  }
};

export { populateSubmitForm, saveWorkflow };

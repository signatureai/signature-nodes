import { getAccessToken, signatureApiBaseUrl } from "./main.js";

const getWorkflowsListForForm = async (element, offset = 0, limit = 100, search = null) => {
  const accessToken = getAccessToken();
  let url = `${signatureApiBaseUrl}/api/v1_management/workflow?offset=${offset}&limit=${limit}`;
  if (search) {
    url += `&search=${search}`;
  }
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get workflows: ${response.status} ${response.statusText}`);
  }

  const parsedResponse = await response.json();
  if (parsedResponse.result && parsedResponse.result.data && parsedResponse.result.data.length !== 0) {
    return parsedResponse.result.data.map((workflow) => {
      return element("option", { value: workflow.uuid, textContent: `${workflow.name} (${workflow.uuid})` });
    });
  } else {
    return [];
  }
};

const getWorkflowById = async (workflowId) => {
  const accessToken = getAccessToken();
  const url = `${signatureApiBaseUrl}/api/v1_management/workflow/${workflowId}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get workflow: ${response.status} ${response.statusText}`);
  }

  const parsedResponse = await response.json();
  return parsedResponse.result;
};

const getWorkflowVersions = async (workflowId, offset = 0, limit = 100) => {
  const accessToken = getAccessToken();
  const url = `${signatureApiBaseUrl}/api/v1_management/workflow/${workflowId}/version?includeWorkflow=true&offset=${offset}&limit=${limit}`;
  const response = await fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to get workflow: ${response.status} ${response.statusText}`);
  }

  const parsedResponse = await response.json();
  return parsedResponse.result;
};

const getManifest = async (workflow) => {
  try {
    const url = window.location.href + "flow/create_manifest";

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        workflow: workflow,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error getting manifest:", errorText);
      throw new Error(`Failed to get manifest: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error in getManifest:", error);
    throw error;
  }
};

export { getManifest, getWorkflowById, getWorkflowsListForForm, getWorkflowVersions };

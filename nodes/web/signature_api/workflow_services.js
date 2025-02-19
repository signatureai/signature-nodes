import { getAccessToken, signatureApiBaseUrl } from "./main.js";

export const getWorkflowsListForForm = async (page = 0, limit = 100) => {
  const offset = page * limit;
  const accessToken = getAccessToken();
  const url = `${signatureApiBaseUrl}/api/v1_management/workflow?offset=${offset}&limit=${limit}`;
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
      return $el("option", { value: workflow.uuid, textContent: `${workflow.name} (${workflow.uuid})` });
    });
  } else {
    return [];
  }
};

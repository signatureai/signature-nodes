import {
  deleteAuthTokens,
  getAccessToken,
  getRefreshToken,
  getStoredAuthTokens,
  loginRequest,
  logoutRequest,
  refreshTokenRequest,
  setAuthTokens,
} from "./auth_services.js";
import { getManifest, getWorkflowById, getWorkflowsListForForm, getWorkflowVersions } from "./workflow_services.js";

const signatureApiBaseUrl = "https://signature-api-qa.signature-eks-staging.signature.ai";

export {
  deleteAuthTokens,
  getAccessToken,
  getManifest,
  getRefreshToken,
  getStoredAuthTokens,
  getWorkflowById,
  getWorkflowsListForForm,
  getWorkflowVersions,
  loginRequest,
  logoutRequest,
  refreshTokenRequest,
  setAuthTokens,
  signatureApiBaseUrl,
};

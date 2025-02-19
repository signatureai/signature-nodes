
import { signatureApiBaseUrl } from "./main.js";

const getStoredAuthTokens = () => {
    const refreshToken = getCookie("refreshToken");
    const accessToken = getCookie("accessToken");
    if (!refreshToken || !accessToken) {
        return null;
    }
    return { refresh_token: refreshToken, access_token: accessToken };
};

const getRefreshToken = () => {
    const refreshToken = getCookie("refreshToken");
    if (!refreshToken) {
        return null;
    }
    return refreshToken;
};

const getAccessToken = () => {
    const accessToken = getCookie("accessToken");
    if (!accessToken) {
        return null;
    }
    return accessToken;
};

const refreshTokenRequest = async () => {
    const refreshToken = getRefreshToken();
    const url = `${signatureApiBaseUrl}/api/v1/user/refresh-token`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${refreshToken}`
        }
    });

    if (!response.ok) {
        throw new Error("Failed to refresh token");
    }

    const data = await response.json();
    const newRefreshToken = data.result.refreshToken;
    const newAccessToken = data.result.accessToken;
    setAuthTokens(newRefreshToken, newAccessToken);
    return {
        refreshToken: newRefreshToken,
        accessToken: newAccessToken
    };
};

const loginRequest = async (email, password) => {
    const url = `${signatureApiBaseUrl}/api/v1/user/login`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    });

    
    if (!response.ok) {
        deleteAuthTokens();
        throw new Error(`Failed to login: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const refreshToken = data.result.refreshToken;
    const accessToken = data.result.accessToken;
    setAuthTokens(refreshToken, accessToken);
    return {
        refreshToken,
        accessToken,
        success: response.ok
    };
};

const logoutRequest = async () => {
    const url = `${signatureApiBaseUrl}/api/v1/user/logout`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });

    if (!response.ok) {
        deleteAuthTokens();
        throw new Error("Failed to logout");
    }
    return await response.json();
};

const setAuthTokens = (refreshToken, accessToken) => {
    document.cookie = `refreshToken=${refreshToken}; path=/`;
    document.cookie = `accessToken=${accessToken}; path=/`;
};

const deleteAuthTokens = () => {
    document.cookie = "refreshToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    document.cookie = "accessToken=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
};

// Helper function to get cookies
const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
};

export {
    deleteAuthTokens, getAccessToken, getRefreshToken, getStoredAuthTokens, loginRequest,
    logoutRequest, refreshTokenRequest, setAuthTokens
};

import {baseUrl} from "../config";
import { AppError, buildHttpError, normalizeError } from "./errors";

interface RefreshResponse {
    access_token: string;
    token_type: string;
}

export const refreshAccessToken = async (): Promise<string | null> => {
    try {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
            throw new AppError("Refresh token not found", {
                code: "AUTH_REQUIRED",
                status: 401,
                userMessage: "Session expired. Please log in again.",
            });
        }

        let response: Response;
        try {
            response = await fetch(baseUrl.concat("api/v1/token/refresh"), {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ "refresh_token": refreshToken })
            });
        } catch (error) {
            throw new AppError("Token refresh request failed", {
                code: "NETWORK_ERROR",
                userMessage: "Unable to contact the server. Check the connection and try again.",
                cause: error,
            });
        }

        if (!response.ok) {
            throw await buildHttpError(response);
        }

        const data: RefreshResponse = await response.json();
        localStorage.setItem("accessToken", data.access_token);

        return data.access_token;
    } catch (error) {
        console.error("Token refresh failed:", normalizeError(error));
        return null;
    }
};

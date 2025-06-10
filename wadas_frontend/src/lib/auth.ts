import {baseUrl} from "../config";

interface RefreshResponse {
    access_token: string;
    token_type: string;
}

export const refreshAccessToken = async (): Promise<string | null> => {
    try {
        const refreshToken = localStorage.getItem("refreshToken");
        if (!refreshToken) {
            throw new Error("Refresh token non trovato nel localStorage");
        }

        const response = await fetch(baseUrl.concat("api/v1/token/refresh"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "refresh_token": refreshToken })
        });

        if (!response.ok) {
            throw new Error(`Error refreshing token: ${response.statusText}`);
        }

        const data: RefreshResponse = await response.json();
        localStorage.setItem("accessToken", data.access_token);

        return data.access_token;
    } catch (error) {
        console.error("Errore nel refresh del token:", error);
        return null;
    }
};

import {refreshAccessToken} from "./auth";
import {ActuationEvent} from "../types/types";
import { AppError, getErrorMessage, isUnauthorizedError, normalizeError } from "./errors";

export async function tryWithRefreshing<T>(
    requestFn: () => Promise<T>
): Promise<T> {

    try {
        return await requestFn();
    } catch (error) {
        const appError = normalizeError(error);

        if (isUnauthorizedError(appError)) {
            const refreshedToken = await refreshAccessToken();
            if (!refreshedToken) {
                throw new AppError("Unauthorized", {
                    code: "AUTH_REQUIRED",
                    status: 401,
                    userMessage: "Session expired. Please log in again.",
                    cause: appError,
                });
            }

            return await requestFn();
        }

        throw appError;
    }
}

export { getErrorMessage, isUnauthorizedError };

export function isMobile(): boolean {
    return window.innerWidth < 1024;
}

export function generateActuationEventId(event: ActuationEvent) {
    return event.actuator.id + "_" + event.timestamp;
}

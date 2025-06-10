import {refreshAccessToken} from "./auth";
import {ActuationEvent} from "../types/types";

export async function tryWithRefreshing<T>(
    requestFn: () => Promise<T>
): Promise<T> {

    try {
        return await requestFn();
    } catch (error) {
        if (error instanceof Error && error.message.includes("Unauthorized")) {
            await refreshAccessToken();
            return await requestFn();
        } else {
            throw new Error("Unknown error");
        }
    }
}

export function isMobile(): boolean {
    return window.innerWidth < 1024;
}

export function generateActuationEventId(event: ActuationEvent) {
    return event.actuator.id + "_" + event.timestamp;
}
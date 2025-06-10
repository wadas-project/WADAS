import {baseUrl} from "../config";
import {
    ActuationEventResponse,
    ActuatorTypesResponse,
    AnimalsResponse,
    CamerasResponse,
    CommandsResponse,
    DetectionEventResponse
} from "../types/types";
import {DateTime} from "luxon";


async function apiGET(url: string, onReceived: (response: Response) => Object): Promise<any> {
    const token = localStorage.getItem("accessToken");
    if (!token) {
        throw new Error("Token not found");
    }
    const response = await fetch(url, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "x-access-token": token
        }
    });
    if (response.ok) {
        return onReceived(response);
    } else {
        if (response.status === 401) {
            throw new Error("Unauthorized");
        } else {
            throw new Error(`Error Code: ${response.status}.`);
        }
    }
}

export async function fetchCameras(): Promise<CamerasResponse> {
    return await apiGET(baseUrl.concat("api/v1/cameras"), (response) => {
        return response.json();
    });
}

export async function fetchAnimalsNames(): Promise<AnimalsResponse> {
    return await apiGET(baseUrl.concat("api/v1/animals"), (response) => {
        return response.json();
    })
}

export async function fetchActuatorTypes(): Promise<ActuatorTypesResponse> {
    return await apiGET(baseUrl.concat("api/v1/actuator_types"), (response) => {
        return response.json();
    })
}

export async function fetchCommands(): Promise<CommandsResponse> {
    return await apiGET(baseUrl.concat("api/v1/actuation_commands"), (response) => {
        return response.json();
    })
}

function buildDetectionEventsParamString(filterCameras: string[],
                                         filterAnimals: string[],
                                         startDate: Date | null,
                                         endDate: Date | null): URLSearchParams {

    let params = new URLSearchParams();
    if (filterCameras) {
        filterCameras.forEach((camera) => {
            params.append("camera_ids", camera)
        })
    }

    if (filterAnimals) {
        filterAnimals.forEach((animal) => {
            params.append("classified_animals", animal)
        })
    }

    if (startDate) {
        const luxonStartDate = DateTime.fromJSDate(startDate).startOf("day")
        const luxonStringDate = luxonStartDate.toISODate();
        if (luxonStringDate !== null && luxonStringDate !== undefined) {
            params.append("date_from", luxonStringDate);
        }
    }

    if (endDate) {
        const luxonEndDate = DateTime.fromJSDate(endDate).startOf("day")
        const luxonStringDate = luxonEndDate.toISODate();
        if (luxonStringDate !== null && luxonStringDate !== undefined) {
            params.append("date_to", luxonStringDate);
        }
    }
    return params;

}

export async function fetchDetectionEvents(
    offset: number,
    filterCameras: string[],
    filterAnimals: string[],
    startDate: Date | null,
    endDate: Date | null
): Promise<DetectionEventResponse> {
    let params = buildDetectionEventsParamString(
        filterCameras,
        filterAnimals,
        startDate,
        endDate);

    params.append("offset", offset.toString());

    const url = baseUrl + "api/v1/detections?" + params.toString();
    return await apiGET(url, (response) => {
        return response.json();
    })
}

function buildActuationEventsParamString(detectionId: number | null = null,
                                         filterTypes: string[] = [],
                                         filterCommands: string[] = [],
                                         startDate: Date | null = null,
                                         endDate: Date | null = null): URLSearchParams {

    let params = new URLSearchParams();

    if (detectionId) {
        params.append("detection_id", detectionId.toString())
    }

    if (filterTypes) {
        filterTypes.forEach((type) => {
            params.append("actuator_types", type)
        })
    }

    if (filterCommands) {
        filterCommands.forEach((command) => {
            params.append("commands", command)
        })
    }

    if (startDate) {
        const luxonStartDate = DateTime.fromJSDate(startDate).startOf("day")
        const luxonStringDate = luxonStartDate.toISODate();
        if (luxonStringDate !== null && luxonStringDate !== undefined) {
            params.append("date_from", luxonStringDate);
        }
    }

    if (endDate) {
        const luxonEndDate = DateTime.fromJSDate(endDate).startOf("day")
        const luxonStringDate = luxonEndDate.toISODate();
        if (luxonStringDate !== null && luxonStringDate !== undefined) {
            params.append("date_to", luxonStringDate);
        }
    }
    return params;

}

export async function fetchActuationEvents(
    offset: number,
    detectionId: number | null = null,
    filterTypes: string[] = [],
    filterCommands: string[] = [],
    startDate: Date | null = null,
    endDate: Date | null = null
): Promise<ActuationEventResponse> {
    let params = buildActuationEventsParamString(
        detectionId,
        filterTypes,
        filterCommands,
        startDate,
        endDate
    )

    params.append("offset", offset.toString());

    const url = baseUrl + "api/v1/actuations?" + params.toString();
    return await apiGET(url, (response) => {
        return response.json();
    })
}

export async function downloadImage(
    eventId: number
): Promise<Blob> {
    const url = baseUrl + "api/v1/detections/" + eventId + "/image";
    return await apiGET(url, (response) => {
        return response.blob();
    })
}

export async function fetchExportDetectionEvents(
    filterCameras: string[],
    filterAnimals: string[],
    startDate: Date | null,
    endDate: Date | null
): Promise<Blob> {
    let params = buildDetectionEventsParamString(
        filterCameras,
        filterAnimals,
        startDate,
        endDate);


    const url = baseUrl + "api/v1/detections/export?" + params.toString();
    return await apiGET(url, (response) => {
        return response.blob();
    })
}

export async function fetchExportActuationEvents(
    detectionId: number | null = null,
    filterTypes: string[] = [],
    filterCommands: string[] = [],
    startDate: Date | null = null,
    endDate: Date | null = null
): Promise<Blob> {
    let params = buildActuationEventsParamString(
        detectionId,
        filterTypes,
        filterCommands,
        startDate,
        endDate
    )

    const url = baseUrl + "api/v1/actuations/export?" + params.toString();
    return await apiGET(url, (response) => {
        return response.blob();
    })
}

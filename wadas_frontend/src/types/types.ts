// INTERFACES

export interface Actuator {
    id: number;
    name: string;
    type: string;
    last_update: string | null;
}

export interface Camera {
    id: number;
    name: string;
    type: string;
    enabled: boolean;
    actuators: Actuator[];
}

export interface ClassifiedAnimal {
    animal: string;
    probability: number;
}

export interface DetectionEvent {
    id: number;
    camera_id: number;
    detection_img_path: string;
    classification_img_path: string;
    detected_animals: number;
    classification: boolean;
    classified_animals: ClassifiedAnimal[];
    timestamp: string;
}

export interface ActuationEvent {
    actuator: Actuator;
    detection_event_id: number;
    command: string;
    timestamp: string;
}

export interface CamerasResponse {
    data: Camera[];
}

export interface AnimalsResponse {
    data: string[];
}

export interface ActuatorsResponse {
    data: Actuator[];
}

export interface ActuatorTypesResponse {
    data: string[];
}

export interface CommandsResponse {
    data: string[];
}

export interface DetectionEventResponse {
    total: number;
    count: number;
    data: DetectionEvent[];
}

export interface ActuationEventResponse {
    total: number;
    count: number;
    data: ActuationEvent[];
}

export interface ActuatorDetailedResponse {
    data: ActuatorDetailed[];
}

export interface ActuatorDetailed  {
    actuator_id: string;
    type: string;
    last_update: string | null;
    log: string | null;
    temperature: number | null;
    humidity: number | null;
    battery_status: number | null;
};

export interface ActuatorLogsResponse {
    data: string[];
}

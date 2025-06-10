// INTERFACES

export interface Actuator {
    id: number;
    name: string;
    type: string;
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
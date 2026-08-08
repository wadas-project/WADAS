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
    battery_temperature: number | null;
    battery_humidity: number | null;
};

export interface ActuatorLogsResponse {
    data: string[];
}

export type BatteryHistoryRange = "1d" | "7d" | "30d" | "90d";

export interface ActuatorBatteryReading {
    voltage: number | null;
    timestamp: string;
}

export interface ActuatorBatteryHistoryResponse {
    data: ActuatorBatteryReading[];
}

export interface ActuatorTemperaturePoint {
    temperature: number | null;
    timestamp: string;
}

export interface BatteryTemperaturePoint {
    temperature: number | null;
    timestamp: string;
}

export interface ActuatorTemperatureHistoryResponse {
    actuator: ActuatorTemperaturePoint[];
    battery: BatteryTemperaturePoint[];
}

export interface ActuatorTestResponse {
    data: {
        message: string;
        payload: {
            duration: number;
        };
    };
}

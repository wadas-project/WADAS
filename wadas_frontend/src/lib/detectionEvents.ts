import { DetectionEvent } from "../types/types";

export function isVideoDetectionEvent(event: DetectionEvent | null | undefined): boolean {
    if (!event) {
        return false;
    }

    const mediaPath = event.classification_img_path || event.detection_img_path;
    return /\.(avi|mov|mp4|mkv|wmv)$/i.test(mediaPath ?? "");
}

export function getDisplayedDetectedAnimals(event: DetectionEvent): number {
    if (event.detected_animals > 0) {
        return event.detected_animals;
    }

    if (isVideoDetectionEvent(event)) {
        return 1;
    }

    return 0;
}

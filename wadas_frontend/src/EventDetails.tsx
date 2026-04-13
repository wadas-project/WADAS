import * as React from 'react';
import {useEffect, useState} from 'react';
import 'react-datepicker/dist/react-datepicker.min.css';
import {ActuationEvent, Camera, DetectionEvent} from "./types/types";
import {getErrorMessage, isUnauthorizedError, tryWithRefreshing} from "./lib/utils";
import {downloadDetectionMedia, downloadImage, fetchActuationEvents} from "./lib/api";
import {useNavigate} from "react-router-dom";
import DetailsContainer from "./components/DetailsContainer";
import DetailsOffcanvas from "./components/DetailsOffcanvas";
import { useErrorModal } from "./components/ErrorModal";
import { isVideoDetectionEvent } from "./lib/detectionEvents";

const EventDetails = (props: {
    currentEvent: DetectionEvent | null,
    cameras: Camera[],
    onOffcanvasClose: () => void | null;
}) => {
    const [mediaUrl, setMediaUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);
    const [mediaType, setMediaType] = useState<"image" | "video" | null>(null);

    const [actuationEvents, setActuationEvents] = useState<ActuationEvent[]>([]);
    const navigate = useNavigate();
    const [isMobile] = useState(window.innerWidth < 1024);
    const [showCanvas, setShowCanvas] = useState(props.currentEvent !== null);
    const { showError } = useErrorModal();


    useEffect(() => {
        const fillImage = async () => {
            if (!props.currentEvent) {
                setMediaUrl(null);
                setMediaType(null);
                return;
            }

            const isVideo = isVideoDetectionEvent(props.currentEvent);

            setMediaType(isVideo ? "video" : "image");

            setLoading(true);
            try {
                const eventId = props.currentEvent.id;
                if (isVideo) {
                    const downloadedBlob: Blob = await tryWithRefreshing(() =>
                        downloadDetectionMedia(eventId)
                    );
                    setMediaUrl(URL.createObjectURL(downloadedBlob));
                } else {
                    const downloadedBlob: Blob = await tryWithRefreshing(() => downloadImage(eventId));
                    setMediaUrl(URL.createObjectURL(downloadedBlob));
                }
            } catch (e) {
                if (isUnauthorizedError(e)) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    showError(getErrorMessage(e), `Unable to load event ${isVideo ? "video" : "image"}`);
                }
            } finally {
                // Small delay to ensure ImageUrl is set
                await new Promise(resolve => setTimeout(resolve, 50));
                setLoading(false);
            }
        };

        const fetchRelatedActuationEvents = async () => {
            if (props.currentEvent !== null) {
                const eventId = props.currentEvent.id;
                try {
                    const actuationEventsResponse = await tryWithRefreshing(
                        () => fetchActuationEvents(0, eventId));
                    setActuationEvents(actuationEventsResponse.data);
                } catch (e) {
                    if (isUnauthorizedError(e)) {
                        console.error("Refresh token failed, redirecting to login...");
                        navigate("/");
                    } else {
                        showError(getErrorMessage(e), "Unable to load related actuation events");
                    }
                } finally {
                    setLoading(false);
                }
            }
        }

        fillImage();
        fetchRelatedActuationEvents();

        if (props.currentEvent) {
            setShowCanvas(true);
        }

    }, [props.currentEvent, navigate, showError]);

    useEffect(() => {
        return () => {
            if (mediaUrl) {
                URL.revokeObjectURL(mediaUrl);
            }
        };
    }, [mediaUrl]);


    const closeOffcanvas = () => {
        setShowCanvas(false);
        setTimeout(() => {
            if (props.onOffcanvasClose) {
                props.onOffcanvasClose();
            }
        }, 300);
    }

    return !isMobile ? (
        <DetailsContainer
            currentEvent={props.currentEvent}
            cameras={props.cameras}
            actuationEvents={actuationEvents}
            mediaUrl={mediaUrl}
            mediaType={mediaType}
            loading={loading}/>
    ) : (
        <DetailsOffcanvas
            show={showCanvas}
            onHide={closeOffcanvas}
            currentEvent={props.currentEvent}
            cameras={props.cameras}
            actuationEvents={actuationEvents}
            mediaUrl={mediaUrl}
            mediaType={mediaType}
            loading={loading}/>
    );
};

export default EventDetails;

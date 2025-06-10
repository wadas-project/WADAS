import * as React from 'react';
import {useEffect, useState} from 'react';
import 'react-datepicker/dist/react-datepicker.min.css';
import {ActuationEvent, Camera, DetectionEvent} from "./types/types";
import {tryWithRefreshing} from "./lib/utils";
import {downloadImage, fetchActuationEvents} from "./lib/api";
import {useNavigate} from "react-router-dom";
import DetailsContainer from "./components/DetailsContainer";
import DetailsOffcanvas from "./components/DetailsOffcanvas";

const EventDetails = (props: {
    currentEvent: DetectionEvent | null,
    cameras: Camera[],
    onOffcanvasClose: () => void | null;
}) => {
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const [actuationEvents, setActuationEvents] = useState<ActuationEvent[]>([]);
    const navigate = useNavigate();
    const [error, setError] = useState<string | null>(null);
    const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
    const [showCanvas, setShowCanvas] = useState(props.currentEvent !== null);


    useEffect(() => {
        const fillImage = async () => {
            if (!props.currentEvent) {
                setImageUrl(null);
                return;
            }

            setLoading(true);
            try {
                const eventId = props.currentEvent.id;
                const downloadedBlob: Blob = await tryWithRefreshing(() => downloadImage(eventId));
                setImageUrl(URL.createObjectURL(downloadedBlob));
            } catch (e) {
                if (e instanceof Error && e.message.includes("Unauthorized")) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                }
            } finally {
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
                    if (e instanceof Error && e.message.includes("Unauthorized")) {
                        console.error("Refresh token failed, redirecting to login...");
                        navigate("/");
                    } else {
                        setError(`Generic Error - ${e.message}. Please contact the administrator.`);
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

    }, [props.currentEvent, navigate]);


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
            imageUrl={imageUrl}
            loading={loading}/>
    ) : (
        <DetailsOffcanvas
            show={showCanvas}
            onHide={closeOffcanvas}
            currentEvent={props.currentEvent}
            cameras={props.cameras}
            actuationEvents={actuationEvents}
            imageUrl={imageUrl}
            loading={loading}/>
    );
};

export default EventDetails;

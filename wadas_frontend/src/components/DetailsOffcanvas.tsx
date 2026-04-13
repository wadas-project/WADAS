import {ActuationEvent, Camera, DetectionEvent} from "../types/types";
import {Button, Col, Container, Offcanvas, Row, Table, Modal} from "react-bootstrap";
import {DateTime} from "luxon";
import CustomSpinner from "./CustomSpinner";
import ActuationEventsModal from "./ActuationEventsModal";
import * as React from "react";
import {useState} from "react";

const DetailsOffcanvas = (props: {
    show: boolean;
    onHide: () => void;
    currentEvent: DetectionEvent | null;
    cameras: Camera[];
    actuationEvents: ActuationEvent[];
    mediaUrl: string | null;
    mediaType: "image" | "video" | null;
    loading: boolean;
}) => {
    const [showImageModal, setShowImageModal] = useState<boolean>(false);
    const [showActuationModal, setShowActuationModal] = useState<boolean>(false);

    const handleImageClick = () => setShowImageModal(true);
    const handleActuationClick = () => setShowActuationModal(true);
    const mediaDownloadName = getMediaDownloadName(props.currentEvent);
    const mediaMimeType = getMediaMimeType(props.currentEvent);

    return (
        <>
            <Offcanvas show={props.show} onHide={props.onHide} placement="end">
                <Offcanvas.Header closeButton>
                    <Offcanvas.Title>Detection Event Details</Offcanvas.Title>
                </Offcanvas.Header>
                <Offcanvas.Body>
                    <Container>
                        <h5 className="mb-4">Detection Event {props.currentEvent.id}</h5>
                        <Row>
                            <Col xs={12}>
                                <p>
                                    <strong>Date:</strong>{" "}
                                    {DateTime.fromISO(props.currentEvent.timestamp).toFormat("yyyy-MM-dd HH:mm")}
                                </p>
                                <p>
                                    <strong>Camera:</strong>{" "}
                                    {props.cameras.find((camera) => camera.id === props.currentEvent?.camera_id)?.name ?? "Unknown"}
                                </p>
                                <p>
                                    <strong>Classification:</strong> {props.currentEvent.classification ? "Yes" : "No"}
                                </p>
                                {props.actuationEvents.length > 0 ? (
                                    <Button variant="link" className="p-0 custom-link-big"
                                            onClick={handleActuationClick}>
                                        Related Actuation Events: {props.actuationEvents.length}
                                    </Button>
                                ) : (
                                    <p>
                                        <strong>No Actuation Event</strong>
                                    </p>
                                )}
                            </Col>
                        </Row>

                        <Row>
                            <Col xs={12} className="my-3">
                                {props.currentEvent.classified_animals.length > 0 ? (
                                    <Table borderless hover size="sm">
                                        <thead>
                                        <tr>
                                            <th>Classified Animal</th>
                                            <th>Probability</th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {props.currentEvent.classified_animals.map((item, index) => (
                                            <tr key={index}>
                                                <td>{item.animal}</td>
                                                <td>{item.probability}</td>
                                            </tr>
                                        ))}
                                        </tbody>
                                    </Table>
                                ) : (
                                    <h6>No classified animal</h6>
                                )}
                            </Col>
                        </Row>

                        <Row className="justify-content-center">
                            <Col xs={12} className="text-center">
                                {props.loading ? (
                                    <CustomSpinner/>
                                ) : props.mediaType === "video" && props.mediaUrl ? (
                                    <>
                                        <video
                                            controls
                                            preload="metadata"
                                            style={{maxWidth: "100%", maxHeight: "300px", cursor: "pointer"}}
                                            onClick={handleImageClick}
                                        >
                                            <source src={props.mediaUrl} type={mediaMimeType ?? undefined}/>
                                            Your browser does not support video playback.
                                        </video>
                                        <div className="mt-3">
                                            <Button
                                                as="a"
                                                href={props.mediaUrl}
                                                download={mediaDownloadName}
                                                variant="outline-primary"
                                            >
                                                Download video
                                            </Button>
                                        </div>
                                    </>
                                ) : props.mediaUrl ? (
                                    <img
                                        src={props.mediaUrl}
                                        alt="Detection"
                                        style={{maxWidth: "100%", maxHeight: "300px", cursor: "pointer"}}
                                        onClick={handleImageClick}
                                    />
                                ) : (
                                    <h6>No Image Available</h6>
                                )}
                            </Col>
                        </Row>
                    </Container>
                </Offcanvas.Body>
            </Offcanvas>

            <Modal show={showImageModal} onHide={() => setShowImageModal(false)} centered size="lg">
                <Modal.Body className="d-flex justify-content-center">
                    {props.mediaType === "video" && props.mediaUrl ? (
                        <video controls autoPlay style={{width: "100%", height: "auto"}}>
                            <source src={props.mediaUrl} type={mediaMimeType ?? undefined}/>
                            Your browser does not support video playback.
                        </video>
                    ) : props.mediaUrl ? (
                        <img src={props.mediaUrl} alt="Detection" style={{width: "100%", height: "auto"}}/>
                    ) : null}
                </Modal.Body>
            </Modal>

            <ActuationEventsModal actuations={props.actuationEvents} show={showActuationModal}
                                  onHide={() => setShowActuationModal(false)}/>
        </>
    );
};

export default DetailsOffcanvas;

function getMediaDownloadName(event: DetectionEvent | null): string {
    if (!event) {
        return "detection-media";
    }

    const mediaPath = event.classification_img_path || event.detection_img_path;
    const extension = mediaPath?.split(".").pop();

    return extension
        ? `detection-event-${event.id}.${extension}`
        : `detection-event-${event.id}`;
}

function getMediaMimeType(event: DetectionEvent | null): string | null {
    if (!event) {
        return null;
    }

    const mediaPath = (event.classification_img_path || event.detection_img_path).toLowerCase();

    if (mediaPath.endsWith(".mp4")) return "video/mp4";
    if (mediaPath.endsWith(".avi")) return "video/x-msvideo";
    if (mediaPath.endsWith(".mov")) return "video/quicktime";
    if (mediaPath.endsWith(".mkv")) return "video/x-matroska";
    if (mediaPath.endsWith(".wmv")) return "video/x-ms-wmv";

    return null;
}

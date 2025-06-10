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
    imageUrl: string;
    loading: boolean;
}) => {
    const [showImageModal, setShowImageModal] = useState<boolean>(false);
    const [showActuationModal, setShowActuationModal] = useState<boolean>(false);

    const handleImageClick = () => setShowImageModal(true);
    const handleActuationClick = () => setShowActuationModal(true);

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
                                ) : props.imageUrl ? (
                                    <img
                                        src={props.imageUrl}
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
                    {props.imageUrl &&
                        <img src={props.imageUrl} alt="Detection" style={{width: "100%", height: "auto"}}/>}
                </Modal.Body>
            </Modal>

            <ActuationEventsModal actuations={props.actuationEvents} show={showActuationModal}
                                  onHide={() => setShowActuationModal(false)}/>
        </>
    );
};

export default DetailsOffcanvas;

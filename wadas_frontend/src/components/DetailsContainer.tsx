import {ActuationEvent, Camera, DetectionEvent} from "../types/types";
import {Button, Col, Container, Modal, Row, Table} from "react-bootstrap";
import {DateTime} from "luxon";
import CustomSpinner from "./CustomSpinner";
import ActuationEventsModal from "./ActuationEventsModal";
import * as React from "react";
import {useState} from "react";

const DetailsContainer = (props: {
    currentEvent: DetectionEvent | null,
    cameras: Camera[],
    actuationEvents: ActuationEvent[],
    imageUrl: string,
    loading: boolean
}) => {

    const [showImageModal, setShowImageModal] = useState<boolean>(false);
    const [showActuationModal, setShowActuationModal] = useState<boolean>(false);


    const handleImageClick = () => {
        setShowImageModal(true);
    };

    const handleActuationClick = () => {
        setShowActuationModal(true);
    };

    return (
        <Container>
            <Row className={"d-none d-lg-flex"}>
                <Col md={6} className="position-relative">
                    {props.currentEvent === null ? (
                        <h5>No event selected</h5>
                    ) : (
                        <Container>
                            <h5 className="mb-4">Detection Event {props.currentEvent.id}</h5>
                            <Row>
                                <Col md={5}>
                                    <div>
                                        <p>
                                            <strong>Date:</strong> {DateTime.fromISO(props.currentEvent.timestamp).toFormat("yyyy-MM-dd HH:mm")}
                                        </p>
                                        <p>
                                            <strong>Camera:</strong> {props.cameras.find(camera =>
                                            camera.id === props.currentEvent?.camera_id)?.name ?? "Unknown"}
                                        </p>
                                        <p>
                                            <strong>Classification:</strong> {props.currentEvent.classification ? "yes" : "no"}
                                        </p>

                                        {props.actuationEvents.length > 0 ? (
                                            <Button
                                                variant="link"
                                                className="p-0 custom-link-big"
                                                onClick={handleActuationClick}>
                                                Related Actuation Events: {props.actuationEvents.length}
                                            </Button>
                                        ) : (
                                            <p>
                                                <strong>No Actuation Event</strong>
                                            </p>
                                        )}

                                    </div>
                                </Col>
                                <Col md={1} className="col-separator"></Col>

                                <Col md={6} style={{maxHeight: "200px", overflowY: "auto", padding: "5px"}}>
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
                                        <Container className="d-flex justify-content-center align-items-center h-100">
                                            <h6>No classified animal</h6>
                                        </Container>
                                    )}
                                </Col>
                            </Row>
                        </Container>
                    )}
                </Col>

                <Col md={6} className="d-flex justify-content-center align-items-center">
                    {props.currentEvent === null ? (
                        <div></div>
                    ) : (
                        <div style={{textAlign: "center", padding: "10px", border: "1px solid #ddd"}}>
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
                        </div>
                    )}
                </Col>
            </Row>

            <Modal show={showImageModal} onHide={() => setShowImageModal(false)} centered size="lg">
                <Modal.Body className="d-flex justify-content-center">
                    {props.imageUrl && <img src={props.imageUrl} alt="Detection or Classification Image"
                                            style={{width: "100%", height: "auto"}}/>}
                </Modal.Body>
            </Modal>

            <ActuationEventsModal actuations={props.actuationEvents}
                                  show={showActuationModal}
                                  onHide={() => setShowActuationModal(false)}>
            </ActuationEventsModal>
        </Container>)
}

export default DetailsContainer;
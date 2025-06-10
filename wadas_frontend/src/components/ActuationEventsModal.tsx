import * as React from 'react';
import {ActuationEvent} from "../types/types";
import {Modal, Table} from "react-bootstrap";
import {DateTime} from "luxon";

const ActuationEventsModal = (props: { actuations: ActuationEvent[], show: boolean, onHide: () => void }) => {
    return (
        <Modal show={props.show} onHide={props.onHide} centered size="lg">
            <Modal.Header closeButton>
                <Modal.Title>Related Actuation Events</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table striped bordered hover>
                    <thead>
                    <tr>
                        <th>Date</th>
                        <th>Actuator</th>
                        <th>Command</th>
                    </tr>
                    </thead>
                    <tbody>
                    {props.actuations.map((event, index) => (
                        <tr key={"row" + index}>
                            <td>{DateTime.fromISO(event.timestamp).toFormat("yyyy-MM-dd HH:mm")}</td>
                            <td>{event.actuator.name}</td>
                            <td>{event.command}</td>
                        </tr>
                    ))}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default ActuationEventsModal;
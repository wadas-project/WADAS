import * as React from 'react';
import {Camera} from "../types/types";
import {Badge, Modal, Table} from "react-bootstrap";

const ActuatorsModal = (props: { camera: Camera | null, show: boolean, onHide: () => void }) => {
    return (
        <Modal show={props.show} onHide={props.onHide} centered size="sm">
            <Modal.Header closeButton>
                <Modal.Title>{props.camera?.name}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Table borderless>
                    <thead>
                    <tr>
                        <th>Connected Actuators</th>
                    </tr>
                    </thead>
                    <tbody>
                    {props.camera?.actuators.map(item => (
                        <tr key={"row" + item.id}>
                            <td>
                                <Badge key={item.id} className="me-2 mb-2 custom-badge">
                                    {item.name}
                                </Badge>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </Table>
            </Modal.Body>
        </Modal>
    );
};

export default ActuatorsModal;
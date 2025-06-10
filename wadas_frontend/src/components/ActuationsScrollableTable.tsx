import * as React from 'react';
import {Container, Table} from "react-bootstrap";
import {ActuationEvent} from "../types/types";
import {DateTime} from "luxon";
import PaginationBar from "./PaginationBar";
import {generateActuationEventId} from "../lib/utils";

const ActuationsScrollableTable = (props: {
    actuations: ActuationEvent[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}) => {



    return (
        <Container className="p-0 d-flex flex-column" style={{height: "75vh"}}>
            <div style={{overflowX: "auto", height: "80%", border: "1px solid #ddd"}}>
                <Table hover responsive>
                    <thead>
                    <tr>
                        <th>Date</th>
                        <th>Actuator</th>
                        <th>Command</th>
                    </tr>
                    </thead>
                    <tbody>
                    {props.actuations.map((item) => {
                        return (
                            <tr
                                key={generateActuationEventId(item)}
                            >
                                <td>{DateTime.fromISO(item.timestamp).toFormat("yyyy-MM-dd HH:mm")}</td>
                                <td>{item.actuator.name}</td>
                                <td>{item.command}</td>
                            </tr>
                        );
                    })}
                    </tbody>
                </Table>
            </div>

            <PaginationBar currentPage={props.currentPage}
                           totalPages={props.totalPages}
                           onPageChange={props.onPageChange}/>
        </Container>
    );
}

export default ActuationsScrollableTable;
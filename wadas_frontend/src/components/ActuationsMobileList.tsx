import * as React from "react";
import {useRef} from "react";
import {Card, Container} from "react-bootstrap";
import {ActuationEvent} from "../types/types";
import {DateTime} from "luxon";
import PaginationBar from "./PaginationBar";
import {generateActuationEventId} from "../lib/utils";

const ActuationsMobileList = (props: {
    actuations: ActuationEvent[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    const handlePageChange = (newPage: number) => {
        props.onPageChange(newPage);

        if (scrollRef.current) {
            scrollRef.current.scrollTop = 0;
        }
    };

    return (
        <Container className="p-0">
            <div style={{display: "flex", flexDirection: "column", height: "80dvh"}}>
                <PaginationBar
                    currentPage={props.currentPage}
                    totalPages={props.totalPages}
                    onPageChange={handlePageChange}
                />
                <div ref={scrollRef} style={{overflowY: "auto", flexGrow: 1, paddingRight: "5px"}}>
                    {props.actuations.map((item) => {
                        return (
                            <Card
                                key={generateActuationEventId(item)}
                                className={"mb-2 p-2"}
                            >
                                <Card.Body>
                                    <Card.Title>
                                        <strong>Date:</strong> {DateTime.fromISO(item.timestamp).toFormat("yyyy-MM-dd HH:mm")}
                                    </Card.Title>
                                    <Card.Text>
                                        <strong>Actuator:</strong> {item.actuator.name} <br/>
                                        <strong>Command:</strong> {item.command}
                                    </Card.Text>
                                </Card.Body>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </Container>
    );
};

export default ActuationsMobileList;

import * as React from "react";
import {useRef} from "react";
import {Card, Container} from "react-bootstrap";
import {Camera, DetectionEvent} from "../types/types";
import {DateTime} from "luxon";
import PaginationBar from "./PaginationBar";

const DetectionsMobileList = (props: {
    detections: DetectionEvent[];
    knownCameras: Camera[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    onCardSelected: (event: DetectionEvent) => void;
    selectedEventId: number | null;
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
                    {props.detections.map((item) => {
                        const camera = props.knownCameras.find((camera) => camera.id === item.camera_id);
                        return (
                            <Card
                                key={item.id}
                                className={`mb-2 p-2 ${item.id === props.selectedEventId ? "border-primary" : ""}`}
                                onClick={() => props.onCardSelected(item)}
                                style={{cursor: "pointer"}}
                            >
                                <Card.Body>
                                    <Card.Title>
                                        <strong>Event ID:</strong> {item.id}
                                    </Card.Title>
                                    <Card.Text>
                                        <strong>Camera:</strong> {camera?.name ?? "N/A"} <br/>
                                        <strong>Date:</strong> {DateTime.fromISO(item.timestamp).toFormat("yyyy-MM-dd HH:mm")}
                                        <br/>
                                        <strong># Detected Animals:</strong> {item.detected_animals} <br/>
                                        <strong># Classified Animals:</strong> {item.classified_animals.length}
                                        <br/>
                                        <strong>Classified Animals:</strong>{" "}
                                        {item.classified_animals.slice(0, 3).map((animal) => animal.animal).join(", ")}
                                        {item.classified_animals.length > 3 && " ..."}
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

export default DetectionsMobileList;

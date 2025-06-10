import * as React from "react";
import {useRef, useState} from "react";
import {Container, Table} from "react-bootstrap";
import {Camera, DetectionEvent} from "../types/types";
import {DateTime} from "luxon";
import PaginationBar from "./PaginationBar";

const DetectionsScrollableTable = (props: {
    detections: DetectionEvent[];
    knownCameras: Camera[];
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    onRowSelected: (row: DetectionEvent) => void;
}) => {
    const [selectedEventId, setSelectedEventId] = useState<number | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    const handleRowClick = (event: DetectionEvent) => {
        setSelectedEventId(event.id);
        props.onRowSelected(event);
    };

    const handlePageChange = (newPage: number) => {
        props.onPageChange(newPage);

        if (scrollRef.current) {
            scrollRef.current.scrollTop = 0;
        }
    };

    return (
        <Container className="h-100 p-0">
            <div ref={scrollRef} style={{overflowX: "auto", maxHeight: "80%", border: "1px solid #ddd"}}>
                <Table hover responsive striped>
                    <thead>
                    <tr>
                        <th>Event ID</th>
                        <th>Camera</th>
                        <th>Date</th>
                        <th># Detected Animals</th>
                        <th># Classified Animals</th>
                        <th>Classified Animals</th>
                    </tr>
                    </thead>
                    <tbody>
                    {props.detections.map((item) => {
                        const camera = props.knownCameras.find(
                            camera => camera.id === item.camera_id);
                        return (
                            <tr
                                key={item.id}
                                className={item.id === selectedEventId ? "selected-row" : ""}
                                onClick={() => handleRowClick(item)}
                                style={{cursor: "pointer"}}
                            >
                                <td>{item.id}</td>
                                <td>{camera?.name ?? "N/A"}</td>
                                <td>{DateTime.fromISO(item.timestamp).toFormat("yyyy-MM-dd HH:mm")}</td>
                                <td>{item.detected_animals}</td>
                                <td>{item.classified_animals.length}</td>
                                <td>
                                    {item.classified_animals
                                        .slice(0, 3)
                                        .map(animal => animal.animal)
                                        .join(", ")
                                    }
                                    {item.classified_animals.length > 3 && " ..."}
                                </td>

                            </tr>
                        );
                    })}
                    </tbody>
                </Table>
            </div>
            <PaginationBar
                currentPage={props.currentPage}
                totalPages={props.totalPages}
                onPageChange={handlePageChange}
            />
        </Container>
    );
};

export default DetectionsScrollableTable;

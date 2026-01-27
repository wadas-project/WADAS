import * as React from "react";
import { useEffect, useState } from "react";
import { Alert, Container, Row, Col, Button } from "react-bootstrap";
import { useNavigate, useParams } from "react-router-dom";

import CustomNavbar from "./components/CustomNavbar";
import CustomSpinner from "./components/CustomSpinner";

import { tryWithRefreshing } from "./lib/utils";
import { fetchActuatorDetail, postActuatorTest,fetchActuatorLogs } from "./lib/api";
import { ActuatorDetailed, ActuatorLogsResponse } from "./types/types";

const ActuatorDetail = () => {
    const { actuatorId } = useParams<{ actuatorId: string }>();
    const navigate = useNavigate();

    const [actuator, setActuator] = useState<ActuatorDetailed | null>(null);
    const [actuatorLogs, setActuatorLogs] = useState<string[]|null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);


    const handleTest = async (actuatorId: string): Promise<void> => {
        await tryWithRefreshing(() =>
            postActuatorTest(actuatorId)
        );
    };
   const handleRefreshLogs = async (actuatorId: string): Promise<void> => {
        const response = await tryWithRefreshing(() =>
            fetchActuatorLogs(actuatorId)
        );
        
          setActuatorLogs(response.data)
              
    };
    useEffect(() => {


        const loadPage = async () => {
            try {
                if (!actuatorId) {
                    setError("Invalid actuator id");
                    setLoading(false);
                    return;
                }

                const response = await tryWithRefreshing(() =>
                    fetchActuatorDetail(actuatorId)
                );

                setActuator(response);
                setActuatorLogs(response.log ? response.log.split("\n") : []);
                setLoading(false);

            } catch (e: any) {
                if (e instanceof Error && e.message.includes("Unauthorized")) {
                    navigate("/");
                } else {
                    setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                    setLoading(false);
                }
            }
        };

        loadPage();
    }, [actuatorId]);



    return (
        <div className="padded-div">
            <CustomNavbar />

            <Container className="mt-3">
                {loading ? (
                    <CustomSpinner />
                ) : error ? (
                    <Alert variant="danger">{error}</Alert>
                ) : !actuator ? (
                    <Alert variant="warning">Actuator not found</Alert>
                ) : (
                    <>
                        {/* Header */}
                        <Row className="align-items-center mb-4">
                            <Col>
                                <h4>Actuator: {actuator.actuator_id}</h4>
                                <small className="text-muted">
                                    Last connection:{" "}
                                    {actuator.last_update
                                        ? new Date(actuator.last_update).toLocaleString()
                                        : "—"}
                                </small>
                            </Col>
                            <Col className="text-end">
                                <Button
                                    variant="info"
                                    onClick={() =>
                                        navigate(`/actuations?actuator=${actuator.actuator_id}`)
                                    }
                                >
                                    Actuation Events
                                </Button>
                            </Col>
                        </Row>

                        {/* Commands */}
                        <Row className="mb-4">
                            <Col>
                                <h6>Commands</h6>
                                <div className="border p-3 d-flex gap-3">
                                    <Button variant="info" onClick={() => handleTest(actuator.actuator_id)}>Test</Button>
                                    {/* <Button variant="primary" >Reboot</Button> */}
                                    <Button variant="info" onClick={() => handleRefreshLogs(actuator.actuator_id)}>Refresh log</Button>
                                </div>
                            </Col>
                        </Row>

                        {/* Telemetry */}
                        <Row className="mb-4">
                            <Col md={3}>
                                <strong>Type</strong>
                                <div>{actuator.type}</div>
                            </Col>
                            <Col md={3}>
                                <strong>Battery</strong>
                                <div>{actuator.battery_status ?? "—"} V</div>
                            </Col>
                            <Col md={3}>
                                <strong>Temperature</strong>
                                <div>{actuator.temperature ?? "—"} °C</div>
                            </Col>
                            <Col md={3}>
                                <strong>Humidity</strong>
                                <div>{actuator.humidity ?? "—"} %</div>
                            </Col>
                        </Row>

                        {/* Log */}
                        <Row>
                            <Col>
                                <h6>Log</h6>
                                <div
                                    className="border p-3"
                                    style={{
                                        maxHeight: "300px",
                                        overflowY: "auto",
                                        whiteSpace: "pre-wrap",
                                        fontSize: "0.85rem",
                                        backgroundColor: "#f8f9fa",
                                    }}
                                >
                                    {actuator.log || "No log available"}
                                </div>
                            </Col>
                        </Row>
                    </>
                )}
            </Container>
        </div>
    );
};

export default ActuatorDetail;

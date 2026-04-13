import { useEffect, useState } from "react";
import { Alert, Button, Col, Container, Modal, Row } from "react-bootstrap";
import { useNavigate, useParams } from "react-router-dom";

import CustomNavbar from "./components/CustomNavbar";
import CustomSpinner from "./components/CustomSpinner";
import { fetchActuatorDetail, fetchActuatorLogs, postActuatorTest } from "./lib/api";
import { getErrorMessage, isUnauthorizedError, tryWithRefreshing } from "./lib/utils";
import { ActuatorDetailed } from "./types/types";
import { useErrorModal } from "./components/ErrorModal";

const ActuatorDetail = () => {
    const { actuatorId } = useParams<{ actuatorId: string }>();
    const navigate = useNavigate();

    const [actuator, setActuator] = useState<ActuatorDetailed | null>(null);
    const [actuatorLogs, setActuatorLogs] = useState<string[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [logsLoading, setLogsLoading] = useState<boolean>(false);
    const [testLoading, setTestLoading] = useState<boolean>(false);
    const [showTestModal, setShowTestModal] = useState<boolean>(false);
    const [testMessage, setTestMessage] = useState<string>("Waiting...");
    const [loadFailed, setLoadFailed] = useState<boolean>(false);
    const { showError } = useErrorModal();

    const handleTest = async (currentActuatorId: string): Promise<void> => {
        setShowTestModal(true);
        setTestLoading(true);
        setTestMessage("Waiting...");
        try {
            const response = await tryWithRefreshing(() =>
                postActuatorTest(currentActuatorId)
            );
            setTestMessage(response?.data?.message ?? "Waiting...");
        } catch (e) {
            setShowTestModal(false);
            if (isUnauthorizedError(e)) {
                navigate("/");
                return;
            }

            showError(getErrorMessage(e), "Actuator test failed");
        } finally {
            setTestLoading(false);
        }
    };

    const handleRefreshLogs = async (currentActuatorId: string): Promise<void> => {
        setLogsLoading(true);
        try {
            const response = await tryWithRefreshing(() =>
                fetchActuatorLogs(currentActuatorId)
            );

            setActuatorLogs(response.data.log ?? []);
        } catch (e) {
            if (isUnauthorizedError(e)) {
                navigate("/");
                return;
            }

            showError(getErrorMessage(e), "Unable to refresh logs");
        } finally {
            setLogsLoading(false);
        }
    };

    useEffect(() => {
        const loadPage = async () => {
            try {
                if (!actuatorId) {
                    setLoadFailed(true);
                    showError("Invalid actuator id", "Unable to load actuator");
                    setLoading(false);
                    return;
                }

                const detailResponse = await tryWithRefreshing(() =>
                    fetchActuatorDetail(actuatorId)
                );

                setActuator(detailResponse);
                setLoading(false);
                setLogsLoading(true);

                try {
                    const logsResponse = await tryWithRefreshing(() =>
                        fetchActuatorLogs(actuatorId)
                    );
                    setActuatorLogs(logsResponse.data.log ?? []);
                } catch (e) {
                    if (isUnauthorizedError(e)) {
                        navigate("/");
                        return;
                    }

                    showError(getErrorMessage(e), "Unable to load logs");
                } finally {
                    setLogsLoading(false);
                }
            } catch (e) {
                if (isUnauthorizedError(e)) {
                    navigate("/");
                } else {
                    setLoadFailed(true);
                    showError(getErrorMessage(e), "Unable to load actuator");
                    setLoading(false);
                }
            }
        };

        loadPage();
    }, [actuatorId, navigate, showError]);

    return (
        <div className="padded-div">
            <CustomNavbar />

            <Modal show={showTestModal} onHide={() => setShowTestModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Actuator test</Modal.Title>
                </Modal.Header>
                <Modal.Body className="text-center py-4">{testMessage}</Modal.Body>
            </Modal>

            <Container className="mt-3">
                {loading ? (
                    <CustomSpinner />
                ) : loadFailed ? (
                    <Alert variant="secondary">Unable to load actuator details</Alert>
                ) : !actuator ? (
                    <Alert variant="warning">Wating...</Alert>
                ) : (
                    <>
                        <Row className="align-items-center mb-4">
                            <Col>
                                <h4>Actuator: {actuator.actuator_id}</h4>
                                <small className="text-muted">
                                    Last connection:{" "}
                                    {actuator.last_update
                                        ? new Date(actuator.last_update).toLocaleString()
                                        : "-"}
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

                        <Row className="mb-4">
                            <Col>
                                <h6>Commands</h6>
                                <div className="border p-3 d-flex gap-3">
                                    <Button
                                        variant="info"
                                        onClick={() => handleTest(actuator.actuator_id)}
                                        disabled={testLoading}
                                    >
                                        Test
                                    </Button>
                                    <Button
                                        variant="info"
                                        onClick={() => handleRefreshLogs(actuator.actuator_id)}
                                    >
                                        Refresh log
                                    </Button>
                                </div>
                            </Col>
                        </Row>

                        <Row className="mb-4">
                            <Col md={3}>
                                <strong>Type</strong>
                                <div>{actuator.type}</div>
                            </Col>
                            <Col md={3}>
                                <strong>Battery</strong>
                                <div>{actuator.battery_status ?? "-"} V</div>
                            </Col>
                            <Col md={3}>
                                <strong>Temperature</strong>
                                <div>{actuator.temperature ?? "-"} °C</div>
                            </Col>
                            <Col md={3}>
                                <strong>Humidity</strong>
                                <div>{actuator.humidity ?? "-"} %</div>
                            </Col>
                        </Row>

                        <Row>
                            <Col>
                                <div className="d-flex justify-content-between align-items-center mb-2">
                                    <h6 className="mb-0">Log</h6>
                                    {logsLoading ? <small className="text-muted">Loading logs...</small> : null}
                                </div>
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
                                    {logsLoading ? (
                                        <div className="d-flex justify-content-center py-3">
                                            <CustomSpinner />
                                        </div>
                                    ) : actuatorLogs.length > 0
                                        ? actuatorLogs.join("\n")
                                        : "No log available"}
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

import * as React from "react";
import {useEffect, useState} from "react";
import {Alert, Button, Col, Container, Modal, Row} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import CustomNavbar from "./components/CustomNavbar";
import Select, {MultiValue} from "react-select";
import DatePick from "./components/DatePick";
import {isMobile, tryWithRefreshing} from "./lib/utils";
import {useNavigate} from 'react-router-dom';
import CustomSpinner from "./components/CustomSpinner";
import {ActuationEvent, ActuationEventResponse, ActuatorTypesResponse, CommandsResponse} from "./types/types";
import {fetchActuationEvents, fetchActuatorTypes, fetchCommands, fetchExportActuationEvents} from "./lib/api";
import ActuationsScrollableTable from "./components/ActuationsScrollableTable";
import ActuationsMobileList from "./components/ActuationsMobileList";


type ActuatorTypeOption = {
    value: string;
    label: string;
}

type CommandOption = {
    value: string;
    label: string;
}

const ActuationEvents = () => {
    const pageSize = 20;
    const [showFilters, setShowFilters] = useState(false);
    const [actuatorTypeOptions, setActuatorTypeOptions] = useState<ActuatorTypeOption[]>([]);
    const [commandOptions, setCommandOptions] = useState<CommandOption[]>([]);
    const [actuations, setActuations] = useState<ActuationEvent[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [exportLoading, setExportLoading] = useState<boolean>(false);
    const [selectedActuatorType, setSelectedActuatorType] = useState<MultiValue<ActuatorTypeOption>>([]);
    const [selectedCommand, setSelectedCommand] = useState<MultiValue<CommandOption>>([]);
    const [error, setError] = useState<string | null>(null);
    const [exportError, setExportError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const navigate = useNavigate();
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [mobileFlag, setMobileFlag] = useState(isMobile());


    const updateDateRange = (dates: [Date | null, Date | null]) => {
        const [start, end] = dates;
        setStartDate(start);
        setEndDate(end);
    };

    const updateActuationData = async (page = 1) => {
        try {
            const offset = (page - 1) * pageSize;
            const actuationsResponse: ActuationEventResponse = await tryWithRefreshing(() =>
                fetchActuationEvents(
                    offset,
                    null,
                    selectedActuatorType.map(actType => actType.value),
                    selectedCommand.map(command => command.value),
                    startDate,
                    endDate
                )
            );
            setActuations(actuationsResponse.data)
            setTotalPages(Math.ceil(actuationsResponse.total / pageSize));
            setCurrentPage(page);
            setLoading(false);
        } catch (e) {
            if (e instanceof Error && e.message.includes("Unauthorized")) {
                console.error("Refresh token failed, redirecting to login...");
                navigate("/");
            } else {
                setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                setLoading(false);
            }
        }
    };

    useEffect(() => {
        const fillActuatorTypeOptions = async () => {
            try {
                const actuatorTypesResponse: ActuatorTypesResponse = await tryWithRefreshing(fetchActuatorTypes);
                let optionsArray = actuatorTypesResponse.data.map(actuatorType => ({
                    value: actuatorType,
                    label: actuatorType
                }));

                setActuatorTypeOptions(optionsArray)
                setLoading(false);
            } catch (e) {
                if (e instanceof Error && e.message.includes("Unauthorized")) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                }
            }
        };

        const fillCommandOptions = async () => {
            try {
                const commandsResponse: CommandsResponse = await tryWithRefreshing(fetchCommands);
                let optionsArray = commandsResponse.data.map(command => ({
                    value: command,
                    label: command
                }));

                setCommandOptions(optionsArray)
                setLoading(false);
            } catch (e) {
                if (e instanceof Error && e.message.includes("Unauthorized")) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                }
            }
        };

        fillActuatorTypeOptions();
        fillCommandOptions();
        updateActuationData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Gestore del cambio di selezione
    const handleChangeActuatorType = (selected: MultiValue<ActuatorTypeOption>) => {
        setSelectedActuatorType(selected);
    };

    const handleChangeCommand = (selected: MultiValue<CommandOption>) => {
        setSelectedCommand(selected);
    };


    const exportResults = () => async () => {
        setExportLoading(true);
        try {
            const responseBlob: Blob = await tryWithRefreshing(() =>
                fetchExportActuationEvents(
                    null,
                    selectedActuatorType.map(actType => actType.value),
                    selectedCommand.map(command => command.value),
                    startDate,
                    endDate
                )
            );

            const url = window.URL.createObjectURL(responseBlob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "actuation_events.csv";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        } catch (e) {
            if (e instanceof Error && e.message.includes("Unauthorized")) {
                console.error("Refresh token failed, redirecting to login...");
                navigate("/");
            } else {
                setExportError("Problem exporting data");
            }
        } finally {
            setExportLoading(false);
        }
    }

    return (
        <div className={"padded-div"}>
            <CustomNavbar/>
            <Container className={"mt-1"}>
                {loading ? (
                    <Container style={{flex: 1, display: "flex", flexDirection: "column"}}>
                        <CustomSpinner/>
                    </Container>
                ) : error ? (
                    <Alert variant="danger">{error}</Alert>
                ) : (
                    <>
                        {!mobileFlag ? (
                            // Desktop view
                            <Container style={{flex: 1, display: "flex", flexDirection: "column"}}>
                                <Container style={{display: "flex", flexDirection: "column"}}>
                                    <Container className="mt-3">
                                        <Row className="mb-3">
                                            <Col md={3}>
                                                <Select
                                                    id="multi-select"
                                                    isMulti
                                                    options={actuatorTypeOptions}
                                                    value={selectedActuatorType}
                                                    onChange={handleChangeActuatorType}
                                                    placeholder={<div className={"custom-placeholder"}>select
                                                        actuator types...</div>}
                                                />
                                            </Col>
                                            <Col md={3}>
                                                <Select
                                                    id="multi-select"
                                                    isMulti
                                                    options={commandOptions}
                                                    value={selectedCommand}
                                                    onChange={handleChangeCommand}
                                                    placeholder={<div className={"custom-placeholder"}>select
                                                        actuation commands...</div>}
                                                />
                                            </Col>
                                            <Col md={3}>
                                                <DatePick
                                                    startDate={startDate}
                                                    endDate={endDate}
                                                    onDateChange={updateDateRange}
                                                />
                                            </Col>
                                            <Col md={1}>
                                                <Button
                                                    variant="primary"
                                                    className="custom-button dark-background"
                                                    onClick={() => updateActuationData(1)}>
                                                    Apply
                                                </Button>
                                            </Col>

                                            <Col md={2} className="d-flex">
                                                {exportLoading ? (
                                                    <CustomSpinner className={"mt-1 ms-auto me-5"}/>
                                                ) : exportError ? (
                                                    <Alert variant="danger" className={"m-0 p-2"}
                                                           style={{fontSize: "12px"}}>{exportError}</Alert>
                                                ) : (
                                                    <Button
                                                        variant="primary"
                                                        className="custom-button ms-auto"
                                                        onClick={exportResults()}>
                                                        Export results
                                                    </Button>)
                                                }
                                            </Col>
                                        </Row>
                                    </Container>

                                    <Container style={{flex: 1, overflow: "hidden"}}>
                                        <ActuationsScrollableTable
                                            actuations={actuations}
                                            currentPage={currentPage}
                                            totalPages={totalPages}
                                            onPageChange={updateActuationData}
                                        />
                                    </Container>
                                </Container>
                            </Container>
                        ) : (
                            // Mobile view
                            <Container>
                                <Row className="mb-3 mt-3 d-flex align-items-center">
                                    <Col xs={8}>
                                        <h3>Actuation Events</h3>
                                    </Col>
                                    <Col xs={4} className="d-flex justify-content-end">
                                        <Button
                                            variant="primary"
                                            className="custom-button dark-background"
                                            onClick={() => setShowFilters(true)}
                                        >
                                            Filter
                                        </Button>
                                    </Col>
                                </Row>

                                <Modal show={showFilters} onHide={() => setShowFilters(false)}>
                                    <Modal.Header closeButton>
                                        <Modal.Title>Filters</Modal.Title>
                                    </Modal.Header>
                                    <Modal.Body>
                                        <Select
                                            id="multi-select"
                                            isMulti
                                            options={actuatorTypeOptions}
                                            value={selectedActuatorType}
                                            onChange={handleChangeActuatorType}
                                            placeholder={<div className={"custom-placeholder"}>select
                                                actuator types...</div>}
                                        />
                                        <Select
                                            id="multi-select"
                                            isMulti
                                            options={commandOptions}
                                            value={selectedCommand}
                                            onChange={handleChangeCommand}
                                            placeholder={<div className={"custom-placeholder"}>select
                                                actuation commands...</div>}
                                            className="mt-3"
                                            styles={{
                                                container: (baseStyles, state) => ({
                                                    ...baseStyles,
                                                    marginBottom: "1rem !important",
                                                }),
                                            }}
                                        />
                                        <DatePick
                                            startDate={startDate}
                                            endDate={endDate}
                                            onDateChange={updateDateRange}
                                        />
                                        <Button
                                            variant="primary"
                                            className="custom-button dark-background"
                                            style={{marginTop: "1rem"}}
                                            onClick={() => {
                                                updateActuationData(1);
                                                setShowFilters(false);
                                            }}>
                                            Apply
                                        </Button>
                                    </Modal.Body>
                                </Modal>
                                <ActuationsMobileList
                                    actuations={actuations}
                                    currentPage={currentPage}
                                    totalPages={totalPages}
                                    onPageChange={updateActuationData}
                                />

                            </Container>
                        )}
                    </>
                )}

            </Container>
        </div>
    );
};

export default ActuationEvents;

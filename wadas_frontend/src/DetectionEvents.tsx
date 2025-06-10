import * as React from "react";
import {useEffect, useState} from "react";
import {Alert, Button, Col, Container, Modal, Row} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import CustomNavbar from "./components/CustomNavbar";
import Select, {MultiValue} from "react-select";
import DatePick from "./components/DatePick";
import {isMobile, tryWithRefreshing} from "./lib/utils";
import DetectionsScrollableTable from "./components/DetectionsScrollableTable";
import DetectionsMobileList from "./components/DetectionsMobileList";
import {useLocation, useNavigate} from 'react-router-dom';
import CustomSpinner from "./components/CustomSpinner";
import {Camera, DetectionEvent, DetectionEventResponse} from "./types/types";
import {fetchAnimalsNames, fetchCameras, fetchDetectionEvents, fetchExportDetectionEvents} from "./lib/api";
import EventDetails from "./EventDetails";


type CameraOption = {
    value: string;
    label: string;
}

type AnimalOption = {
    value: string;
    label: string;
}

const DetectionEvents = () => {
    const pageSize = 20;
    const location = useLocation();
    const [showFilters, setShowFilters] = useState(false);
    const [prevClickedCamera, setPrevClickedCamera] = useState(null);
    const [optionsCameras, setOptionsCameras] = useState<CameraOption[]>([]);
    const [optionsAnimals, setOptionsAnimals] = useState<AnimalOption[]>([]);
    const [cameras, setCameras] = useState<Camera[]>([]);
    const [detections, setDetections] = useState<DetectionEvent[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [exportLoading, setExportLoading] = useState<boolean>(false);
    const [selectedCameras, setSelectedCameras] = useState<MultiValue<CameraOption>>([]);
    const [selectedAnimals, setSelectedAnimals] = useState<MultiValue<AnimalOption>>([]);
    const [error, setError] = useState<string | null>(null);
    const [exportError, setExportError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const navigate = useNavigate();
    const [startDate, setStartDate] = useState<Date | null>(null);
    const [endDate, setEndDate] = useState<Date | null>(null);
    const [currentEvent, setCurrentEvent] = useState<DetectionEvent | null>(null)
    const [mobileFlag, setMobileFlag] = useState(isMobile());


    const updateDateRange = (dates: [Date | null, Date | null]) => {
        const [start, end] = dates;
        setStartDate(start);
        setEndDate(end);
    };

    const updateDetectionData = async (page = 1) => {
        try {
            const offset = (page - 1) * pageSize;
            const detectionsResponse: DetectionEventResponse = await tryWithRefreshing(() =>
                fetchDetectionEvents(
                    offset,
                    selectedCameras.map(cam => cam.value),
                    selectedAnimals.map(animal => animal.value),
                    startDate,
                    endDate
                )
            );
            setDetections(detectionsResponse.data)
            setTotalPages(Math.ceil(detectionsResponse.total / pageSize));
            setCurrentPage(page);
            setCurrentEvent(null);
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


    const handleChangeCameras = (selected: MultiValue<CameraOption>) => {
        setSelectedCameras(selected);
    };

    const handleChangeAnimals = (selected: MultiValue<AnimalOption>) => {
        setSelectedAnimals(selected);
    };


    const exportResults = () => async () => {
        setExportLoading(true);
        try {
            const responseBlob: Blob = await tryWithRefreshing(() =>
                fetchExportDetectionEvents(
                    selectedCameras.map(cam => cam.value),
                    selectedAnimals.map(animal => animal.value),
                    startDate,
                    endDate
                )
            );

            const url = window.URL.createObjectURL(responseBlob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "detection_events.csv";
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

    const showDetails = (event: DetectionEvent) => {
        setCurrentEvent(event);
    }

    const resetSelectedEvent = (): void => {
        setCurrentEvent(null);
    }

    useEffect(() => {
        if (location.state?.selectedCamera) {
            const clickedCamera = location.state?.selectedCamera;
            setPrevClickedCamera(clickedCamera);
            setSelectedCameras([{value: clickedCamera.id.toString(), label: clickedCamera.name}]);
            location.state.selectedCamera = null;
        }

        const loadFiltersData = async () => {
            try {
                const [camerasResponse, animalsResponse] = await Promise.all([
                    tryWithRefreshing(fetchCameras),
                    tryWithRefreshing(fetchAnimalsNames),
                ]);

                setOptionsCameras(camerasResponse.data.map(cam => ({value: cam.id.toString(), label: cam.name})));
                setCameras(camerasResponse.data);
                setOptionsAnimals(animalsResponse.data.map(animal => ({value: animal, label: animal})));
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

        loadFiltersData();
        updateDetectionData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [prevClickedCamera]);

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
                                <Container style={{height: "45vh", display: "flex", flexDirection: "column"}}>
                                    <Container className="mt-3">
                                        <Row className="mb-3">
                                            <Col md={3}>
                                                <Select
                                                    id="multi-select"
                                                    isMulti
                                                    options={optionsCameras}
                                                    value={selectedCameras}
                                                    onChange={handleChangeCameras}
                                                    placeholder={<div className={"custom-placeholder"}>select
                                                        cameras...</div>}
                                                />
                                            </Col>
                                            <Col md={3}>
                                                <Select
                                                    id="multi-select"
                                                    isMulti
                                                    options={optionsAnimals}
                                                    value={selectedAnimals}
                                                    onChange={handleChangeAnimals}
                                                    placeholder={<div className={"custom-placeholder"}>select
                                                        animals...</div>}
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
                                                    onClick={() => updateDetectionData(1)}>
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
                                        <DetectionsScrollableTable
                                            detections={detections}
                                            knownCameras={cameras}
                                            currentPage={currentPage}
                                            totalPages={totalPages}
                                            onPageChange={updateDetectionData}
                                            onRowSelected={showDetails}
                                        />
                                    </Container>
                                </Container>

                                <Container className="my-2">
                                    <hr/>
                                </Container>

                                {/*Event Details*/}
                                <Container style={{height: "40vh"}}>
                                    {currentEvent === null ? (
                                        <Container style={{paddingLeft: "24px"}}>
                                            <Row className={"d-none d-lg-flex"}>
                                                <Col md={6} className="position-relative">
                                                    <h5>No event selected</h5>
                                                </Col>
                                            </Row>
                                        </Container>
                                    ) : (
                                        <EventDetails currentEvent={currentEvent} cameras={cameras}
                                                      onOffcanvasClose={null}/>
                                    )}

                                </Container>
                            </Container>

                        ) : (
                            // Mobile view
                            <Container>
                                <Row className="mb-3 mt-3 d-flex align-items-center">
                                    <Col xs={8}>
                                        <h3>Detection Events</h3>
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
                                            isMulti
                                            options={optionsCameras}
                                            value={selectedCameras}
                                            onChange={setSelectedCameras}
                                            placeholder={<div className={"custom-placeholder"}>select
                                                cameras...</div>}
                                        />
                                        <Select
                                            isMulti
                                            options={optionsAnimals}
                                            value={selectedAnimals}
                                            onChange={setSelectedAnimals}
                                            placeholder={<div className={"custom-placeholder"}>select
                                                animals...</div>}
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
                                                updateDetectionData(1);
                                                setShowFilters(false);
                                            }}>
                                            Apply
                                        </Button>
                                    </Modal.Body>
                                </Modal>
                                <DetectionsMobileList
                                    detections={detections}
                                    knownCameras={cameras}
                                    currentPage={currentPage}
                                    totalPages={totalPages}
                                    onPageChange={updateDetectionData}
                                    onCardSelected={showDetails}
                                    selectedEventId={currentEvent?.id}
                                />

                                {currentEvent !== null ? (
                                    <EventDetails currentEvent={currentEvent} cameras={cameras}
                                                  onOffcanvasClose={resetSelectedEvent}/>
                                ) : (
                                    <></>
                                )}

                            </Container>
                        )}
                    </>
                )}
            </Container>

        </div>
    );
};

export default DetectionEvents;

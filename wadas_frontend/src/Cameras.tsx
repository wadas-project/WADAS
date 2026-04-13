import * as React from "react";
import {useEffect, useState} from "react";
import {Alert, Col, Container, Row} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import CustomNavbar from "./components/CustomNavbar";
import CameraCard from "./components/CameraCard";
import {Camera, CamerasResponse} from "./types/types";
import {useNavigate} from 'react-router-dom';
import {getErrorMessage, isUnauthorizedError, tryWithRefreshing} from './lib/utils';
import CustomSpinner from "./components/CustomSpinner";
import {fetchCameras} from "./lib/api";
import ActuatorsModal from "./components/ActuatorsModal";
import { useErrorModal } from "./components/ErrorModal";


const Cameras = () => {

    const [cameras, setCameras] = useState<Camera[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [loadFailed, setLoadFailed] = useState<boolean>(false);
    const [showActuatorsModal, setShowActuatorsModal] = useState<boolean>(false);
    const [clickedCamera, setClickedCamera] = useState<Camera | null>(null);
    const navigate = useNavigate();
    const { showError } = useErrorModal();


    const handleActuatorsClick = (camera: Camera) => {
        setClickedCamera(camera);
        setShowActuatorsModal(true);
    };

    useEffect(() => {
        const loadPage = async () => {
            try {
                const cameraResponse: CamerasResponse = await tryWithRefreshing(fetchCameras);
                setCameras(cameraResponse.data);
                setLoading(false);
            } catch (e) {
                if (isUnauthorizedError(e)) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    setLoadFailed(true);
                    showError(getErrorMessage(e), "Unable to load cameras");
                    setLoading(false);
                }
            }
        };
        loadPage();
    }, [navigate, showError]);

    return (
        <div className={"padded-div"}>
            <CustomNavbar/>

            <Container className="mt-1">
                {loading ? (
                    <CustomSpinner/>
                ) : loadFailed ? (
                    <Alert variant="secondary" className="text-center">Unable to load cameras</Alert>
                ) : cameras !== null && cameras !== undefined && cameras.length === 0 ? (
                    <Alert variant="warning" className="text-center">No Enabled Camera found</Alert>
                ) : (
                    <Row>
                        {cameras.map((camera, index) => (
                            <Col md={4} className="mb-4" key={index}>
                                <CameraCard camera={camera} onActuatorsClick={handleActuatorsClick}/>
                            </Col>
                        ))}
                    </Row>
                )}
            </Container>
            <ActuatorsModal camera={clickedCamera}
                            show={showActuatorsModal}
                            onHide={() => setShowActuatorsModal(false)}>
            </ActuatorsModal>
        </div>
    );
};

export default Cameras;

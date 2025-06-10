import * as React from "react";
import {useEffect, useState} from "react";
import {Alert, Col, Container, Row} from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import CustomNavbar from "./components/CustomNavbar";
import CameraCard from "./components/CameraCard";
import {Camera, CamerasResponse} from "./types/types";
import {useNavigate} from 'react-router-dom';
import {tryWithRefreshing} from './lib/utils';
import CustomSpinner from "./components/CustomSpinner";
import {fetchCameras} from "./lib/api";
import ActuatorsModal from "./components/ActuatorsModal";


const Cameras = () => {

    const [cameras, setCameras] = useState<Camera[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [showActuatorsModal, setShowActuatorsModal] = useState<boolean>(false);
    const [clickedCamera, setClickedCamera] = useState<Camera | null>(null);
    const navigate = useNavigate();


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
                if (e instanceof Error && e.message.includes("Unauthorized")) {
                    console.error("Refresh token failed, redirecting to login...");
                    navigate("/");
                } else {
                    setError(`Generic Error - ${e.message}. Please contact the administrator.`);
                    setLoading(false);
                }
            }
        };
        loadPage();
    }, []);

    return (
        <div className={"padded-div"}>
            <CustomNavbar/>

            <Container className="mt-1">
                {loading ? (
                    <CustomSpinner/>
                ) : error ? (
                    <Alert variant="danger">{error}</Alert>
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

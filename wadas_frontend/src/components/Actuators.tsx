import React from "react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { tryWithRefreshing } from "../lib/utils";
import { fetchActuators } from "../lib/api";
import { Actuator, ActuatorsResponse } from "../types/types";
import CustomNavbar from "./CustomNavbar";
import { Alert, Col, Container, Row } from "react-bootstrap";
import CustomSpinner from "./CustomSpinner";
import CameraCard from "./CameraCard";
import ActuatorCard from "./ActuatorCard";



const Actuators = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actuators, setActuators] = useState<Actuator[]>([]);

  useEffect(() => {
    const loadPage = async () => {
      try {
        const actuatorsResponse: ActuatorsResponse = await tryWithRefreshing(fetchActuators);
        setActuators(actuatorsResponse.data);
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
                ) : actuators !== null && actuators !== undefined && actuators.length === 0 ? (
                    <Alert variant="warning" className="text-center">No Enabled Camera found</Alert>
                ) : (
                    <Row>
                        {actuators.map((actuator, index) => (
                            <Col md={4} className="mb-4" key={index}>
                                <ActuatorCard actuator={actuator} />
                            </Col>
                        ))}
                    </Row>
                )}
            </Container>
    </div>
  );
};

export default Actuators;

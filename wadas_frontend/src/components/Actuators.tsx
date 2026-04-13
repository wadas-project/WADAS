import React from "react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getErrorMessage, isUnauthorizedError, tryWithRefreshing } from "../lib/utils";
import { fetchActuators } from "../lib/api";
import { Actuator, ActuatorsResponse } from "../types/types";
import CustomNavbar from "./CustomNavbar";
import { Alert, Col, Container, Row } from "react-bootstrap";
import CustomSpinner from "./CustomSpinner";
import ActuatorCard from "./ActuatorCard";
import { useErrorModal } from "./ErrorModal";



const Actuators = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(true);
  const [loadFailed, setLoadFailed] = useState<boolean>(false);
  const [actuators, setActuators] = useState<Actuator[]>([]);
  const { showError } = useErrorModal();

  useEffect(() => {
    const loadPage = async () => {
      try {
        console.log('fetch')
        const actuatorsResponse: ActuatorsResponse = await tryWithRefreshing(fetchActuators);
        setActuators(actuatorsResponse.data);
        setLoading(false);
      } catch (e) {
        if (isUnauthorizedError(e)) {
          console.error("Refresh token failed, redirecting to login...");
          navigate("/");
        } else {
          setLoadFailed(true);
          showError(getErrorMessage(e), "Unable to load actuators");
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
                    <Alert variant="secondary" className="text-center">Unable to load actuators</Alert>
                ) : actuators !== null && actuators !== undefined && actuators.length === 0 ? (
                    <Alert variant="warning" className="text-center">No Enabled Actuators found</Alert>
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

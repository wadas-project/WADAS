import * as React from 'react';
import { Badge, Button, Card } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import "../styles/App.css"
import { Actuator } from "../types/types";
import { useNavigate } from "react-router-dom";

const ActuatorCard = (props: { actuator: Actuator }) => {
  const navigate = useNavigate();

  const handleDetailClick = () => {
    navigate(`/actuator/${props.actuator.id}`);
  };

  return (
    <Card className="h-100 thin-solid-grey-border m-3">
      <Card.Body className="d-flex flex-column" style={{ padding: "1.7rem" }}>
        <Card.Title className="d-flex flex-column mb-4">

          <span className="d-block mb-2" style={{ fontSize: "1.10rem" }}>
            {props.actuator.id}
          </span>

          <span className="d-block card-subtitle">
            Actuator Type: {props.actuator.type}
          </span>

          <span className="d-block card-subtitle">
            Last Update:{" "}
            {props.actuator.last_update
              ? new Date(props.actuator.last_update).toLocaleString("it-IT")
              : "N/A"}
          </span>

        </Card.Title>
        <div className="d-flex justify-content-end mt-auto">
          <Button
              variant="primary"
              className="custom-button dark-background"
              onClick={handleDetailClick}
          >
            Detail
          </Button>
        </div>
      </Card.Body>
    </Card>
  );
};

export default ActuatorCard;

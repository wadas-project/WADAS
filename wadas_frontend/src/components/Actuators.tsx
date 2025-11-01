import React from "react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { tryWithRefreshing } from "../lib/utils";
import { fetchActuators } from "../lib/api";
import { Actuator, ActuatorsResponse } from "../types/types";



const Actuators = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [actuators, setActuators] = useState<Actuator[] | null>(null);

  useEffect(() => {
    const loadPage = async () => {
      try {
        const actuatorsResponse: ActuatorsResponse = await tryWithRefreshing(fetchActuators);
        setActuators(actuatorsResponse.data);
        console.log(actuators)
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
    <div>
      <h1>Actuators</h1>
      <p>Componente base pronto per essere esteso.</p>
    </div>
  );
};

export default Actuators;

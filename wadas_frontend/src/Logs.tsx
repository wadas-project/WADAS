import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { Container } from "react-bootstrap";
import "bootstrap/dist/css/bootstrap.min.css";
import CustomNavbar from "./components/CustomNavbar";
import { fetchLogs } from "./lib/api";
import { getErrorMessage, isUnauthorizedError, tryWithRefreshing } from "./lib/utils";
import { useNavigate } from "react-router-dom";
import { useErrorModal } from "./components/ErrorModal";

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const hasShownErrorRef = useRef(false);
  const navigate = useNavigate();
  const { showError } = useErrorModal();

  // Fetch logs every second
  useEffect(() => {
    const fetchLogsData = async () => {
      try {
        const response = await tryWithRefreshing(fetchLogs);
        const newLogs = Array.isArray(response.data) ? response.data : [];
        setLogs(newLogs);
        hasShownErrorRef.current = false;
      } catch (err) {
        if (isUnauthorizedError(err)) {
          navigate("/");
          return;
        }

        if (!hasShownErrorRef.current) {
          showError(getErrorMessage(err), "Unable to load application logs");
          hasShownErrorRef.current = true;
        }
      }
    };

    fetchLogsData(); // initial fetch
    const interval = setInterval(fetchLogsData, 1000);

    return () => clearInterval(interval);
  }, [navigate, showError]);

  return (
    <div className="padded-div">
      <CustomNavbar />

      <Container className="mt-4">
        <h1 className="text-xl sm:text-2xl font-semibold mb-4">WADAS App log</h1>
        <pre
          className="whitespace-pre-wrap break-words bg-gray-100 p-4 rounded max-h-[70vh] overflow-y-auto w-full text-sm sm:text-base
                     sm:p-6 sm:text-base sm:rounded-lg"
        >
          {logs.join("\n")}
        </pre>
      </Container>
    </div>
  );
};

export default Logs;

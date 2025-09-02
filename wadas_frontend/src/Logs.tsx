import { useEffect, useState } from "react";
import { Container, Card, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import CustomNavbar from "./components/CustomNavbar";
import CustomSpinner from "./components/CustomSpinner";
import { fetchLogs } from "./lib/api";
import { tryWithRefreshing } from "./lib/utils";

const Logs = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const role = localStorage.getItem("role");

    // If not Admin role, redirect to login
    if (!token || role !== "Admin") {
      localStorage.clear();
      navigate("/");
      return;
    }

    const loadLogs = async () => {
      try {
        const result = await tryWithRefreshing(fetchLogs);
        setLogs(result || []);
        setLoading(false);
      } catch (err: any) {
          console.error("Error detail:", err);

          const backendMessage = err.response?.data?.detail;
          const friendlyMessage = backendMessage || err.message || "Unknown Error";

          setError(friendlyMessage);
          setLoading(false);
        }
    };

    loadLogs();
  }, [navigate]);

  return (
    <div className="padded-div">
      <CustomNavbar />

      <Container className="p-4">
        <h1 className="mb-3">Server Logs</h1>

        {loading ? (
          <CustomSpinner />
        ) : error ? (
          <Alert variant="danger">Error: {error}</Alert>
        ) : (
          <Card className="bg-black text-green-400 font-mono max-h-[600px] overflow-y-auto">
            <Card.Body style={{ whiteSpace: "pre-wrap" }}>
              {logs.map((line, i) => (
                <div key={i}>{line}</div>
              ))}
            </Card.Body>
          </Card>
        )}
      </Container>
    </div>
  );
};

export default Logs;

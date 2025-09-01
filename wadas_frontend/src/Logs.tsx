import { useEffect, useState } from "react";
import { Container, Card, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { baseUrl } from "./config";

const Logs = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    const role = localStorage.getItem("role");

    if (!token || role !== "Administrator") {
      localStorage.clear();
      navigate("/"); // redirect se non admin
      return;
    }

    const fetchLogs = async () => {
      try {
        const res = await fetch(baseUrl + "api/v1/logs", {
          headers: { "x-access-token": token },
        });

        if (!res.ok) throw new Error(await res.text());

        const data = await res.json();
        setLogs(data.data);
      } catch (err: any) {
        setError(err.message);
      }
    };

    fetchLogs();
  }, [navigate]);

  if (error) return <Alert variant="danger">Errore: {error}</Alert>;

  return (
    <Container className="p-4">
      <h1 className="mb-3">Server Logs</h1>
      <Card className="bg-black text-green-400 font-mono max-h-[600px] overflow-y-auto">
        <Card.Body style={{ whiteSpace: "pre-wrap" }}>
          {logs.map((line, i) => (
            <div key={i}>{line}</div>
          ))}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Logs;

import { useEffect, useState } from "react";

export default function Logs() {
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchLogs = async () => {
    try {
      const token = localStorage.getItem("accessToken");
      const res = await fetch("/api/v1/logs", {
        headers: { "x-access-token": token ?? "" },
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const json = await res.json();

      if (Array.isArray(json.data)) {
        // ✅ aggiorna solo se i log sono cambiati
        if (JSON.stringify(json.data) !== JSON.stringify(logs)) {
          setLogs(json.data);
        }
      } else {
        throw new Error("Formato logs non valido");
      }
    } catch (err: any) {
      console.error("Fetch logs failed:", err);
      setError("Impossibile recuperare i log.");
    }
  };

  useEffect(() => {
    // prima fetch subito
    fetchLogs();

    // poi ogni 1 secondo
    const interval = setInterval(fetchLogs, 1000);
    return () => clearInterval(interval);
  }, [logs]); // attenzione alla dipendenza

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-4">Logs</h1>
      {error && <p className="text-red-500">{error}</p>}
      <pre className="whitespace-pre-wrap bg-gray-100 p-4 rounded max-h-[70vh] overflow-y-auto">
        {logs.join("\n")}
      </pre>
    </div>
  );
}

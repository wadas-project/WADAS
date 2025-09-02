import * as React from "react";
import { useEffect, useState } from "react";
import { fetchLogs } from "./lib/api";

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);

  // Fetch logs every second
  useEffect(() => {
    const fetchLogsData = async () => {
      try {
        const response = await fetchLogs(); // { data: [...] }
        const newLogs = Array.isArray(response.data) ? response.data : [];
        setLogs(newLogs);
      } catch (err) {
        console.error("Fetch logs failed:", err);
      }
    };

    fetchLogsData(); // initial fetch
    const interval = setInterval(fetchLogsData, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-xl sm:text-2xl font-semibold mb-4">WADAS App log</h1>
      <pre
        className="whitespace-pre-wrap break-words bg-gray-100 p-4 rounded max-h-[70vh] overflow-y-auto w-full text-sm sm:text-base
                   sm:p-6 sm:text-base sm:rounded-lg"
      >
        {logs.join("\n")}
      </pre>
    </div>
  );
};

export default Logs;

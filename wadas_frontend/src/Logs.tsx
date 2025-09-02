import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { fetchLogs } from "./lib/api";

const Logs: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const containerRef = useRef<HTMLPreElement | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);
  const [isAtBottom, setIsAtBottom] = useState(true);

  // Fetch logs every second
  useEffect(() => {
    const fetchLogsData = async () => {
      try {
        const response = await fetchLogs(); // response is { data: [...] }
        const newLogs = Array.isArray(response.data) ? response.data : [];

        // update logs
        setLogs(newLogs);
      } catch (err) {
        console.error("Fetch logs failed:", err);
      }
    };

    fetchLogsData(); // initial fetch
    const interval = setInterval(fetchLogsData, 1000);

    return () => clearInterval(interval);
  }, []);

  // Handle auto-scroll
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    if (isAtBottom) {
      logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, isAtBottom]);

  // Track user's scroll position
  const handleScroll = () => {
    const container = containerRef.current;
    if (!container) return;

    const atBottom =
      container.scrollHeight - container.scrollTop - container.clientHeight < 10;
    setIsAtBottom(atBottom);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl sm:text-2xl font-semibold mb-4">WADAS App log</h1>
      <pre
        ref={containerRef}
        onScroll={handleScroll}
        className="whitespace-pre-wrap break-words bg-gray-100 p-4 rounded max-h-[70vh] overflow-y-auto w-full text-sm sm:text-base"
      >
        {logs.join("\n")}
        <div ref={logsEndRef} />
      </pre>
    </div>
  );
};

export default Logs;

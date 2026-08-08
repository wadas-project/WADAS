import { useEffect, useState } from "react";
import { ButtonGroup, ToggleButton } from "react-bootstrap";
import {
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import CustomSpinner from "./CustomSpinner";
import { fetchActuatorTemperatureHistory } from "../lib/api";
import { getErrorMessage, isUnauthorizedError, tryWithRefreshing } from "../lib/utils";
import { BatteryHistoryRange } from "../types/types";
import { useErrorModal } from "./ErrorModal";
import { useNavigate } from "react-router-dom";

const RANGE_OPTIONS: { value: BatteryHistoryRange; label: string }[] = [
    { value: "1d", label: "24h" },
    { value: "7d", label: "1 week" },
    { value: "30d", label: "1 month" },
    { value: "90d", label: "3 months" },
];

interface ChartPoint {
    timestamp: number;
    actuatorTemperature: number | null;
    batteryTemperature: number | null;
}

// Merges two independently-sampled time series (actuator sensor, battery sensor)
// into a single array of points sorted by timestamp, as required by recharts
// for a shared numeric X axis. Points from each series keep null on the other
// series' key where there is no matching reading, and Line's `connectNulls`
// draws through the gaps.
const mergeSeries = (
    actuator: { temperature: number | null; timestamp: string }[],
    battery: { temperature: number | null; timestamp: string }[]
): ChartPoint[] => {
    const byTimestamp = new Map<number, ChartPoint>();

    for (const reading of actuator) {
        const ts = new Date(reading.timestamp).getTime();
        const existing = byTimestamp.get(ts);
        if (existing) {
            existing.actuatorTemperature = reading.temperature;
        } else {
            byTimestamp.set(ts, {
                timestamp: ts,
                actuatorTemperature: reading.temperature,
                batteryTemperature: null,
            });
        }
    }

    for (const reading of battery) {
        const ts = new Date(reading.timestamp).getTime();
        const existing = byTimestamp.get(ts);
        if (existing) {
            existing.batteryTemperature = reading.temperature;
        } else {
            byTimestamp.set(ts, {
                timestamp: ts,
                actuatorTemperature: null,
                batteryTemperature: reading.temperature,
            });
        }
    }

    return Array.from(byTimestamp.values()).sort((a, b) => a.timestamp - b.timestamp);
};

const TemperatureHistoryChart = (props: { actuatorId: string }) => {
    const { actuatorId } = props;
    const navigate = useNavigate();
    const { showError } = useErrorModal();

    const [range, setRange] = useState<BatteryHistoryRange>("7d");
    const [points, setPoints] = useState<ChartPoint[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        let cancelled = false;

        const loadHistory = async () => {
            setLoading(true);
            try {
                const response = await tryWithRefreshing(() =>
                    fetchActuatorTemperatureHistory(actuatorId, range)
                );

                if (cancelled) {
                    return;
                }

                setPoints(mergeSeries(response.actuator, response.battery));
            } catch (e) {
                if (cancelled) {
                    return;
                }

                if (isUnauthorizedError(e)) {
                    navigate("/");
                    return;
                }

                showError(getErrorMessage(e), "Unable to load temperature history");
            } finally {
                if (!cancelled) {
                    setLoading(false);
                }
            }
        };

        loadHistory();

        return () => {
            cancelled = true;
        };
    }, [actuatorId, range, navigate, showError]);

    const formatTick = (value: number): string => {
        const date = new Date(value);
        return range === "1d" || range === "7d"
            ? date.toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit" }) +
                  " " +
                  date.toLocaleTimeString("it-IT", { hour: "2-digit", minute: "2-digit" })
            : date.toLocaleDateString("it-IT", { day: "2-digit", month: "2-digit" });
    };

    return (
        <div>
            <div className="d-flex justify-content-between align-items-center mb-2">
                <h6 className="mb-0">Temperature</h6>
                <ButtonGroup size="sm">
                    {RANGE_OPTIONS.map((option) => (
                        <ToggleButton
                            key={option.value}
                            id={`temperature-range-${option.value}`}
                            type="radio"
                            variant="outline-secondary"
                            name="temperature-range"
                            value={option.value}
                            checked={range === option.value}
                            onChange={() => setRange(option.value)}
                        >
                            {option.label}
                        </ToggleButton>
                    ))}
                </ButtonGroup>
            </div>

            <div className="border p-3" style={{ backgroundColor: "#f8f9fa" }}>
                {loading ? (
                    <div className="d-flex justify-content-center py-4">
                        <CustomSpinner />
                    </div>
                ) : points.length === 0 ? (
                    <div className="text-muted text-center py-4">
                        No temperature data available for this period
                    </div>
                ) : (
                    <ResponsiveContainer width="100%" height={260}>
                        <LineChart data={points} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis
                                dataKey="timestamp"
                                type="number"
                                domain={["dataMin", "dataMax"]}
                                tickFormatter={formatTick}
                                minTickGap={40}
                            />
                            <YAxis domain={["auto", "auto"]} unit="°C" width={60} />
                            <Tooltip
                                labelFormatter={(value) => new Date(value as number).toLocaleString("it-IT")}
                                formatter={(value: number, name: string) => [
                                    `${value.toFixed(1)} °C`,
                                    name,
                                ]}
                            />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="actuatorTemperature"
                                name="Actuator"
                                stroke="#dc3545"
                                dot={false}
                                connectNulls
                                isAnimationActive={false}
                            />
                            <Line
                                type="monotone"
                                dataKey="batteryTemperature"
                                name="Battery"
                                stroke="#fd7e14"
                                dot={false}
                                connectNulls
                                isAnimationActive={false}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                )}
            </div>
        </div>
    );
};

export default TemperatureHistoryChart;

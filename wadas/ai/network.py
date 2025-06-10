#!/usr/bin/env python3
"""
monitor_net_prom_min.py – esporta su http://localhost:8003/metrics

    network_rx_bytes_per_second  ↘
    network_tx_bytes_per_second  ↗
"""

from __future__ import annotations
import time
import psutil
from prometheus_client import Gauge, start_http_server

# ----- CONFIG -----
IFACE = "wlp0s20f3"     # interfaccia da monitorare
PORTA_METRICHE = 8004  # porta per /metrics
SAMPLING_PERIOD = 1.0   # secondi
# -------------------

# Gauge Prometheus (con una label facoltativa “iface”)
rx_metric = Gauge(
    "network_rx_bytes_per_second",
    "Byte ricevuti al secondo",
    labelnames=("iface",),
)
tx_metric = Gauge(
    "network_tx_bytes_per_second",
    "Byte trasmessi al secondo",
    labelnames=("iface",),
)


# Variabili di stato per il calcolo del delta
_precedente = psutil.net_io_counters(pernic=True)[IFACE]
_prev_time = time.time()


def calcolo_net_bytes() -> tuple[float, float]:
    """Calcola Byte/s RX e TX rispetto alla misurazione precedente, aggiorna i Gauge."""
    global _precedente, _prev_time

    corrente = psutil.net_io_counters(pernic=True)[IFACE]
    adesso = time.time()
    dt = adesso - _prev_time if adesso > _prev_time else 1.0  # evita div. per 0

    rx_Bps = (corrente.bytes_recv - _precedente.bytes_recv) / dt
    tx_Bps = (corrente.bytes_sent - _precedente.bytes_sent) / dt

    # Aggiorna i Gauge
    rx_metric.labels(iface=IFACE).set(rx_Bps)
    tx_metric.labels(iface=IFACE).set(tx_Bps)

    # Debug a console
    print(f"RX={rx_Bps:.0f} B/s  TX={tx_Bps:.0f} B/s")

    # Salva stato per la prossima iterazione
    _precedente, _prev_time = corrente, adesso

    return rx_Bps, tx_Bps


def expose_metrics():
    """Avvio server HTTP per esporre le metriche e le aggiorno in loop."""
    start_http_server(PORTA_METRICHE)
    print(f"Server metriche avviato sulla porta {PORTA_METRICHE} …")
    while True:
        print(f"porta{PORTA_METRICHE} ----- {calcolo_net_bytes()}")
        time.sleep(SAMPLING_PERIOD)


# ---- main ----
if __name__ == "__main__":
    while True:
        expose_metrics()

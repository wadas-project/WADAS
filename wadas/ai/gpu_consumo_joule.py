from prometheus_client import Gauge, start_http_server
import subprocess
import re
import time

# Metrica Prometheus per potenza GPU in Watt
gpu_power_metric = Gauge('gpu_power_watt', 'Potenza media consumata dalla GPU in Watt', ['device'])

SAMPLING_PERIOD = 2  # intervallo di misura in secondi

def read_gpu_power_joules():
    """
    Esegue 'perf stat' per misurare il consumo energetico della GPU in Joule.
    Restituisce il valore float di Joule consumati nell'intervallo SAMPLING_PERIOD.
    """
    try:
        cmd = ["sudo", "perf", "stat", "-a", "-e", "power/energy-gpu/", "sleep", str(SAMPLING_PERIOD)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        stderr_output = result.stderr
        match = re.search(r'([\d.,]+)\s+Joules\s+power/energy-gpu/', stderr_output)
        if match:
            joules_str = match.group(1).replace(',', '.')
            joules = float(joules_str)
            return joules
        else:
            print("Errore: valore Joules non trovato nell'output di perf")
            return 0.0
    except Exception as e:
        print(f"Errore durante la lettura del consumo energetico GPU: {e}")
        return 0.0

def expose_metrics():
    start_http_server(8002)
    print("Server Prometheus avviato sulla porta 8002")
    while True:
        joules = read_gpu_power_joules()
        watt = joules / SAMPLING_PERIOD  # Conversione Joules -> Watt
        print(f"Potenza media GPU: {watt:.6f} Watt (energia {joules:.6f} Joules in {SAMPLING_PERIOD}s)")
        gpu_power_metric.labels(device="gpu").set(watt)

if __name__ == "__main__":
    expose_metrics()

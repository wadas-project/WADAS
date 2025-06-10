from prometheus_client import Gauge, start_http_server
import time

# Path energia CPU via RAPL (Intel)
ENERGY_PATH = "/sys/class/powercap/intel-rapl:0/energy_uj"
SAMPLING_PERIOD = 2  # secondi

# Metrica Prometheus per potenza CPU in Watt
cpu_power_metric = Gauge('cpu_power_watt', 'Potenza media consumata dalla CPU in Watt', ['device'])

def read_energy():
    with open(ENERGY_PATH) as f:
        return int(f.read().strip())

def calculate_power():
    e1 = read_energy()
    time.sleep(SAMPLING_PERIOD)
    e2 = read_energy()
    delta_uj = e2 - e1

    # Gestione overflow contatore energia
    if delta_uj < 0:
        delta_uj += 2**32  # adattare a 2**64 se necessario

    joules = delta_uj / 1_000_000  # microjoule -> joule
    watt = joules / SAMPLING_PERIOD
    return watt

def expose_metrics():
    start_http_server(8002)  # Espone metrica su porta 8004
    print("Server Prometheus CPU avviato sulla porta 8004")
    while True:
        watt = calculate_power()
        print(f"Potenza media CPU: {watt:.6f} Watt")
        cpu_power_metric.labels(device="cpu").set(watt)

if __name__ == "__main__":
    expose_metrics()

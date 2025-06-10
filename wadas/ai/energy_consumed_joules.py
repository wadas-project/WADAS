from prometheus_client import Gauge, start_http_server
import time
import subprocess

# Metrica: energia totale consumata in Joule
energy_consumed_metric = Gauge('energy_consumed_joules', 'Energia consumata totale in joule (da powertop)', ['empty'])

SAMPLING_PERIOD = 2  # secondi

def read_energy_from_powertop():
    try:
        # Esegui powertop in modalità test di 1 secondo in CSV
        result = subprocess.run(
            ["sudo", "powertop", "--time=1", "--csv=/tmp/powertop.csv"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Cerca il valore in joule nel file CSV
        with open("/tmp/powertop.csv", "r") as f:
            for line in f:
                if "The energy consumed was" in line:
                    # Esempio: 'The energy consumed was 151 Joules'
                    parts = line.strip().split()
                    joules = float(parts[-2])  # penultimo elemento: 151
                    print(f"Energia letta da powertop: {joules} J")
                    return joules
                
    except Exception as e:
        print(f"Errore durante lettura energia da powertop: {e}")
        return 0.0

def calcolo_energia_joule():
    joules = read_energy_from_powertop()
    energy_consumed_metric.labels(empty="").set(joules)
    return joules

def expose_metrics():
    start_http_server(8003)
    print("Exporter Prometheus avviato sulla porta 8003...")
    while True:
        val = calcolo_energia_joule()
        print(f"[{time.strftime('%H:%M:%S')}] Energia totale: {val} J")
        time.sleep(SAMPLING_PERIOD)

if __name__ == "__main__":
    expose_metrics()

from prometheus_client import Gauge, start_http_server
import time

#npu_utilization_metric = Gauge('npu_utilization', 'Percentuale di utilizzo della NPU')
# Definiamo il Gauge CON UNA ETICHETTA fittizia "empty"
npu_utilization_metric = Gauge('npu_utilization', 'Percentuale di utilizzo della NPU', ['empty'])

NPU_BUSY_TIME_PATH = "/sys/devices/pci0000:00/0000:00:0b.0/npu_busy_time_us"
SAMPLING_PERIOD = 2  # 200 millisecondi



def read_npu_busy_time():
    with open(NPU_BUSY_TIME_PATH, "r") as f:
        return int(f.read().strip())

def calcolo_npu_percent():
    print("Calcolo utilizzo NPU...")
    time_1 = read_npu_busy_time()
    time.sleep(SAMPLING_PERIOD)
    time_2 = read_npu_busy_time()

    delta = time_2 - time_1
    utilization = 100 * delta/ (SAMPLING_PERIOD * 1_000_000)

    print(f"NPU Utilization: {utilization:.2f}%")   

    # Imposta l'etichetta vuota (valore stringa vuota)
    npu_utilization_metric.labels(empty="").set(utilization)
    #npu_utilization_metric.set(utilization)

    return utilization


def expose_metrics():
    """Avvia il server HTTP per esporre le metriche su una porta"""
    start_http_server(8000)  # Esponi le metriche sulla porta 8000
    print("Server di metrica avviato sulla porta 8000...")
    while True:
        print(f"porta{8000}-----{calcolo_npu_percent()}")  # Calcola l'utilizzo e aggiorna la metrica
        time.sleep(SAMPLING_PERIOD)  # Aspetta prima di ricalcolare



#expose_metrics()
if __name__=="__main__":
    while True:
        expose_metrics()
from prometheus_client import Gauge, start_http_server
import time

gpu_utilization_metric = Gauge('gpu_utilization', 'Percentuale di utilizzo della GPU', ['empty'])

GPU_BUSY_TIME_PATH = "/sys/class/drm/renderD128/device/power/runtime_active_time"
#"/sys/class/drm/renderD128/device/power/"

SAMPLING_PERIOD =  2

def read_active_time():
    with open(GPU_BUSY_TIME_PATH) as f:
        return int(f.read().strip())



  

def read_gpu_busy_time():
    while True:
        # Misura su intervallo di 1 secondo
        t1 = read_active_time()
        time.sleep(SAMPLING_PERIOD)
        t2 = read_active_time()

        delta = t2 -t1 # microsecondi attivi in 1 secondo
        percent = (delta/ (SAMPLING_PERIOD* 1000000))*100

        print(f"Utilizzo GPU (Compute) in questo secondo: {percent:.7f}%")
        return percent
    

def calcolo_gpu_percent():
    print("Calcolo utilizzo GPU...")
    usage = read_gpu_busy_time()

    print(f"GPU Utilization: {usage:.7f}%")

    gpu_utilization_metric.labels(empty="").set(usage)

    return usage


def expose_metrics():
    """Avvio server HTTP per esporre le metriche su una porta"""
    start_http_server(8002)  # Espongo le metriche sulla porta 8001
    print("Server di metrica avviato sulla porta 8001..")
    while True:
        print(f"porta{8002}-----{calcolo_gpu_percent()}")  # Calcola l'utilizzo e aggiorna la metrica
        #time.sleep(SAMPLING_PERIOD)  # Aspetta prima di ricalcolare



#expose_metrics()
if __name__=="__main__":
    while True:
        expose_metrics()
import ray
#from ray.util.metrics import Counter, Gauge

import requests
import re

ray.init(address='auto')

# #INFO SU TUTTI I NODI
# nodes = ray.nodes()
# for n in nodes:
#     print(f"Node ID: {n['NodeID']}")
#     print(f"Is Alive: {n['Alive']}")
#     print(f"Resources: {n['Resources']}")
#     print(f"Tags: {n['NodeManagerAddress']}")
#     print("-" * 40)
#     print(n)




# # URL del nodo head Ray (o localhost se esegui da lì)
# metrics_url = "http://localhost:8080/metrics"

# # Scarica tutte le metriche
# response = requests.get(metrics_url)
# metrics_text = response.text

# # Dizionari per memorizzare i valori
# metrics = {
#     "cpu_usage": {},
#     "cpu_count": {},
#     "gpus_utilization": {},
#     "disk_usage": {},
#     "mem_total": {},
#     "component_cpu_percentage": {},
#     "gram_used": {},
#     "network_send_speed": {},
#     "network_receive_speed": {}
# }

# import requests
# import re
# from collections import defaultdict

# # Lista di URL dei nodi Ray
# metrics_urls = [
#     "http://localhost:8080/metrics",  # Nodo head
#     #"http://localhost:8081/metrics",  # Worker 1
#     #http://localhost:8082/metrics",  # Worker 2
#     #"http://localhost:8083/metrics",  # Worker 3
# ]

# # Metriche target
# target_metrics = {
#     "ray_node_cpu_utilization",
#     "ray_node_cpu_count",
#     "ray_node_gpus_utilization",
#     "ray_node_disk_usage",
#     "ray_node_mem_total",
#     "ray_component_cpu_percentage",
#     "ray_node_gram_used",
#     "ray_node_network_send_speed",
#     "ray_node_network_receive_speed",
#     "ray_node_mem_used"
# }

# # Dizionario: metrica -> lista di tuple (sessione, ip, valore)
# metrics = defaultdict(list)

# # Cicla su tutti gli URL per raccogliere metriche da ogni nodo
# for url in metrics_urls:
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         metrics_text = response.text
#     except Exception as e:
#         print(f" Errore con {url}: {e}")
#         continue

#     for line in metrics_text.splitlines():
#         if line.startswith("#") or "{" not in line or "}" not in line:
#             continue

#         metric_match = re.match(r'^([a-zA-Z0-9_]+)\{', line)
#         if not metric_match:
#             continue

#         metric_name = metric_match.group(1)
#         if metric_name not in target_metrics:
#             continue

#         ip_match = re.search(r'ip="([^"]+)"', line)
#         session_match = re.search(r'SessionName="([^"]+)"', line)
#         value_match = re.search(r'}\s+([0-9\.eE\+\-]+)', line)

#         if ip_match and value_match and session_match:
#             ip = ip_match.group(1)
#             session = session_match.group(1)
#             value = float(value_match.group(1))
#             metrics[metric_name].append((session, ip, value))

# # Stampa i risultati
# print("\n Metriche raccolte per ogni nodo:")
# for metric_name in target_metrics:
#     print(f"\n🔹 Metrica: {metric_name}")
#     if metric_name in metrics:
#         for session, ip, value in metrics[metric_name]:
#             print(f"  - Sessione: {session}, IP: {ip}, Valore: {value}")
#     else:
#         print("   Nessun dato trovato.")


import requests
import re

# URL dei nodi Ray (aggiungi o modifica gli URL dei worker se necessario)
metrics_urls = [
    "http://localhost:8080/metrics",  # Nodo head
    # Aggiungi gli URL dei worker se necessario
    # "http://localhost:8081/metrics",  # Worker 1
     "http://localhost:8082/metrics",  # Worker 2
    # "http://localhost:8083/metrics",  # Worker 3
]

# Metriche target (queste sono le metriche che vogliamo raccogliere)
target_metrics = {
    "ray_node_cpu_utilization",
    "ray_node_cpu_count",
    "ray_node_gpus_utilization",
    "ray_node_disk_usage",
    "ray_node_mem_total",
    "ray_component_cpu_percentage",
    "ray_node_gram_used",
    "ray_node_network_send_speed",
    "ray_node_network_receive_speed",
    "ray_node_mem_used"
}

# Variabili per memorizzare i valori delle metriche
cpu_usage = 0  # Impostiamo direttamente a 0
cpu_count = 0
gpus_utilization = 0
disk_usage = 0
mem_total = 0
component_cpu_percentage = 0
gram_used = 0
network_send_speed = 0
network_receive_speed = 0
mem_used = 0
ip = None  # Sarà sempre lo stesso per tutte le metriche

# Cicla su tutti gli URL per raccogliere metriche da ogni nodo
for url in metrics_urls:
    try:
        response = requests.get(url)
        response.raise_for_status()
        metrics_text = response.text
    except Exception as e:
        print(f"Errore con {url}: {e}")
        continue

    # Analizza ogni riga di metriche
    for line in metrics_text.splitlines():
        if line.startswith("#") or "{" not in line or "}" not in line:
            continue  # Ignora le righe di commento o non valide

        metric_match = re.match(r'^([a-zA-Z0-9_]+)\{', line)
        if not metric_match:
            continue

        metric_name = metric_match.group(1)
        if metric_name not in target_metrics:
            continue  # Ignora le metriche che non ci interessano

        # Estrai l'IP, sessione e valore dalla riga
        ip_match = re.search(r'ip="([^"]+)"', line)
        session_match = re.search(r'SessionName="([^"]+)"', line)
        value_match = re.search(r'}\s+([0-9\.eE\+\-]+)', line)

        if ip_match and value_match and session_match:
            ip = ip_match.group(1)
            session = session_match.group(1)
            value = value_match.group(1)

            # Sostituisci "None" con 0 quando necessario
            value = float(value) if value else 0  # Converti il valore in float e gestisci None come 0

            # Assegna i valori alle variabili corrispondenti (impostando 0 se non ci sono valori)
            if metric_name == "ray_node_cpu_utilization":
                cpu_usage = value
            elif metric_name == "ray_node_cpu_count":
                cpu_count = value
            elif metric_name == "ray_node_gpus_utilization":
                gpus_utilization = value
            elif metric_name == "ray_node_disk_usage":
                disk_usage = value
            elif metric_name == "ray_node_mem_total":
                mem_total = value
            elif metric_name == "ray_component_cpu_percentage":
                component_cpu_percentage = value
            elif metric_name == "ray_node_gram_used":
                gram_used = value
            elif metric_name == "ray_node_network_send_speed":
                network_send_speed = value
            elif metric_name == "ray_node_network_receive_speed":
                network_receive_speed = value
            elif metric_name == "ray_node_mem_used":
                mem_used = value

# Funzioni di calcolo

def Compu_CPU(cpu_utilization, cpu_count):
    if cpu_count == 0:
        cpu_count = 1  # Imposta a 1 per evitare divisioni per 0
    return cpu_utilization / cpu_count

def Compu_GPU(ray_node_gpus_utilization, num_gpus):
    if num_gpus == 0:
        num_gpus = 1  # Imposta a 1 per evitare divisioni per 0
    return ray_node_gpus_utilization / num_gpus

def Compu_NPU(resources):
    return resources.get("NPU", 0)

def Computation(cpu_utilization, cpu_count, ray_node_gpus_utilization, num_gpus, resources):
    cpu_result = Compu_CPU(cpu_utilization, cpu_count)
    gpu_result = Compu_GPU(ray_node_gpus_utilization, num_gpus)
    npu_result = Compu_NPU(resources)
    total_computation = cpu_result + gpu_result + npu_result
    return total_computation

def Memory(ray_node_mem_total, ray_node_mem_used):
    if ray_node_mem_used == 0:
        ray_node_mem_used = 1  # Imposta a 1 per evitare divisioni per 0
    return ray_node_mem_total / ray_node_mem_used

def Bandwidth(ray_node_network_send_speed, ray_node_network_receive_speed):
    return ray_node_network_send_speed + ray_node_network_receive_speed

# Assicurati di definire 'num_gpus' e 'resources' prima di passare alle funzioni

#TO DO ORA................................................................................
num_gpus = 10  # DA RECUPERARE 
resources = {"NPU": 10}  # DA RECUPERARE
#costanti che variano a seconda del modello. (FORSE VANNO NEL FILE.YAML)
#Ipotizzo che a ogni modello viene preferito per uno USE CASE WADAS
#A=0.3 #Da precedenza al Computational Power -- 
#B=0.5 #Da precedenza al Memory_Capacity -- MONITORAGGIO
#C=0.2 #Da precendeza alla comunizazione -- SITUAZIONI CRITICHE
# Esegui i calcoli

computation_result = Computation(cpu_usage, cpu_count, gpus_utilization, num_gpus, resources)
memory_result = Memory(mem_total, mem_used)
bandwidth_result = Bandwidth(network_send_speed, network_receive_speed)

# Somma totale delle metriche
total_score = computation_result + memory_result + bandwidth_result
print(f"Punteggio totale: {total_score}")
    

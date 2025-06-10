import ray
import logging
import requests
import re
from abc import ABC, abstractmethod
from wadas.ai.npu_utilization import expose_metrics

logger = logging.getLogger(__name__)


#FORSE DA SPOSTARE IN .YAML
CONSUMO_CPU=4
CONSUMO_GPU=8
CONSUMO_NPU=2

ALPHA=0.7 #IMPORTANZA PER POWER CAPACITY in monitoring / upload bandwith in actuator
BETA=0.3 #IMPORTANZA PER MEMORIA in monitoring /download bandwith in actuator

class Scheduler(ABC):

    #def __init__(self):
    
    def find_nodes(self):
        "Metodo per scannerizzare i nodi nel cluster in base al detection_device e classification device"
        nodes = ray.nodes()

        nodi = {}  # Definisci il dizionario prima del ciclo

        for n in nodes:
            node_id = n["NodeID"]
            resources =n["Resources"]
            metric_port=n["MetricsExportPort"]
            node_ip = n["NodeManagerAddress"]

            print(f"Risorse del nodo!!!!!!!!!!!!!!!!!!!!!! ID:{node_id} IP:{node_ip} RISORSE:{resources}")

             # Aggiungi i dati al dizionario esistente
            nodi[node_id] = {
                "ip": node_ip,
                "metric_port": metric_port,
                "resources": resources
            }

        return nodi

    def url_to_metric(self, url, target_metrics):
        "Metodo per ricavare le metriche del nodo papabile"

        dict_metriche={}
        #dict_metriche["ray_node_gpus_utilization"]=100
        
        # Raccoglie le metriche del nodo dall' URL
        try:
            response = requests.get(url)
            response.raise_for_status()
            metrics_text = response.text
        except Exception as e:
            print(f"Errore con {url}: {e}")

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
            value_match = re.search(r'}\s+([0-9\.eE\+\-]+)', line)

            if value_match: 
                value = value_match.group(1)

                # Sostituisci "None" con 0 quando necessario
                value = float(value) if value else 0  # Converti il valore in float e gestisci None come 0

                # Assegna i valori alle variabili corrispondenti (impostando 0 se non ci sono valori)
                if metric_name == "ray_node_cpu_utilization":
                    cpu_usage = value
                    dict_metriche["ray_node_cpu_utilization"]=cpu_usage
                #elif metric_name == "ray_node_gpus_utilization":
                #    gpus_utilization = value
                #    dict_metriche["ray_node_gpus_utilization"]=gpus_utilization
                elif metric_name == "ray_node_mem_total":
                    mem_total = value
                    dict_metriche["ray_node_mem_total"]=mem_total
                elif metric_name == "ray_node_mem_used":
                    mem_used = value
                    dict_metriche["ray_node_mem_used"]=mem_used
                elif metric_name == "network_tx_bytes_per_second":
                    network_send_speed = value
                    dict_metriche["network_tx_bytes_per_second"]=network_send_speed
                elif metric_name == "network_rx_bytes_per_second":
                    network_receive_speed = value
                    dict_metriche["network_tx_bytes_per_second"]=network_receive_speed
                elif metric_name == "ray_node_disk_io_write_speed":
                    write_speed = value
                    dict_metriche["ray_node_disk_io_write_speed"]=write_speed
                elif metric_name == "ray_node_disk_io_read_speed":
                   read_speed = value
                   dict_metriche["ray_node_disk_io_read_speed"]=read_speed
                elif metric_name == 'npu_utilization':
                    npu_usage=value
                    dict_metriche["npu_utilization"]=npu_usage
                elif metric_name == 'gpu_utilization':
                    gpus_utilization = value
                    dict_metriche['gpu_utilization']=gpus_utilization

        return  dict_metriche
    
    @abstractmethod
    def best_nodes_det_class(self):
        "Metodo per ricavare l'id del nodo e device con score migliore per detection e classification"
        pass
        
class Monitoring_Scheduler(Scheduler):
    
    # Metriche target (queste sono le metriche che vogliamo raccogliere)
    target_metrics = {
            "ray_node_cpu_utilization",
            #"ray_node_gpus_utilization",
            "ray_node_mem_total",
            "ray_node_mem_used"
        }
    
    def best_nodes_det_class(self):
        
        id_url_detection={}
        npu_bool=False
        best_node_detection={}
        best_node_classification={}
        best_score=float("inf")
        id_url_classification={}
        nodi = self.find_nodes()

        #gpus_utilization=0
        npu_usage=0

        #dection
        for node_id, info in nodi.items():
            id_url_detection[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_detection[node_id]}")
            metriche=self.url_to_metric(id_url_detection[node_id], self.target_metrics)
            cpu_usage = metriche["ray_node_cpu_utilization"]
   #         gpus_utilization = metriche["ray_node_gpus_utilization"]
            mem_total = metriche["ray_node_mem_total"]
            mem_used = metriche["ray_node_mem_used"]

            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']
                

            #se esite NPU nel nodo
            if info['resources'].get('NPU', 0) > 0:
                url_npu=f"http://{info['ip']}:8000"
                npu_usage=self.url_to_metric(url_npu,'npu_utilization')
                npu_usage=npu_usage['npu_utilization']
                #se NPU non è utilizzata
                if npu_usage == 0:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization
                    score = ALPHA * power_consumption + BETA * (mem_used/mem_total)
                    npu_bool=True
                    if score < best_score:
                        best_node_detection={"id_node": node_id,"device":"NPU"}
                        best_score=score
            #se non esiste
            if npu_bool== False:
                if npu_usage > 0:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization + CONSUMO_NPU*npu_usage
                else:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization
                score = ALPHA * power_consumption + BETA * (mem_used/mem_total)
                if score <= best_score:
                    if gpus_utilization <= cpu_usage and info["resources"].get("GPU",0) > 0: 
                        best_node_detection={"id_node": node_id, "device": "GPU"}
                        best_score=score
                    else:
                        best_node_detection={"id_node": node_id,"device": "CPU"}
                        best_score=score
            
            #gpus_utilization=0
            npu_usage=0

        best_score=float("inf")
        #gpus_utilization=0
        npu_usage=0

        #classification
        for node_id, info in nodi.items():
            id_url_classification[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_detection[node_id]}")
            metriche=self.url_to_metric(id_url_detection[node_id], self.target_metrics)
            cpu_usage = metriche["ray_node_cpu_utilization"]
            #gpus_utilization = metriche["ray_node_gpus_utilization"]
            mem_total = metriche["ray_node_mem_total"]
            mem_used = metriche["ray_node_mem_used"]

            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']

            if info['resources'].get('NPU', 0) > 0:
                url_npu=f"http://{info['ip']}:8000"
                npu_usage=self.url_to_metric(url_npu,'npu_utilization')
                npu_usage=npu_usage['npu_utilization']

            power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization + CONSUMO_NPU*npu_usage

            score = ALPHA * power_consumption + BETA * (mem_used/mem_total)

            if score <= best_score:
                if gpus_utilization < cpu_usage and info["resources"].get("GPU",0) > 0:
                    best_node_classification={"id_node": node_id, "device": "GPU"}
                    best_score=score
                else:
                    best_node_classification={"id_node": node_id,"device": "CPU"}
                    best_score=score
            
            #gpus_utilization=0
            npu_usage=0
        
        return best_node_detection, best_node_classification

class Actuator_Scheduler(Scheduler):

    # Metriche target (queste sono le metriche che vogliamo raccogliere)
    target_metrics = {
        #"ray_node_network_send_speed",
        #"ray_node_network_receive_speed",
        "ray_node_disk_io_write_speed",
        "ray_node_disk_io_read_speed",
        #"ray_node_gpus_utilization",
    }

    network_metrics = {
        "network_tx_bytes_per_second",
        "network_tx_bytes_per_second"
    }

    def best_nodes_det_class(self):

        best_node_detection={}
        best_node_classification={}
        best_score = 0
        id_url_detection={}
        id_url_classification={}
        nodi= self.find_nodes()
        #gpus_utilization=0
        npu_usage=0

        #detection
        for node_id, info in nodi.items():
            id_url_detection[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_detection[node_id]}")
            metriche=self.url_to_metric(id_url_detection[node_id], self.target_metrics)
            #gpus_utilization = metriche["ray_node_gpus_utilization"]
            write_speed = metriche["ray_node_disk_io_write_speed"]
            read_speed = metriche["ray_node_disk_io_read_speed"]
            #receive_speed = metriche["ray_node_network_receive_speed"]
            #send_speed = metriche["ray_node_network_send_speed"]

            url_network_speed=f"http://{info['ip']}:8004"
            metriche_network=self.url_to_metric(url_network_speed, self.network_metrics)
            send_speed=metriche_network["network_tx_bytes_per_second"]
            receive_speed=metriche_network["network_rx_bytes_per_second"]


            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']

            throughput= (ALPHA* send_speed)+ (BETA* receive_speed) 
            if read_speed==0:
                score=throughput
            else:
                score= throughput + (write_speed/read_speed)

            #se esite NPU nel nodo
            if info['resources'].get('NPU', 0) > 0:
                url_npu=f"http://{info['ip']}:8000"
                npu_usage=self.url_to_metric(url_npu,'npu_utilization')
                npu_usage=npu_usage['npu_utilization']

            if score >= best_score:
                best_score = score
                if gpus_utilization < 70 and info["resources"].get("GPU",0) > 0: #soglia GPU MASSIMA 70%
                    best_node_detection={"id_node": node_id, "device": "GPU"}
                elif npu_usage == 0 and info["resources"].get('NPU', 0) > 0:
                    best_node_detection={"id_node": node_id, "device":"NPU"}
                else:
                    best_node_detection={"id_node":node_id,"device":"CPU"}

            #gpus_utilization=0
            npu_usage=0

        best_score=0

        #classification
        for node_id, info in nodi.items():
            id_url_classification[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_classification[node_id]}")
            metriche=self.url_to_metric(id_url_classification[node_id], self.target_metrics)
            #gpus_utilization = metriche["ray_node_gpus_utilization"]
            write_speed = metriche["ray_node_disk_io_write_speed"]
            read_speed = metriche["ray_node_disk_io_read_speed"]
            #receive_speed = metriche["ray_node_network_receive_speed"]
            #send_speed = metriche["ray_node_network_send_speed"]

            url_network_speed=f"http://{info['ip']}:8004"
            metriche_network=self.url_to_metric(url_network_speed, self.network_metrics)
            send_speed=metriche_network["network_tx_bytes_per_second"]
            receive_speed=metriche_network["network_rx_bytes_per_second"]


            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']

            throughput= (ALPHA* send_speed)+ (BETA* receive_speed) 
            if read_speed==0:
                score=throughput
            else:
                score= throughput + (write_speed/read_speed)

            if score >= best_score:
                best_score = score
                if gpus_utilization < 70 and info["resources"].get("GPU", 0) > 0: #soglia GPU MASSIMA 70%
                    best_node_classification={"id_node": node_id, "device": "GPU"}
                else:
                    best_node_classification={"id_node":node_id,"device":"CPU"}


        return best_node_detection,best_node_classification

class Optimum_Scheduler(Scheduler):

    # Metriche target (queste sono le metriche che vogliamo raccogliere)
    target_metrics = {
            "ray_node_cpu_utilization",
            #"ray_node_gpus_utilization",
            "ray_node_mem_total",
            "ray_node_mem_used",
            #"ray_node_network_send_speed",
            #"ray_node_network_receive_speed",
            "ray_node_disk_io_write_speed",
            "ray_node_disk_io_read_speed"
        }
    
    network_metrics = {
        "network_tx_bytes_per_second",
        "network_tx_bytes_per_second"
    }



    def best_nodes_det_class(self):
        best_node_detection={}
        best_node_classification={}
        best_score = 0
        id_url_detection={}
        id_url_classification={}
        nodi= self.find_nodes()
        npu_usage=0
        npu_bool=False
        #detection
        for node_id, info in nodi.items():
            id_url_detection[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_detection[node_id]}")
            metriche=self.url_to_metric(id_url_detection[node_id], self.target_metrics)
            cpu_usage = metriche["ray_node_cpu_utilization"]
            mem_total = metriche["ray_node_mem_total"]
            mem_used = metriche["ray_node_mem_used"]
            #gpus_utilization = metriche["ray_node_gpus_utilization"]
            write_speed = metriche["ray_node_disk_io_write_speed"]
            read_speed = metriche["ray_node_disk_io_read_speed"]
            #receive_speed = metriche["ray_node_network_receive_speed"]
            #send_speed = metriche["ray_node_network_send_speed"]

            url_network_speed=f"http://{info['ip']}:8004"
            metriche_network=self.url_to_metric(url_network_speed, self.network_metrics)
            send_speed=metriche_network["network_tx_bytes_per_second"]
            receive_speed=metriche_network["network_rx_bytes_per_second"]

            

            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']

            throughput= (ALPHA* send_speed)+ (BETA* receive_speed) 
            if read_speed==0:
                performance=throughput
            else:
                performance= throughput + (write_speed/read_speed)
            #se esite NPU nel nodo
            if info['resources'].get('NPU', 0) > 0:
                url_npu=f"http://{info['ip']}:8000"
                npu_usage=self.url_to_metric(url_npu,'npu_utilization')
                npu_usage=npu_usage['npu_utilization']
                #se NPU non è utilizzata
                if npu_usage == 0:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization
                    watt = ALPHA * power_consumption + BETA * (mem_used/mem_total)
                    npu_bool=True
            #se non esiste
            if npu_bool== False:
                if npu_usage > 0:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization + CONSUMO_NPU*npu_usage
                else:
                    power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization
                watt = ALPHA * power_consumption + BETA * (mem_used/mem_total)

            score= performance/watt

            if score >= best_score:
                best_score = score
                if info['resources'].get('NPU', 0) > 0:   
                    if npu_usage ==0:
                        best_device = 'NPU'
                        best_node_detection= {"id_node": node_id, "device": best_device}
                    elif info["resources"].get("GPU",0) > 0:
                        usage_devices = {'CPU': cpu_usage, 'GPU': gpus_utilization}
                        # Trova device con usage minore
                        best_device = min (usage_devices, key=usage_devices.get)
                        best_node_detection= {"id_node": node_id,"device": best_device}
                    else:
                        best_device = 'CPU'
                        best_node_detection= {"id_node": node_id, "device": best_device}
                elif info["resources"].get("GPU",0) > 0:
                    usage_devices = {'CPU': cpu_usage, 'GPU': gpus_utilization}
                    # Trova device con usage_minore
                    best_device = min(usage_devices, key=usage_devices.get)
                    best_node_detection={"id_node": node_id, "device": best_device}
                else:
                    best_device = 'CPU'
                    best_node_detection= {"id_node": node_id, "device": best_device}

            
            npu_usage=0

        best_score=0
        npu_usage=0

        #classification
        for node_id, info in nodi.items():
            id_url_classification[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_classification[node_id]}")
            metriche=self.url_to_metric(id_url_classification[node_id], self.target_metrics)
            cpu_usage = metriche["ray_node_cpu_utilization"]
            mem_total = metriche["ray_node_mem_total"]
            mem_used = metriche["ray_node_mem_used"]
            #gpus_utilization = metriche["ray_node_gpus_utilization"]
            write_speed = metriche["ray_node_disk_io_write_speed"]
            read_speed = metriche["ray_node_disk_io_read_speed"]
            #receive_speed = metriche["ray_node_network_receive_speed"]
            #send_speed = metriche["ray_node_network_send_speed"]

            url_network_speed=f"http://{info['ip']}:8004"
            metriche_network=self.url_to_metric(url_network_speed, self.network_metrics)
            send_speed=metriche_network["network_tx_bytes_per_second"]
            receive_speed=metriche_network["network_rx_bytes_per_second"]

            if info['resources'].get('GPU', 0) > 0:
                url_gpu=f"http://{info['ip']}:8002"
                gpus_utilization = self.url_to_metric(url_gpu,'gpu_utilization')
                gpus_utilization=gpus_utilization['gpu_utilization']
            
            #performance
            throughput= (ALPHA* send_speed)+ (BETA* receive_speed) 
            if read_speed==0:
                performance=throughput
            else:
                performance= throughput + (write_speed/read_speed)

            #watt

            #se esite NPU nel nodo
            if info['resources'].get('NPU', 0) > 0:
                url_npu=f"http://{info['ip']}:8000"
                npu_usage=self.url_to_metric(url_npu,'npu_utilization')
                npu_usage=npu_usage['npu_utilization']

            power_consumption= CONSUMO_CPU*cpu_usage+ CONSUMO_GPU*gpus_utilization + CONSUMO_NPU*npu_usage
            watt = ALPHA * power_consumption + BETA * (mem_used/mem_total)

            score= performance/watt

            if score >= best_score:
                best_score = score
                if info['resources'].get('GPU', 0) > 0:
                    usage_devices = {'CPU': cpu_usage, 'GPU': gpus_utilization}
                    # Trova device con usage_minore
                    best_device = min(usage_devices, key=usage_devices.get)
                    best_node_classification={"id_node": node_id, "device": best_device}
                else:
                    best_device = 'CPU'
                    best_node_detection= {"id_node": node_id, "device": best_device}

            
            npu_usage=0

        return best_node_detection,best_node_classification


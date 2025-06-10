import ray
import logging
import requests
import re
#from npu_utilization import calcolo_npu_percent

logger = logging.getLogger(__name__)


#FORSE DA SPOSTARE IN .YAML
CONSUMO_CPU=4
CONSUMO_GPU=8
CONSUMO_NPU=2

ALPHA=0.7 #IMPORTANZA PER POWER CAPACITY in monitoring / upload bandwith in actuator
BETA=0.3 #IMPORTANZA PER MEMORIA in monitoring /download bandwith in actuator

class Monitoring_Scheduler:

    device_to_detection= {"CPU", "NPU"}
    device_to_classifier = {"CPU"}

    def __init__(
        self,
        detection_device,
        classification_device,
    ):
        self.detection_device = detection_device
        self.classification_device = classification_device

         # CONTROLLO VALIDITÀ DEVICE DETECTION PER MONITORING
        logger.info("Check device for detection in monitoring %s...", self.detection_device)
        if not detection_device in Monitoring_Scheduler.device_to_detection:
            raise ValueError("Invalid device for detection in monitoring: " + detection_device)

        # CONTROLLO VALIDITÀ DEVICE CLASSIFICATION PER MONITORING
        logger.info("Check device for classification in monitoring %s...", self.classification_device)
        if not classification_device in Monitoring_Scheduler.device_to_classifier:
            raise ValueError("Invalid device for classification in monitoring: " + classification_device)

    def find_nodes(self): 
        #VERIFICA NODI CON RISORSE GIUSTE
        id_nodi_detection=[]
        id_nodi_classification=[]
        ip_nodi_detection=[]
        ip_nodi_classification=[]
        metric_port_detection=[]
        metric_port_classification=[]
        nodes = ray.nodes()
        for n in nodes:
            node_id = n["NodeID"]
            resources =n["Resources"]
            metric_port=n["MetricsExportPort"]
            node_ip = n["NodeManagerAddress"]

            print(f"Risorse del nodo!!!!!!!!!!!!!!!!!!!!!! ID:{node_id} IP:{node_ip} RISORSE:{resources}")

            if resources[self.detection_device] > 3: #da controllare
                id_nodi_detection.append(node_id)
                ip_nodi_detection.append(node_ip)
                metric_port_detection.append(metric_port)
            if resources[self.classification_device] > 3: #da controllare
                id_nodi_classification.append(node_id)
                ip_nodi_classification.append(node_ip)
                metric_port_classification.append(metric_port)
            
        #nodi_detection= dict(zip(id_nodi_detection, ip_nodi_detection, metric_port_detection))
        nodi_detection = {
            id_nodo: {"ip": ip, "metric_port": metric_port}
            for id_nodo, ip, metric_port in zip(id_nodi_detection, ip_nodi_detection, metric_port_detection)
        }

        #nodi_classification= dict(zip(id_nodi_classification, ip_nodi_classification, metric_port_classification))
        nodi_classification = {
            id_nodo: {"ip": ip, "metric_port": metric_port}
            for id_nodo, ip, metric_port in zip(id_nodi_classification, ip_nodi_classification, metric_port_classification)
        }
        return nodi_detection, nodi_classification

    #POWER CONSUMPTION E MEMORY_CAPACITY
    def best_nodes_det_class(self):

        id_url_detection={}
        id_url_classification={}
        nodi_detection, nodi_classification = self.find_nodes()
        classifica_det=[]
        classifica_class=[]

        #CALCOLO PUNTEGGIO PER OGNI NODO CANDIDATO A DETECTION
        for node_id, info in nodi_detection.items():
            id_url_detection[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_detection[node_id]}")
            cpu_usage, gpus_utilization, mem_total, mem_used= self.url_to_metric(id_url_detection[node_id])
            #npu_utilization= calcolo_npu_percent()
            power_consumption= (CONSUMO_CPU* cpu_usage)+ (CONSUMO_GPU*gpus_utilization) #+ (CONSUMO_NPU*npu_utilization) #NON SO PER PERCENTUALE DI UTILIZZO RISORSE CUSTOM
            score= ALPHA * power_consumption + BETA * (mem_used/mem_total)
            classifica_det.append((node_id,score))

        #CALCOLO PUNTEGGIO PER OGNI NODO CANDIDATO CLASSIFICATION
        for node_id, info in nodi_classification.items():
            id_url_classification[node_id] = f"http://{info['ip']}:{info['metric_port']}/metrics"
            print(f"ID_NODO = {node_id} e il suo URL:{id_url_classification[node_id]}")
            cpu_usage, gpus_utilization, mem_total, mem_used= self.url_to_metric(id_url_classification[node_id])
            #npu_utilization= calcolo_npu_percent()
            power_consumption= (CONSUMO_CPU* cpu_usage)+ (CONSUMO_GPU*gpus_utilization) #+ (CONSUMO_NPU*npu_utilization) #NON SO PER PERCENTUALE DI UTILIZZO RISORSE CUSTOM
            score= ALPHA * power_consumption + BETA * (mem_used/mem_total)
            classifica_class.append((node_id,score))

        nodo_minimo_det= min(classifica_det, key=lambda x: x[1])[0] #labmda per funzioni piccole in python
        nodo_minimo_class= min(classifica_class, key=lambda x:x[1])[0]

        print(f"id_nodo per detection {nodo_minimo_det}, id_nodo per classification {nodo_minimo_class}")

        return nodo_minimo_det, nodo_minimo_class

    def url_to_metric(self, url):

        cpu_usage = 0  # Impostiamo direttamente a 0
        gpus_utilization = 0
        mem_total = 0
        mem_used = 0

        # Metriche target (queste sono le metriche che vogliamo raccogliere)
        target_metrics = {
            "ray_node_cpu_utilization",
            "ray_node_gpus_utilization",
            "ray_node_disk_usage",
            "ray_node_mem_total",
            "ray_component_cpu_percentage",
            "ray_node_gram_used",
            "ray_node_network_send_speed",
            "ray_node_network_receive_speed",
            "ray_node_mem_used"
        }

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

            # Estrai l'IP, sessione e valore dalla riga
            #ip_match = re.search(r'ip="([^"]+)"', line)
            #session_match = re.search(r'SessionName="([^"]+)"', line)
            value_match = re.search(r'}\s+([0-9\.eE\+\-]+)', line)

            if value_match: #ip_match and value_match and session_match:
                #ip = ip_match.group(1)
                #session = session_match.group(1)
                value = value_match.group(1)

                # Sostituisci "None" con 0 quando necessario
                value = float(value) if value else 0  # Converti il valore in float e gestisci None come 0

                # Assegna i valori alle variabili corrispondenti (impostando 0 se non ci sono valori)
                if metric_name == "ray_node_cpu_utilization":
                    cpu_usage = value
                #elif metric_name == "ray_node_cpu_count":
                #    cpu_count = value
                elif metric_name == "ray_node_gpus_utilization":
                    gpus_utilization = value
                #elif metric_name == "ray_node_disk_usage":
                 #   disk_usage = value
                elif metric_name == "ray_node_mem_total":
                    mem_total = value
                #elif metric_name == "ray_node_gram_used":
                #    gram_used = value
                #elif metric_name == "ray_node_network_send_speed":
                #    network_send_speed = value
                #elif metric_name == "ray_node_network_receive_speed":
                 #   network_receive_speed = value
                elif metric_name == "ray_node_mem_used":
                    mem_used = value
        return cpu_usage, gpus_utilization, mem_total, mem_used
    
class Actuator_Scheduler:

    device_to_detection= {"CPU", "GPU"}
    device_to_classifier = {"CPU", "GPU"}

    def __init__(
        self,
        detection_device,
        classification_device,
    ):
        self.detection_device = detection_device
        self.classification_device = classification_device

         # CONTROLLO VALIDITÀ DEVICE DETECTION PER MONITORING
        logger.info("Check device for detection in actuator %s...", self.detection_device)
        if not detection_device in Actuator_Scheduler.device_to_detection:
            raise ValueError("Invalid device for detection in monitoring: " + detection_device)

        # CONTROLLO VALIDITÀ DEVICE CLASSIFICATION PER MONITORING
        logger.info("Check device for classification in actuator %s...", self.classification_device)
        if not classification_device in Actuator_Scheduler.device_to_classifier:
            raise ValueError("Invalid device for classification in monitoring: " + classification_device)
        
    def find_nodes(self): 
        #VERIFICA NODI CON RISORSE GIUSTE
        id_nodi_detection=[]
        id_nodi_classification=[]
        metric_port_detection=[]
        metric_port_classification=[]
        nodes = ray.nodes()
        for n in nodes:
            node_id = n["NodeID"]
            resources =n["Resources"]
            metric_port=n["MetricsExportPort"]
            if resources[self.detection_device] > 4: #da controllare
                id_nodi_detection.append(node_id)
                metric_port_detection.append(metric_port)
            if resources[self.classification_device] > 4: #da controllare
                id_nodi_classification.append(node_id)
                metric_port_classification.append(metric_port)
            
        nodi_detection= dict(zip(id_nodi_detection, metric_port_detection))
        nodi_classification= dict(zip(id_nodi_classification, metric_port_classification))
        return nodi_detection, nodi_classification
    

    def url_to_metric(self, url):

        # Metriche target (queste sono le metriche che vogliamo raccogliere)
        target_metrics = {
            "ray_node_cpu_utilization",
            "ray_node_gpus_utilization",
            "ray_node_disk_usage",
            "ray_node_mem_total",
            "ray_component_cpu_percentage",
            "ray_node_gram_used",
            "ray_node_network_send_speed",
            "ray_node_network_receive_speed",
            "ray_node_mem_used",
            "ray_node_disk_io_write_speed",
            "ray_node_disk_io_read_speed"
        }

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

            # Estrai l'IP, sessione e valore dalla riga
            #ip_match = re.search(r'ip="([^"]+)"', line)
            #session_match = re.search(r'SessionName="([^"]+)"', line)
            value_match = re.search(r'}\s+([0-9\.eE\+\-]+)', line)

            if value_match: #ip_match and value_match and session_match:
                #ip = ip_match.group(1)
                #session = session_match.group(1)
                value = value_match.group(1)

                # Sostituisci "None" con 0 quando necessario
                value = float(value) if value else 0  # Converti il valore in float e gestisci None come 0

                # Assegna i valori alle variabili corrispondenti (impostando 0 se non ci sono valori)
                #if metric_name == "ray_node_cpu_utilization":
                #    cpu_usage = value
                #elif metric_name == "ray_node_cpu_count":
                #    cpu_count = value
                #elif metric_name == "ray_node_gpus_utilization":
                #    gpus_utilization = value
                #elif metric_name == "ray_node_disk_usage":
                 #   disk_usage = value
                #elif metric_name == "ray_node_mem_total":
                #   mem_total = value
                #elif metric_name == "ray_node_gram_used":
                #    gram_used = value
                if metric_name == "ray_node_network_send_speed":
                    network_send_speed = value
                elif metric_name == "ray_node_network_receive_speed":
                    network_receive_speed = value
                elif metric_name == "ray_node_disk_io_write_speed":
                    write_speed = value
                elif metric_name == "ray_node_disk_io_read_speed":
                   read_speed = value

        return network_send_speed, network_receive_speed, read_speed, write_speed
    
    def best_nodes_det_class(self):

        id_url_detection={}
        id_url_classification={}
        nodi_detection, nodi_classification = self.find_nodes()
        classifica_det=[]
        classifica_class=[]

        #CALCOLO PUNTEGGIO PER OGNI NODO CANDIDATO A DETECTION
        for node_id, port in nodi_detection.items():
            id_url_detection[node_id] = f"http://localhost:{port}/metrics"
            print(id_url_detection)
            network_send_speed, network_receive_speed, read_speed, write_speed = self.url_to_metric(id_url_detection[node_id])
            throughput= (ALPHA* network_send_speed)+ (BETA* network_receive_speed) 
            score= throughput + (write_speed/read_speed)
            classifica_det.append((node_id,score))

        #CALCOLO PUNTEGGIO PER OGNI NODO CANDIDATO CLASSIFICATION
        for node_id, port in nodi_classification.items():
            id_url_classification[node_id] = f"http://localhost:{port}/metrics"
            print(id_url_classification)
            network_send_speed, network_receive_speed, read_speed, write_speed= self.url_to_metric(id_url_classification[node_id])
            throughput= (ALPHA* network_send_speed)+ (BETA* network_receive_speed) 
            score= throughput + (write_speed/read_speed)
            classifica_class.append((node_id,score))

        nodo_massimo_det= max(classifica_det, key=lambda x: x[1])[0] #labmda per funzioni piccole in python
        nodo_massimo_class= max(classifica_class, key=lambda x:x[1])[0]

        print(f"id_nodo per detection {nodo_massimo_det}, id_nodo per classification {nodo_massimo_class}")

        return nodo_massimo_det, nodo_massimo_class
    
#monitoir= Monitoring_Scheduler("CPU", "CPU").best_nodes_det_class()

#print(f"id_nodo per detection {monitoir[0]}, id_nodo per classification {monitoir[1]}")
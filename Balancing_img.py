#from wadas.ai.pipeline import DetectionPipeline
from wadas.domain.ai_model import AiModel
#from PIL import Image
import time #per calcolo inferenza
import psutil #PER MONITORAGGIO MEMORIA DI SISTEMA
import os#PER MONITORAGGIO MEMORIA
from threading import Thread, Event#PER MONITORAGGIO CPU
#import intel_npu_acceleration_library as npu_libray

def memoria(memoria_iniziale, memoria_finale):
    #TO DO-- BANDWITH_MEMORIA:Gb/S
    return (memoria_finale-memoria_iniziale)

def monitoraggio_cpu(processo, stop_event, cpu_usato):
    
    
    while not stop_event.is_set():  # Continua fino a quando stop_event non è settato
        cpu_percentuale = processo.cpu_percent(interval=1)  # Misura ogni 1 secondo
        num_core_logici = psutil.cpu_count()
        uso_normalizzato = cpu_percentuale / num_core_logici
        cpu_usato.append(uso_normalizzato)
        print(f"Uso CPU per il processo: {uso_normalizzato}%")  # Stampa l'uso della CPU
        
    # Calcola l'uso medio della CPU durante l'inferenza
    uso_medio_cpu = sum(cpu_usato) / len(cpu_usato) if cpu_usato else 0
    print(f"Uso medio della CPU durante l'inferenza: {uso_medio_cpu:.2f}%")
    return uso_medio_cpu

def inferenza(start: float, end: float):
    return round((end-start),6)

#FONTE consumo_cpu_watt: https://www.intel.com/content/www/us/en/products/sku/240961/intel-core-ultra-9-processor-288v-12m-cache-up-to-5-10-ghz/specifications.html
def stima_consumo_energia(uso_medio_cpu, tempo_inferenza, consumo_cpu_watt=37):
    # Consideriamo che il consumo della CPU sia lineare con l'uso percentuale della CPU
    # Ad esempio, se la CPU usa 50W al 100%, al 50% consumerebbe 25W
    consumo_cpu = (uso_medio_cpu / 100) * consumo_cpu_watt  # consumo in Watt
    #consumo_energia = consumo_cpu * tempo_inferenza  # Consumo in Wattsecondi (Ws)
    #consumo_energia = consumo_cpu * (tempo_inferenza / 60)  # Consumo in Wattminuti(Wminuti)
    consumo_energia = consumo_cpu * (tempo_inferenza / 3600)  # Consumo in Wattora (Wh)
    return consumo_energia

def detection_classification(processo):   #(processo, *det_device, **class_device)
    memoria_iniziale = processo.memory_info().rss / (1024 ** 3)  # in GB
    start=time.perf_counter()
    #PER CAMBIAMENTI
    AiModel.detection_threshold=0.5
    AiModel.detection_model_version="MDV5-yolov5"
    AiModel.detection_device="NPU" 
    AiModel.classification_device = "GPU" 
    AiModel.classification_threshold = 0.5
    AiModel.language = "en"
    AiModel.video_fps = 1
    AiModel.distributed_inference = False
    AiModel.classification_model_version = "DFv1.2"
    AiModel.use_case='MONITORING'
    print("AIMODEL DEVICE: ", AiModel.detection_device)
    ai_model=AiModel()
    
    print("\n")
    print("-------------DETECTOR--------------")
    print("AIMODEL DEVICE impostato in Balancing: ", AiModel.detection_device, "\n oggetto aimodel DETDEVICE creato in Balancing: ", ai_model.detection_device, "\n device DETDEVICE in PIPELINE scelto da scheduler: ", ai_model.detection_pipeline.detection_device)
    print("\n")
    print("-------------CLASSIFICATOR--------------")
    print("AIMODEL DEVICE impostato in Balancing: ", AiModel.classification_device, "\n oggetto aimodel DETDEVICE creato in Balancing: ", ai_model.classification_device, "\n device DETDEVICE in PIPELINE scelto da scheduler: ", ai_model.detection_pipeline.classification_device)
    print("\n")
    
    detection=ai_model.process_image(Image_path, True) 
    ai_model.classify(Image_path,detection[0]) #CLASSIFICAZIONE

    memoria_finale = processo.memory_info().rss / (1024 ** 3)  # in GB
    end=time.perf_counter()
    
    return memoria_iniziale, memoria_finale,start, end, ai_model


Image_path="/home/univaq/Scaricati/video-immagini_test_1/immagine_test_1_ANIMALI.png"
cpu_usato = []
id_process=os.getpid()
processo = psutil.Process(id_process)
uso_medio_cpu=0
stop_event = Event()
# Avvia il thread di monitoraggio della CPU
monitor_thread = Thread(target=monitoraggio_cpu, args=(processo, stop_event,cpu_usato))
monitor_thread.start()
risultati=detection_classification(processo)

stop_event.set()
monitor_thread.join()

risultato_inferenza=inferenza(risultati[2],risultati[3])
risultato_memoria= memoria(risultati[0],risultati[1])
uso_medio_cpu = sum(cpu_usato) / len(cpu_usato) if cpu_usato else 0
risultato_energia= stima_consumo_energia(uso_medio_cpu,risultato_inferenza)


#salva risultati su file.txt
path_file_risultati = "/home/univaq/WADAS/risultati/risultati_test.txt"
with open(path_file_risultati, "a") as f:
    f.write(f"Detection_device: {risultati[4].detection_device},\n detection_threshold: {risultati[4].detection_threshold},\n detection_model_version: {risultati[4].detection_model_version},\n classification_device: {risultati[4].classification_device},\n classification_threshold: {risultati[4].classification_threshold},\n classification_model_version: {risultati[4].classification_model_version},\n distributed_inference: {risultati[4].distributed_inference},\n  video_FPS: {risultati[4].video_fps}\n")
    f.write(f"Tempo di inferenza: {risultato_inferenza:.6f} secondi\n")
    f.write(f"Uso medio della CPU durante l'inferenza: {uso_medio_cpu:.2f}%\n")
    f.write(f"Memoria usata: {risultato_memoria:.2f} GB\n")
    f.write(f"Consumo stimato: {risultato_energia:.6f} Wh\n")
    f.write(f"---------------------------..--------------------------------------..----------------------------\n")




   
   
    
    
   
   
   
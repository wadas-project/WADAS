from wadas.ai.pipeline import DetectionPipeline
from wadas.domain.ai_model import AiModel
from PIL import Image
import time #per calcolo inferenza
import psutil #PER MONITORAGGIO MEMORIA DI SISTEMA
import os#PER MONITORAGGIO MEMORIA
from threading import Thread, Event#PER MONITORAGGIO CPU

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

def detection_classification(processo):
    memoria_iniziale = processo.memory_info().rss / (1024 ** 3)  # in GB
    start=time.perf_counter()
    #PER CAMBIAMENTI
    AiModel.detection_threshold=0.5
    AiModel.detection_model_version="MDV5-yolov5"
    AiModel.detection_device="GPU"
    AiModel.classification_device = "CPU"
    AiModel.classification_threshold = 0.5
    AiModel.language = "en"
    AiModel.video_fps = 1
    AiModel.distributed_inference = True
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

    #ai_model.detection_pipeline = DetectionPipeline(
    #detection_device=ai_model.detection_device,
    #classification_device=ai_model.classification_device,
    #language=ai_model.language,
    #distributed_inference=ai_model.distributed_inference,
    #megadetector_version=ai_model.detection_model_version,
    #)
    
    detection_video=ai_model.process_video(Video_Path,True)
    results = [] 
    detected_img_path = [] 
    frame_path = []
    for result, det_img_path, fr_path in detection_video:
        results.append(result)
        detected_img_path.append(det_img_path)
        frame_path.append(fr_path)

    for path, res in zip(detected_img_path, results):
        classification_video=ai_model.classify(path, res)
    
    memoria_finale = processo.memory_info().rss / (1024 ** 3)  # in GB
    end=time.perf_counter()
    
    #detection_video = list(detection_video)
    #print("RISULTATO", "detection[0]:", detection_video[0],"detection[1]:", detection_video[1] )
    return memoria_iniziale, memoria_finale,start, end, ai_model

#VIDEO REOLINK(test)
Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR1.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR2.mp4"
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR3.mp4"
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR4.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR5.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR6.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR7.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR8.mp4" 
#Video_Path="/Scrivania/VIDEO_TEST/ReolinkGoR9.mp4" 

 



## VIDEO QUI-youtube
#Video_Path="/home/univaq/Scaricati/video-immagini_test_1/video_10MB_360px.mp4" 
#Video_Path="/home/univaq/Scaricati/video-immagini_test_1/Video_10MB_720px.mp4" NO
#Video_Path="/home/univaq/Scaricati/video-immagini_test_1/video_86MB.mp4"
#Video_Path="/home/univaq/Scaricati/video-immagini_test_1/video_158MB.mp4"
#Video_Path="/home/univaq/Scaricati/video-immagini_test_1/video_175MB.mp4" --------- non usare da errore corrupted size vs. prev_size Annullato (core dump creato)



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
path_file_risultati = "/home/univaq/WADAS/risultati_video/risultati_test_video.txt"
with open(path_file_risultati, "a") as f:
    f.write(f"Detection_device: {risultati[4].detection_device},\n detection_threshold: {risultati[4].detection_threshold},\n detection_model_version: {risultati[4].detection_model_version},\n classification_device: {risultati[4].classification_device},\n classification_threshold: {risultati[4].classification_threshold},\n classification_model_version: {risultati[4].classification_model_version},\n distributed_inference: {risultati[4].distributed_inference},\n  video_FPS: {risultati[4].video_fps}\n")
    f.write(f"Tempo di inferenza: {risultato_inferenza:.6f} secondi\n")
    f.write(f"Uso medio della CPU durante l'inferenza: {uso_medio_cpu:.2f}%\n")
    f.write(f"Memoria usata: {risultato_memoria:.2f} GB\n")
    f.write(f"Consumo stimato: {risultato_energia:.6f} Wh\n")
    f.write(f"---------------------------..--------------------------------------..----------------------------\n")

from openvino.runtime import Core

# Inizializza il Core di OpenVINO
core = Core()

# Ottieni la lista dei dispositivi disponibili
devices = core.available_devices
print("Dispositivi disponibili:", devices)

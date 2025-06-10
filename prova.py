

from openvino.runtime import Core

core = Core()
model_path = "/home/univaq/WADAS/model/classification/DFv1.2_openvino_model/DFv1.2.xml"  # Assicurati che sia il percorso giusto
try:
    model = core.read_model(model_path)
    compiled_model = core.compile_model(model, "GPU")  # Prova a compilarlo sulla CPU
    print("Il modello è stato caricato e compilato con successo!")
except Exception as e:
    print(f"Errore durante il caricamento del modello: {e}")

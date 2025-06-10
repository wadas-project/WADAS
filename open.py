#from openvino.runtime import Core
#core = Core()
#devices = core.get_available_devices()
#print(devices)
import openvino as ov
core = ov.Core()
for device in core.available_devices:
    print(f"Device: {device}")
    print(core.get_property(device, "FULL_DEVICE_NAME"))


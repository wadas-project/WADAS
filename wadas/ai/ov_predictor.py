import logging
from pathlib import Path

import torch
from ultralytics.models.yolo.detect import DetectionPredictor
from ultralytics.utils.torch_utils import select_device
from wadas_runtime import load_and_compile_model

from wadas.ai.openvino_model import __model_folder__

# Silence ultralytics logger
logging.getLogger("ultralytics").setLevel(logging.ERROR)


class OVModelWrapper(torch.nn.Module):
    def __init__(self, compiled_model, device="cpu"):
        super().__init__()
        self.model = compiled_model
        self.device = device
        self.input_name = next(iter(compiled_model.inputs)).any_name

    def forward(self, x):
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().numpy()
        output_dict = self.model({self.input_name: x})
        output = next(iter(output_dict.values()))
        return torch.tensor(output, device=self.device)


class OVBackend(torch.nn.Module):
    def __init__(self, compiled_model, device="cpu", fp16=False, stride=32, names=None):
        super().__init__()
        self.model = OVModelWrapper(compiled_model, device=device)
        self.device = torch.device(device)
        self.fp16 = fp16
        self.stride = stride
        self.names = names or {i: f"class_{i}" for i in range(80)}
        self.pt = False
        self.triton = False
        self.yaml_file = None

    def forward(self, x, *args, **kwargs):
        return self.model(x)

    def eval(self):
        return self.model.eval()

    def warmup(self, imgsz=(1, 3, 640, 640)):
        dummy_input = torch.zeros(imgsz, device=self.device)
        with torch.no_grad():
            _ = self.forward(dummy_input)

    def fuse(self):
        return self

    def autoshape(self):
        return self


class OVPredictor(DetectionPredictor):
    def __init__(self, *args, ov_device="AUTO", **kwargs):
        super().__init__(*args, **kwargs)
        self.ov_device = ov_device

    def setup_model(self, model_instance, relative_path, verbose=False):
        model_path = Path(__model_folder__) / relative_path
        xml_path = next(model_path.glob("*.xml"))
        bin_path = xml_path.with_suffix(".bin")

        compiled_model = load_and_compile_model(
            str(xml_path), str(bin_path), self.ov_device, config={"PERFORMANCE_HINT": "LATENCY"}
        )

        self.model = OVBackend(
            compiled_model=compiled_model,
            device=select_device(self.args.device, verbose=verbose),
            fp16=self.args.half,
            stride=32,
            names=model_instance.get_class_names(),
        )

        self.device = self.model.device
        self.args.half = self.model.fp16
        self.model.eval()


def load_ov_model(weights, device, inference_mode="LATENCY"):
    from pathlib import Path

    w = str(weights[0] if isinstance(weights, list) else weights)
    w = Path(w)
    if not w.is_file():
        w = next(w.glob("*.xml"))
    config = {"PERFORMANCE_HINT": inference_mode}
    return load_and_compile_model(str(w), str(w.with_suffix(".bin")), device, config)

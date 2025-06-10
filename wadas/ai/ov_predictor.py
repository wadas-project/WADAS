import logging
import os
from pathlib import Path

import openvino as ov
import torch
from ultralytics.models.yolo.detect import DetectionPredictor
from ultralytics.nn.autobackend import AutoBackend
from ultralytics.utils.torch_utils import select_device

from wadas.ai.openvino_model import __model_folder__

# Silence ultralytics logger
logging.getLogger("ultralytics").setLevel(logging.ERROR)


def load_ov_model(weights, device, inference_mode="LATENCY"):
    core = ov.Core()
    w = str(weights[0] if isinstance(weights, list) else weights)
    w = Path(w)
    if not w.is_file():  # if not *.xml
        w = next(w.glob("*.xml"))  # get *.xml file from *_openvino_model dir
    ov_model = core.read_model(model=str(w), weights=w.with_suffix(".bin"))
    return core.compile_model(
        ov_model,
        device_name=str(device).upper(),
        config={"PERFORMANCE_HINT": inference_mode},
    )


class OVBackend(AutoBackend):
    @torch.no_grad()
    def __init__(
        self,
        weights="yolo11n.pt",
        device="cpu",
        dnn=False,
        data=None,
        fp16=False,
        ov_device="AUTO",
        batch=1,
        fuse=True,
        verbose=True,
    ):
        super().__init__(weights, torch.device(device), dnn, data, fp16, batch, fuse, verbose)
        w = str(weights[0] if isinstance(weights, list) else weights)
        w = Path(w)
        if not w.is_file():  # if not *.xml
            w = next(w.glob("*.xml"))  # get *.xml file from *_openvino_model dir
        self.inference_mode = "LATENCY"
        self.ov_compiled_model = load_ov_model(w, ov_device, self.inference_mode)


class OVPredictor(DetectionPredictor):
    def __init__(self, *args, ov_device="AUTO", **kwargs):
        super().__init__(*args, **kwargs)
        self.ov_device = ov_device

    def setup_model(self, model, verbose):
        model = os.path.join(__model_folder__, model)
        self.model = OVBackend(
            weights=model or self.args.model,
            device=select_device(self.args.device, verbose=verbose),
            ov_device=self.ov_device,
            dnn=self.args.dnn,
            data=self.args.data,
            fp16=self.args.half,
            batch=self.args.batch,
            fuse=True,
            verbose=verbose,
        )

        self.device = self.model.device  # update device
        self.args.half = self.model.fp16  # update half
        self.model.eval()

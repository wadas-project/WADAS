import logging
import os
from pathlib import Path

import torch
import wadas_runtime as wadas
import yaml
from ultralytics.models.yolo.detect import DetectionPredictor
from ultralytics.nn.autobackend import (
    AutoBackend,
    check_class_names,
    default_class_names,
)
from ultralytics.utils.torch_utils import select_device

from wadas.ai.openvino_model import __model_folder__

# Silence ultralytics logger
logging.getLogger("ultralytics").setLevel(logging.ERROR)


def load_ov_model(weights, device, inference_mode="LATENCY"):
    w = str(weights[0] if isinstance(weights, list) else weights)
    w = Path(w)
    if not w.is_file():  # if not *.xml
        w = next(w.glob("*.xml"))  # get *.xml file from *_openvino_model dir
    config = {"PERFORMANCE_HINT": inference_mode}
    return wadas.load_and_compile_model(str(w), str(w.with_suffix(".bin")), device.upper(), config)


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
        """AutoBackend class attempts to load a model using OpenVINO runtime.
        However for an encrypted model that won't work because some layer attributes like shapes
        and so are in the bin and encrypted, so if AutoBackend loads it it will fail.
        The solution here is to bypass the AutoBackend __init__ and load the model here.
        AutoBakend sets a lot of attributes that we need to set here manually."""
        torch.nn.Module.__init__(self)
        nhwc = False  # default to NCHW
        dynamic = False  # default to static shape
        fp16 = fp16
        w = str(weights[0] if isinstance(weights, list) else weights)
        nn_module = False
        w = Path(w)
        (
            pt,
            jit,
            onnx,
            xml,
            engine,
            coreml,
            saved_model,
            pb,
            tflite,
            edgetpu,
            tfjs,
            paddle,
            mnn,
            ncnn,
            imx,
            rknn,
            triton,
        ) = self._model_type(w)
        if not w.is_file():  # if not *.xml
            w = next(w.glob("*.xml"))  # get *.xml file from *_openvino_model dir
        inference_mode = "LATENCY"
        ov_compiled_model = load_ov_model(w, ov_device, inference_mode)
        input_name = ov_compiled_model.input().get_any_name()

        with open(w.parent / "metadata.yaml", "r") as f:
            metadata = yaml.safe_load(f)
        if metadata and isinstance(metadata, dict):
            for k, v in metadata.items():
                if k in {"stride", "batch"}:
                    metadata[k] = int(v)
                elif k in {"imgsz", "names", "kpt_shape", "args"} and isinstance(v, str):
                    metadata[k] = eval(v)
            stride = metadata["stride"]
            task = metadata["task"]
            batch = metadata["batch"]
            imgsz = metadata["imgsz"]
            names = metadata["names"]
            kpt_shape = metadata.get("kpt_shape")
            end2end = metadata.get("args", {}).get("nms", False)
            dynamic = metadata.get("args", {}).get("dynamic", dynamic)

        if "names" not in locals():  # names missing
            names = default_class_names(data)
        names = check_class_names(names)
        self.__dict__.update(locals())


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

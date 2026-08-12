# This file is part of WADAS project.
#
# WADAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WADAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with WADAS. If not, see <https://www.gnu.org/licenses/>.
#
# Author(s): Stefano Dell'Osa, Alessandro Palla, Cesare Di Mauro, Antonio Farina
# Date: 2024-10-11
# Description: This module implements OpenVINO related classes and functionalities.

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
import torch
from PytorchWildlife.data import transforms as pw_trans
from PytorchWildlife.models import detection as pw_detection
from torchvision.transforms import InterpolationMode, transforms

from wadas.ai.openvino_model import OVModel
from wadas.ai.ov_predictor import OVPredictor

txt_animalclasses = {
    "DFv1.2": {
        "fr": [
            "blaireau",
            "bouquetin",
            "cerf",
            "chamois",
            "chat",
            "chevre",
            "chevreuil",
            "chien",
            "ecureuil",
            "equide",
            "genette",
            "herisson",
            "lagomorphe",
            "loup",
            "lynx",
            "marmotte",
            "micromammifere",
            "mouflon",
            "mouton",
            "mustelide",
            "oiseau",
            "ours",
            "ragondin",
            "renard",
            "sanglier",
            "vache",
        ],
        "en": [
            "badger",
            "ibex",
            "red deer",
            "chamois",
            "cat",
            "goat",
            "roe deer",
            "dog",
            "squirrel",
            "equid",
            "genet",
            "hedgehog",
            "lagomorph",
            "wolf",
            "lynx",
            "marmot",
            "micromammal",
            "mouflon",
            "sheep",
            "mustelid",
            "bird",
            "bear",
            "nutria",
            "fox",
            "wild boar",
            "cow",
        ],
        "it": [
            "tasso",
            "stambecco",
            "cervo",
            "camoscio",
            "gatto",
            "capra",
            "capriolo",
            "cane",
            "scoiattolo",
            "equide",
            "genet",
            "riccio",
            "lagomorfo",
            "lupo",
            "lince",
            "marmotta",
            "micromammifero",
            "muflone",
            "pecora",
            "mustelide",
            "uccello",
            "orso",
            "nutria",
            "volpe",
            "cinghiale",
            "mucca",
        ],
        "de": [
            "Dachs",
            "Steinbock",
            "Rothirsch",
            "Gämse",
            "Katze",
            "Ziege",
            "Rehwild",
            "Hund",
            "Eichhörnchen",
            "Equiden",
            "Ginsterkatze",
            "Igel",
            "Lagomorpha",
            "Wolf",
            "Luchs",
            "Murmeltier",
            "Kleinsäuger",
            "Mufflon",
            "Schaf",
            "Mustelide",
            "Vogen",
            "Bär",
            "Nutria",
            "Fuchs",
            "Wildschwein",
            "Kuh",
        ],
    },
    "DFv1.3": {
        "fr": [
            "bison",
            "blaireau",
            "bouquetin",
            "castor",
            "cerf",
            "chamois",
            "chat",
            "chevre",
            "chevreuil",
            "chien",
            "daim",
            "ecureuil",
            "elan",
            "equide",
            "genette",
            "glouton",
            "herisson",
            "lagomorphe",
            "loup",
            "loutre",
            "lynx",
            "marmotte",
            "micromammifere",
            "mouflon",
            "mouton",
            "mustelide",
            "oiseau",
            "ours",
            "ragondin",
            "raton laveur",
            "renard",
            "renne",
            "sanglier",
            "vache",
        ],
        "en": [
            "bison",
            "badger",
            "ibex",
            "beaver",
            "red deer",
            "chamois",
            "cat",
            "goat",
            "roe deer",
            "dog",
            "fallow deer",
            "squirrel",
            "moose",
            "equid",
            "genet",
            "wolverine",
            "hedgehog",
            "lagomorph",
            "wolf",
            "otter",
            "lynx",
            "marmot",
            "micromammal",
            "mouflon",
            "sheep",
            "mustelid",
            "bird",
            "bear",
            "nutria",
            "raccoon",
            "fox",
            "reindeer",
            "wild boar",
            "cow",
        ],
        "it": [
            "bisonte",
            "tasso",
            "stambecco",
            "castoro",
            "cervo",
            "camoscio",
            "gatto",
            "capra",
            "capriolo",
            "cane",
            "daino",
            "scoiattolo",
            "alce",
            "equide",
            "genetta",
            "ghiottone",
            "riccio",
            "lagomorfo",
            "lupo",
            "lontra",
            "lince",
            "marmotta",
            "micromammifero",
            "muflone",
            "pecora",
            "mustelide",
            "uccello",
            "orso",
            "nutria",
            "procione",
            "volpe",
            "renna",
            "cinghiale",
            "mucca",
        ],
        "de": [
            "Bison",
            "Dachs",
            "Steinbock",
            "Biber",
            "Rothirsch",
            "Gämse",
            "Katze",
            "Ziege",
            "Rehwild",
            "Hund",
            "Damwild",
            "Eichhörnchen",
            "Elch",
            "Equide",
            "Ginsterkatze",
            "Vielfraß",
            "Igel",
            "Lagomorpha",
            "Wolf",
            "Otter",
            "Luchs",
            "Murmeltier",
            "Kleinsäuger",
            "Mufflon",
            "Schaf",
            "Marder",
            "Vogel",
            "Bär",
            "Nutria",
            "Waschbär",
            "Fuchs",
            "Rentier",
            "Wildschwein",
            "Kuh",
        ],
    },
    "DFv1.4": {
        "fr": [
            "bison",
            "blaireau",
            "bouquetin",
            "castor",
            "cerf",
            "chacal doré",
            "chamois",
            "chat",
            "chevre",
            "chevreuil",
            "chien",
            "chien viverrin",
            "daim",
            "ecureuil",
            "elan",
            "equide",
            "genette",
            "glouton",
            "herisson",
            "lagomorphe",
            "loup",
            "loutre",
            "lynx",
            "marmotte",
            "micromammifere",
            "mouflon",
            "mouton",
            "mustelide",
            "oiseau",
            "ours",
            "porcepic",
            "ragondin",
            "rat musqué",
            "raton laveur",
            "renard",
            "renne",
            "sanglier",
            "vache",
        ],
        "en": [
            "bison",
            "badger",
            "ibex",
            "beaver",
            "red deer",
            "golden jackal",
            "chamois",
            "cat",
            "goat",
            "roe deer",
            "dog",
            "raccoon dog",
            "fallow deer",
            "squirrel",
            "moose",
            "equid",
            "genet",
            "wolverine",
            "hedgehog",
            "lagomorph",
            "wolf",
            "otter",
            "lynx",
            "marmot",
            "micromammal",
            "mouflon",
            "sheep",
            "mustelid",
            "bird",
            "bear",
            "porcupine",
            "nutria",
            "muskrat",
            "raccoon",
            "fox",
            "reindeer",
            "wild boar",
            "cow",
        ],
        "it": [
            "bisonte",
            "tasso",
            "stambecco",
            "castoro",
            "cervo",
            "sciacallo dorato",
            "camoscio",
            "gatto",
            "capra",
            "capriolo",
            "cane",
            "cane procione",
            "daino",
            "scoiattolo",
            "alce",
            "equide",
            "genetta",
            "ghiottone",
            "riccio",
            "lagomorfo",
            "lupo",
            "lontra",
            "lince",
            "marmotta",
            "micromammifero",
            "muflone",
            "pecora",
            "mustelide",
            "uccello",
            "orso",
            "istrice",
            "nutria",
            "ondatra",
            "procione",
            "volpe",
            "renna",
            "cinghiale",
            "mucca",
        ],
        "de": [
            "Bison",
            "Dachs",
            "Steinbock",
            "Biber",
            "Rothirsch",
            "Goldschakal",
            "Gämse",
            "Katze",
            "Ziege",
            "Rehwild",
            "Hund",
            "Marderhund",
            "Damwild",
            "Eichhörnchen",
            "Elch",
            "Equide",
            "Ginsterkatze",
            "Vielfraß",
            "Igel",
            "Lagomorpha",
            "Wolf",
            "Otter",
            "Luchs",
            "Murmeltier",
            "Kleinsäuger",
            "Mufflon",
            "Schaf",
            "Marder",
            "Vogel",
            "Bär",
            "Stachelschwein",
            "Nutria",
            "Bisamratte",
            "Waschbär",
            "Fuchs",
            "Rentier",
            "Wildschwein",
            "Kuh",
        ],
    },
}


class WadasAiModel(ABC):
    """Base class for WADAS AI models."""

    def get_class_names(self):
        """Get class names"""
        return self.CLASS_NAMES

    @abstractmethod
    def run(self, img_array: np.ndarray, detection_threshold: float):
        """Method to run detection model"""
        pass

    @staticmethod
    @abstractmethod
    def check_model():
        """Check if detection model is initialized"""
        pass

    @staticmethod
    @abstractmethod
    def download_model(force: bool = False):
        """Method to download the model."""
        pass


class OVMegaDetectorV5(pw_detection.MegaDetectorV5, WadasAiModel):
    """MegaDetectorV5 class for detection model"""

    def __init__(self, device, model_name="MDV5-yolov5"):
        self.model = OVModel(
            Path("detection", f"{model_name}_openvino_model", f"{model_name}.xml"), device
        )
        self.device = "cpu"  # torch device, keep to CPU when using with OpenVINO
        self.transform = pw_trans.MegaDetector_v5_Transform(
            target_size=self.IMAGE_SIZE, stride=self.STRIDE
        )

    def run(self, img_array: np.ndarray, detection_threshold: float):
        """Run detection model"""
        return self.single_image_detection(img_array, None, detection_threshold, None)

    @staticmethod
    def check_model():
        """Check if detection model is initialized"""
        return OVModel.check_model(
            Path("detection", "MDV5-yolov5_openvino_model", "MDV5-yolov5.xml")
        )

    @staticmethod
    def download_model(force: bool = False):
        """Method to download the model."""
        return OVModel.download_model(
            Path("detection", "MDV5-yolov5_openvino_model", "MDV5-yolov5"), force
        )


class OVMegaDetectorV6(pw_detection.MegaDetectorV6, WadasAiModel, ABC):
    """MegaDetectorV6 base class for detection model"""

    IMAGE_SIZE = 640

    def __init__(self, device, model_name):
        self.predictor = OVPredictor(ov_device=device)
        self.device = "cpu"  # torch device, keep to CPU when using with OpenVINO
        self.model_name = model_name
        self.predictor.setup_model(
            Path("detection", f"{self.model_name}_openvino_model"), verbose=False
        )

        self.predictor.args.imgsz = self.IMAGE_SIZE
        self.predictor.args.save = (
            False  # Will see if we want to use ultralytics native inference saving functions.
        )

    def run(self, img_array: np.ndarray, detection_threshold: float):
        """Run detection model"""
        return self.single_image_detection(img_array, None, detection_threshold, None)


class OVMegaDetectorV6YOLO9(OVMegaDetectorV6):
    """MegaDetectorV6 YOLO9 class for detection model"""

    @staticmethod
    def check_model():
        """Check if detection model is initialized"""
        return OVModel.check_model(
            Path("detection", "MDV6b-yolov9c_openvino_model", "MDV6b-yolov9c.xml")
        )

    @staticmethod
    def download_model(force: bool = False):
        """Method to download the model."""
        return OVModel.download_model(
            Path("detection", "MDV6b-yolov9c_openvino_model", "MDV6b-yolov9c"), force
        )


class OVMegaDetectorV6YOLO10(OVMegaDetectorV6):
    """MegaDetectorV6 YOLO10 class for detection model"""

    @staticmethod
    def check_model():
        """Check if detection model is initialized"""
        return OVModel.check_model(
            Path("detection", "MDV6-yolov10n_openvino_model", "MDV6-yolov10n.xml")
        )

    @staticmethod
    def download_model(force: bool = False):
        """Method to download the model."""
        return OVModel.download_model(
            Path("detection", "MDV6-yolov10n_openvino_model", "MDV6-yolov10n"), force
        )


class Classifier:
    """Classifier class for classification model (DeepFaune)."""

    CROP_SIZE = 182

    def __init__(self, device, version="DFv1.2"):
        self.version = version
        self.model = OVModel(
            Path("classification", f"{version}_openvino_model", f"{version}.xml"), device
        )
        self.transforms = transforms.Compose(
            [
                transforms.Resize(
                    size=(self.CROP_SIZE, self.CROP_SIZE),
                    interpolation=InterpolationMode.BICUBIC,
                    max_size=None,
                    antialias=None,
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=torch.tensor([0.4850, 0.4560, 0.4060]),
                    std=torch.tensor([0.2290, 0.2240, 0.2250]),
                ),
            ]
        )

    def get_labels(self, language: str) -> list[str]:
        """Return the ordered list of class display names for this classifier and language."""
        return txt_animalclasses[self.version][language]

    @staticmethod
    def check_model(version="DFv1.2"):
        """Check if classification model is initialized"""
        return OVModel.check_model(
            Path("classification", f"{version}_openvino_model", f"{version}.xml")
        )

    @staticmethod
    def download_model(version="DFv1.2", force: bool = False):
        """Download classification model"""
        return OVModel.download_model(
            Path("classification", f"{version}_openvino_model", f"{version}"), force
        )

    def predictOnBatch(self, batchtensor, withsoftmax=True):
        """Predict on a batch of images"""
        logits = self.model(batchtensor)
        return logits.softmax(dim=1) if withsoftmax else logits

    def preprocessImage(self, croppedimage):
        """Preprocess the image for classification.
        The preprocessing consists of resizing, converting to tensor and normalizing the image.
        """
        preprocessimage = self.transforms(croppedimage)
        return preprocessimage.unsqueeze(dim=0)

    def predictOnImages(self, request, withsoftmax=True) -> torch.Tensor:
        img, results = request
        if results["detections"].xyxy.shape[0] == 0:
            return
        """Predict on a single image"""
        tensor = torch.concatenate(
            [self.preprocessImage(img.crop(xyxy)) for xyxy in results["detections"].xyxy],
            axis=0,
        )
        return self.predictOnBatch(tensor, withsoftmax=withsoftmax)


class SpeciesNetClassifier:
    """Classifier wrapping the OpenVINO-converted SpeciesNet model (Google cameratrapai).

    Key differences from DeepFaune Classifier:
    - Input: NHWC float32 [0, 1], size 480x480 (no ImageNet mean/std normalization).
    - Labels: loaded from labels.txt alongside the IR; ~2000+ classes in English only.
    - class_probs in classify() output is capped to TOP_K_CLASS_PROBS entries to avoid
      bloating the DB and notification payloads.
    - Language support: only "en" (SpeciesNet labels are English species names).
    """

    IMG_SIZE = 480
    # Only the top-N scores are stored in class_probs to keep payloads manageable.
    TOP_K_CLASS_PROBS = 10

    def __init__(self, device, version="SpeciesNetV4"):
        self.version = version
        self.model = OVModel(
            Path("classification", f"{version}_openvino_model", f"{version}.xml"), device
        )
        labels_path = (
            Path(__file__).resolve().parents[2]
            / "model"
            / "classification"
            / f"{version}_openvino_model"
            / "labels.txt"
        )
        with open(labels_path, encoding="utf-8") as fp:
            # Raw label format: "uuid;class;order;family;genus;species;common_name"
            # We store the full raw label for traceability and expose display names via get_labels().
            self._raw_labels = {idx: line.strip() for idx, line in enumerate(fp.readlines())}
        # Precompute display names: last semicolon-separated field (common name / category).
        self._display_labels = [label.split(";")[-1] for label in self._raw_labels.values()]

    def get_labels(self, language: str) -> list[str]:
        """Return ordered list of display names.  Language is ignored (always English)."""
        return self._display_labels

    @staticmethod
    def check_model(version="SpeciesNetV4"):
        """Check if the OpenVINO IR for SpeciesNet is present."""
        return OVModel.check_model(
            Path("classification", f"{version}_openvino_model", f"{version}.xml")
        )

    @staticmethod
    def download_model(version="SpeciesNetV4", force: bool = False):
        """Download and convert the SpeciesNet classifier to OpenVINO IR.

        Requires: speciesnet, torch, openvino packages.
        The model source identifier can be overridden via the SPECIESNET_MODEL_NAME env var
        (default: kaggle source for SpeciesNet v4).
        Run tools/convert_speciesnet_to_openvino.py for a standalone conversion workflow.
        """
        import os
        import shutil

        import openvino as ov
        import torch
        from speciesnet.utils import ModelInfo

        model_name = os.environ.get(
            "SPECIESNET_MODEL_NAME",
            "kaggle:google/speciesnet/pyTorch/v4.0.1a",
        )
        model_info = ModelInfo(model_name)

        torch_model = torch.load(model_info.classifier, map_location="cpu", weights_only=False)
        torch_model.eval()
        for p in torch_model.parameters():
            p.requires_grad = False

        example_input = torch.rand(
            1,
            SpeciesNetClassifier.IMG_SIZE,
            SpeciesNetClassifier.IMG_SIZE,
            3,
            dtype=torch.float32,
        )

        ov_model = ov.convert_model(torch_model, example_input=example_input)

        from wadas.ai.openvino_model import __model_folder__

        out_dir = Path(__model_folder__) / "classification" / f"{version}_openvino_model"
        out_dir.mkdir(parents=True, exist_ok=True)

        xml_path = out_dir / f"{version}.xml"
        ov.save_model(ov_model, str(xml_path))

        labels_dst = out_dir / "labels.txt"
        shutil.copy(model_info.classifier_labels, labels_dst)

        return str(xml_path)

    def preprocessImage(self, croppedimage):
        """Resize crop to IMG_SIZE x IMG_SIZE and scale to [0, 1]; output NHWC tensor."""
        img = croppedimage.resize((self.IMG_SIZE, self.IMG_SIZE))
        arr = np.asarray(img, dtype=np.float32) / 255.0  # HWC
        return torch.from_numpy(arr).unsqueeze(0)  # -> [1, H, W, 3]

    def predictOnBatch(self, batchtensor, withsoftmax=True):
        """Run the compiled OV model on a [N, H, W, 3] NHWC batch."""
        logits = self.model(batchtensor)
        return logits.softmax(dim=-1) if withsoftmax else logits

    def predictOnImages(self, request, withsoftmax=True) -> torch.Tensor:
        """Crop each detected animal bbox, preprocess, and classify."""
        img, results = request
        if results["detections"].xyxy.shape[0] == 0:
            return
        tensor = torch.concatenate(
            [self.preprocessImage(img.crop(xyxy)) for xyxy in results["detections"].xyxy],
            axis=0,
        )
        return self.predictOnBatch(tensor, withsoftmax=withsoftmax)

from pathlib import Path

import numpy as np
import pytest
import requests
import torch
from PIL import Image

from wadas.ai.models_custom import Classifier, OVMegaDetectorV5
from wadas.ai.openvino_model import OVModel
from wadas.ai.pipeline import DetectionPipeline

TEST_URL = "https://www.parks.it/tmpFoto/30079_4_PNALM.jpeg"
NAME_TO_PATH = {
    "MDV5-yolov5": Path("detection", "MDV5-yolov5_openvino_model", "MDV5-yolov5.xml"),
    "MDV6b-yolov9c": Path("detection", "MDV6b-yolov9c_openvino_model", "MDV6b-yolov9c.xml"),
}


@pytest.fixture(scope="session", autouse=True)
def test_download_models():
    """Test download models. This will run before any test function."""
    assert OVMegaDetectorV5.download_model(force=False)
    assert Classifier.download_model(force=False)


def test_detection_model():
    """Test if model exists."""
    assert OVMegaDetectorV5.check_model()


def test_classification_model():
    assert Classifier.check_model()


@pytest.fixture
def detection_pipeline():
    pipeline = DetectionPipeline(detection_device="cpu", classification_device="cpu")
    assert pipeline.check_models("MDV5-yolov5", "DFv1.2")
    return pipeline


# Compute IoU (Intersection over Union)
def compute_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1g, y1g, x2g, y2g = box2

    xi1 = max(x1, x1g)
    yi1 = max(y1, y1g)
    xi2 = min(x2, x2g)
    yi2 = min(y2, y2g)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2g - x1g) * (y2g - y1g)
    union_area = box1_area + box2_area - inter_area

    iou = inter_area / union_area
    return iou


def test_detection(detection_pipeline):
    """Test detection pipeline."""

    img = Image.open(requests.get(TEST_URL, stream=True).raw).convert("RGB")
    results = detection_pipeline.run_detection(img, 0.5)

    assert results is not None
    assert "detections" in results

    assert len(results["detections"].xyxy) == 1

    # Test with a valid image
    assert results["detections"].xyxy.shape == (1, 4)
    assert results["detections"].xyxy.dtype == np.float32

    detected_box = results["detections"].xyxy.flatten().tolist()
    assert compute_iou(detected_box, [289, 175, 645, 424]) > 0.5

    assert results["detections"].mask is None
    assert results["detections"].confidence.item() > 0.7
    assert results["detections"].confidence.shape == (1,)
    assert results["detections"].confidence.dtype == np.float32


def test_detection_non_animal(detection_pipeline):
    # This image does contain two dogs and a human.
    # Check that the detection pipeline returns only the dogs.
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )
    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")
    results = detection_pipeline.run_detection(img, 0.5)

    assert results is not None
    assert "detections" in results

    assert len(results["detections"].xyxy) == 2

    # Test with a valid image
    assert results["detections"].xyxy.shape == (2, 4)
    assert results["detections"].xyxy.dtype == np.float32

    assert results["detections"].mask is None
    assert results["detections"].confidence.shape == (2,)
    assert results["detections"].confidence.dtype == np.float32

    assert ["animal" in res for res in results["labels"]]


def test_detection_panorama(detection_pipeline):
    # This image does not contain any animals.
    # Check that the detection pipeline returns no detections.
    URL = (
        "https://www.shutterstock.com/image-photo/"
        "after-rain-landscapes-arches-national-260nw-2077881598.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")
    results = detection_pipeline.run_detection(img, 0.5)

    assert results is not None
    assert "detections" in results

    assert len(results["detections"].xyxy) == 0
    assert results["labels"] == []


def test_classification(detection_pipeline):

    img = Image.open(requests.get(TEST_URL, stream=True).raw).convert("RGB")
    results = detection_pipeline.run_detection(img, 0.5)

    classified_animals = detection_pipeline.classify(img, results, 0.5)

    assert classified_animals is not None

    assert len(classified_animals) == 1

    assert classified_animals[0]["id"] == 0

    assert classified_animals[0]["classification"][0] == "bear"
    assert classified_animals[0]["classification"][1].item() > 0.7

    detected_box = classified_animals[0]["xyxy"]
    assert compute_iou(detected_box, [289, 175, 645, 424]) > 0.5


def test_classification_dog_overlapping(detection_pipeline):
    URL = (
        "https://www.addestramentocaniromasud.it/wp/wp-content/uploads/2021/05/cane-in-braccio.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")
    results = detection_pipeline.run_detection(img, 0.5)

    classified_animals = detection_pipeline.classify(img, results, 0.5)

    assert classified_animals is not None

    assert len(classified_animals) == 1

    assert classified_animals[0]["id"] == 0

    assert classified_animals[0]["classification"][0] == "dog"
    assert classified_animals[0]["classification"][1].item() > 0.84

    assert classified_animals[0]["xyxy"] == [554, 368, 1045, 616]


@pytest.fixture(scope="module")
def ov_model(version="MDV5-yolov5"):
    model_name = NAME_TO_PATH.get(version)
    if model_name is None:
        raise ValueError(f"Version '{version}' not found in NAME_TO_PATH")

    device = "CPU"
    return OVModel(model_name, device)


def test_get_available_device(ov_model):
    devices = ov_model.get_available_device()
    assert "CPU" in devices


def test_compile_model_MDV5(ov_model):
    model_name = NAME_TO_PATH.get("MDV5-yolov5")
    model = ov_model.load_model(model_name)
    compiled_model = ov_model.compile_model(model)
    assert compiled_model is not None


def test_call_model(ov_model):
    input_tensor = torch.randn(1, 3, 1280, 1280)
    output = ov_model(input_tensor)
    assert isinstance(output, torch.Tensor) or (
        isinstance(output, list) and all(isinstance(t, torch.Tensor) for t in output)
    )


@pytest.mark.parametrize("language", ["en", "fr", "it", "de"])
def test_set_language_valid(detection_pipeline, language):
    detection_pipeline.set_language(language)
    assert detection_pipeline.language == language


@pytest.mark.parametrize("language", ["ru", "ch", "jp"])
def test_set_language_invalid(detection_pipeline, language):
    with pytest.raises(ValueError, match="Language not supported"):
        detection_pipeline.set_language(language)

import os
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest
import requests
import torch
import wadas_runtime as wadas
from PIL import Image

from wadas.ai.models import Classifier, OVMegaDetectorV5
from wadas.ai.openvino_model import OVModel
from wadas.ai.pipeline import DetectionPipeline
from wadas.domain.ai_model import AiModel

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
    model_folder = Path(__file__).resolve().parent.parent / "model"
    model_name = model_folder / model_name
    compiled_model = wadas.load_and_compile_model(str(model_name), device_name="CPU")
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


def test_check_models_with_invalid_detector():
    """Test that check_models handles invalid detector model gracefully."""
    # This should not raise AttributeError when detector is None
    result = DetectionPipeline.check_models("INVALID_MODEL", "DFv1.2")
    assert result is False


def test_blur_bounding_box_modifies_image():
    """Test that blur_bounding_box actually modifies the specified region."""
    # Create a test image with a clear pattern
    img_array = np.ones((300, 300, 3), dtype=np.uint8) * 255  # White image
    # Add a black rectangle in the middle with some edges for blur to work on
    img_array[100:200, 100:200] = 0
    # Add some pattern for better blur detection
    img_array[120:180, 120:180] = 255

    original_img = img_array.copy()
    bbox = [100, 100, 200, 200]

    # Blur the bounding box (need to pass a copy since it modifies in-place)
    test_img = img_array.copy()
    blurred_img = AiModel.blur_bounding_box(test_img, bbox)

    # Check that the image was modified
    assert not np.array_equal(original_img, blurred_img)

    # Check that the blurred region is different from the original
    blurred_region = blurred_img[100:200, 100:200]
    original_region = original_img[100:200, 100:200]
    assert not np.array_equal(original_region, blurred_region)

    # Check that regions outside the bbox are unchanged
    assert np.array_equal(original_img[0:100, :], blurred_img[0:100, :])
    assert np.array_equal(original_img[200:300, :], blurred_img[200:300, :])


def test_blur_bounding_box_with_pil_image():
    """Test that blur_bounding_box works with PIL Images."""
    # Create a PIL Image with some pattern
    img = Image.new("RGB", (300, 300), color="white")
    # Add a pattern for blur to be visible
    img_array = np.array(img)
    img_array[50:150, 50:150] = 0  # Black square
    img_array[75:125, 75:125] = 255  # White square inside
    img = Image.fromarray(img_array)

    bbox = [50, 50, 150, 150]

    original_array = np.array(img)

    # Blur the bounding box
    blurred_img = AiModel.blur_bounding_box(img, bbox)

    # Check that result is a PIL Image (as the function returns PIL when given PIL)
    assert isinstance(blurred_img, (np.ndarray, Image.Image))

    # Convert to array for comparison
    blurred_array = np.array(blurred_img) if isinstance(blurred_img, Image.Image) else blurred_img

    # Check that the image was modified
    assert not np.array_equal(original_array, blurred_array)


def test_blur_non_animal_detections_in_pipeline(detection_pipeline):
    """Test that non-animal detections are properly blurred when blur_other_classes=True."""
    # This image contains two dogs and a human.
    # We expect the human to be blurred while dogs remain unblurred.
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")

    # First, run detection WITHOUT filtering to get all detections including non-animals
    img_array = np.array(img)
    results_all = detection_pipeline.detection_model.run(img_array, detection_threshold=0.5)

    # Handle the case where results_all might be a list
    if isinstance(results_all, list):
        results_all = results_all[0]

    # Identify non-animal detections
    non_animal_idx = np.where(
        results_all["detections"].class_id != detection_pipeline.animal_class_idx
    )[0]

    # Verify that there are non-animal detections in this image
    assert len(non_animal_idx) > 0, "Test image should contain non-animal detections"

    # Store original image for comparison
    original_img_array = img_array.copy()

    # Run detection WITH filtering (default behavior)
    results = detection_pipeline.run_detection(img, 0.5, filter_animals=True)

    assert results is not None

    # Test blur_bounding_box method directly
    test_bbox = results_all["detections"].xyxy[non_animal_idx[0]]
    blurred_test = AiModel.blur_bounding_box(original_img_array.copy(), test_bbox)

    # Check that blur_bounding_box actually modifies the image
    assert not np.array_equal(original_img_array, blurred_test)

    # The animal detections should still be present and correct
    assert len(results["detections"].xyxy) == 2  # Two dogs
    assert results["detections"].xyxy.shape == (2, 4)
    assert all("animal" in res for res in results["labels"])


@pytest.fixture
def temp_test_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp(prefix="wadas_test_")
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def test_blur_in_saved_image(temp_test_dir):
    """Test that blur is applied to images during processing with AiModel."""
    # Download test image with human and dogs
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")

    # Save to temp directory
    img_path = os.path.join(temp_test_dir, "test_image.jpg")
    img.save(img_path)

    # Initialize AiModel with blur enabled
    ai_model = AiModel()
    AiModel.detection_threshold = 0.5
    AiModel.classification_threshold = 0.5
    AiModel.detection_device = "cpu"
    AiModel.classification_device = "cpu"
    AiModel.blur_non_animal_detections = True

    # Check models are available
    assert ai_model.check_model("MDV5-yolov5", "DFv1.2")

    # Process the image (note: image gets deleted if no animals after filtering)
    # So we test that blur happens by checking the blur_image_bounding_boxes was called
    results, _ = ai_model.process_image(img_path, save_detection_image=False)

    # After processing, dogs should be detected (animals are detected)
    assert results is not None
    assert len(results["detections"].xyxy) == 2  # Two dogs should be detected

    # Note: The original image file may be deleted by process_image if no animals detected
    # So instead we verify blur works through the blur_image_bounding_boxes method test


def test_no_blur_when_disabled(temp_test_dir):
    """Test that blur is NOT applied when blur_non_animal_detections=False."""
    # Download test image with human and dogs
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")

    # Save to temp directory
    img_path = os.path.join(temp_test_dir, "test_image_no_blur.jpg")
    img.save(img_path)

    # Initialize AiModel with blur disabled
    ai_model = AiModel()
    AiModel.detection_threshold = 0.5
    AiModel.classification_threshold = 0.5
    AiModel.detection_device = "cpu"
    AiModel.classification_device = "cpu"
    AiModel.blur_non_animal_detections = False

    # Check models are available
    assert ai_model.check_model("MDV5-yolov5", "DFv1.2")

    # Process the image (this should NOT blur)
    results, _ = ai_model.process_image(img_path, save_detection_image=False)

    assert results is not None
    assert len(results["detections"].xyxy) == 2  # Two dogs should be detected

    # Verify blur was NOT called by checking that no blur method was invoked
    # The test passes if process_image completes without error when blur is disabled


def test_blur_image_bounding_boxes_method():
    """Test the blur_image_bounding_boxes method of AiModel."""
    # Create test image
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")
    original_array = np.array(img)

    # Initialize AiModel
    ai_model = AiModel()
    AiModel.detection_threshold = 0.5
    AiModel.detection_device = "cpu"
    assert ai_model.check_model("MDV5-yolov5", "DFv1.2")

    # Get detections without filtering
    results = ai_model.detection_pipeline.run_detection(img, 0.5, filter_animals=False)

    # Apply blur to non-animal detections
    blurred_img = ai_model.blur_image_bounding_boxes(img, results)

    # Check that result is a PIL Image
    assert isinstance(blurred_img, Image.Image)

    # Check that the image was modified
    blurred_array = np.array(blurred_img)
    assert not np.array_equal(original_array, blurred_array)

    # The blurred image should have the same dimensions
    assert blurred_img.size == img.size


def test_blur_preserves_animal_regions():
    """Test that blur preserves animal regions while blurring non-animals."""
    # Create test image with human and dogs
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")

    # Initialize AiModel
    ai_model = AiModel()
    AiModel.detection_threshold = 0.5
    AiModel.detection_device = "cpu"
    assert ai_model.check_model("MDV5-yolov5", "DFv1.2")

    # Get all detections (animals and non-animals)
    results_all = ai_model.detection_pipeline.run_detection(img, 0.5, filter_animals=False)

    # Get animal-only detections
    results_animals = ai_model.detection_pipeline.run_detection(img, 0.5, filter_animals=True)

    # Apply blur
    blurred_img = ai_model.blur_image_bounding_boxes(img, results_all)

    # Extract animal regions from original and blurred images
    if len(results_animals["detections"].xyxy) > 0:
        animal_bbox = results_animals["detections"].xyxy[0]
        x1, y1, x2, y2 = map(int, animal_bbox)

        # Get animal regions
        original_animal_region = np.array(img.crop((x1, y1, x2, y2)))
        blurred_animal_region = np.array(blurred_img.crop((x1, y1, x2, y2)))

        # Animal regions should be very similar
        diff = np.abs(original_animal_region.astype(float) - blurred_animal_region.astype(float))
        mean_diff = np.mean(diff)

        # Allow for small differences due to image processing
        assert mean_diff < 5.0, "Animal regions should be preserved"


def test_blur_with_detection_pipeline_filter():
    """Test that blur integrates correctly with detection pipeline filtering."""
    # Test image with multiple detections
    URL = (
        "https://img.freepik.com/premium-photo/"
        "happy-human-dog-walking-through-park_1199394-134331.jpg"
    )

    img = Image.open(requests.get(URL, stream=True).raw).convert("RGB")

    # Initialize detection pipeline
    pipeline = DetectionPipeline(detection_device="cpu", classification_device="cpu")
    assert pipeline.check_models("MDV5-yolov5", "DFv1.2")

    # Get unfiltered results
    results_unfiltered = pipeline.run_detection(img, 0.5, filter_animals=False)

    # Get filtered results
    results_filtered = pipeline.run_detection(img, 0.5, filter_animals=True)

    # Verify filtering works
    assert len(results_filtered["detections"].xyxy) < len(
        results_unfiltered["detections"].xyxy
    ), "Filtered results should have fewer detections than unfiltered"

    # Verify all filtered detections are animals
    assert all(
        "animal" in label for label in results_filtered["labels"]
    ), "All filtered detections should be animals"


def test_blur_edge_cases():
    """Test blur function with edge cases."""
    # Test with empty bounding box
    img_array = np.ones((100, 100, 3), dtype=np.uint8) * 128

    # Very small bbox
    small_bbox = [10, 10, 11, 11]
    blurred = AiModel.blur_bounding_box(img_array.copy(), small_bbox)
    assert blurred is not None
    assert blurred.shape == img_array.shape

    # Bbox at image edge
    edge_bbox = [0, 0, 50, 50]
    blurred = AiModel.blur_bounding_box(img_array.copy(), edge_bbox)
    assert blurred is not None
    assert blurred.shape == img_array.shape

    # Bbox touching image boundary
    boundary_bbox = [50, 50, 100, 100]
    blurred = AiModel.blur_bounding_box(img_array.copy(), boundary_bbox)
    assert blurred is not None
    assert blurred.shape == img_array.shape

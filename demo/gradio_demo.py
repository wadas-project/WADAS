import gradio as gr
from wadas.domain.ai_model import AiModel

ai_model = AiModel()
url = (
    "https://www.provincia.bz.it/agricoltura-foreste/fauna-caccia-pesca/images/braunbaer_6016_L.jpg"
)


def detection_from_url(url):

    det_data = ai_model.process_image_from_url(url, "test_image", True)
    img_path, det_results, detected_img_path = det_data
    return img_path, det_results


def classification_from_path(img_path, det_results):

    if len(det_results["detections"].xyxy) > 0:
        print("Running classification on detection result(s)...")
        img_path, classified_animals = ai_model.classify(img_path, det_results)
        str = (
            f"Found {len(classified_animals)} animal{'s' if len(classified_animals) > 1 else ''}:\n"
        )
        for animals in classified_animals:
            animal, confidence = animals["classification"]
            str += f"\t - Class: {animal}, confidence: {confidence*100:.2f}%\n"

        return str
    else:
        return "No animal found"


def process_url(url):
    # 1: Detection
    detection_path, det_results = detection_from_url(url)

    # 2: Classification
    classification_result = classification_from_path(detection_path, det_results)
    return detection_path, classification_result


demo = gr.Interface(
    fn=process_url,
    inputs=gr.Textbox(label="Image URL"),
    outputs=[
        gr.Image(label="Detection Results"),
        gr.Textbox(label="Classification Results"),
    ],
    title="WADAS Demo",
    description="Enter a URL to get the detection and classification",
)

demo.launch()

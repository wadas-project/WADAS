from wadas.ai.object_counter import ObjectCounter
import argparse


import cv2


def main(video_path):

    model_path = "MDV6b-yolov9c_openvino_model"

    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Error reading video file"

    # region_points = [(640//2, 350), (640//2, 384)]                                      # line counting
    # region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360)]  # rectangle region
    # region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360), (20, 400)]   # polygon region

    w, h, fps = (
        int(cap.get(x))
        for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS)
    )

    delta = 200
    region_points = [(w, h - delta), (w - delta, h)]

    # Initialize object counter object
    counter = ObjectCounter(
        show=True,  # display the output
        region=region_points,  # pass region points
        model=model_path,  # model for object counting.
        classes=[0],  # count specific classes
    )

    # Process video
    frames = []
    while cap.isOpened():
        success, im0 = cap.read()

        if not success:
            break

        frames.append(im0)

    results = counter.process_frames(frames)
    print(results)  # access the output

    cap.release()
    cv2.destroyAllWindows()  # destroy all opened windows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("video", type=str, help="Path to the video file")
    args = parser.parse_args()

    main(args.video)

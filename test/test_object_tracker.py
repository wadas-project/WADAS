import numpy as np

from wadas.ai.object_tracker import KalmanFilter, ObjectTracker, compute_iou


def test_kalman_filter_initialization():
    initial_value = [0, 0, 1, 1]
    kf = KalmanFilter(initial_value)
    assert np.array_equal(kf.x, np.array(initial_value, dtype=np.float32))
    assert kf.dim == 2
    assert kf.P.shape == (4, 4)
    assert kf.Q.shape == (4, 4)
    assert kf.R.shape == (2, 2)


def test_kalman_filter_update():
    initial_value = [0, 0, 1, 1]
    kf = KalmanFilter(initial_value)
    measurement = [1, 1]
    updated_state = kf.update(measurement)
    assert updated_state.shape == (4,)


def test_compute_iou():
    box1 = [0, 0, 2, 2]
    box2 = [1, 1, 3, 3]
    iou = compute_iou(box1, box2)
    assert 0 <= iou <= 1


def test_object_tracker_initialization():
    ot = ObjectTracker()
    assert ot.trackers == {}
    assert ot.next_id == 0


def test_object_tracker_compute_centroid():
    ot = ObjectTracker()
    xyxy = [0, 0, 2, 2]
    centroid = ot.compute_centroid(xyxy)
    assert centroid == (1, 1)


def test_object_tracker_associate_detections():
    ot = ObjectTracker()
    detections = [{"xyxy": [0, 0, 2, 2], "class_probs": {"class1": 0.9}}]
    associations = ot.associate_detections(detections)
    assert len(associations) == 1


def test_object_tracker_update():
    ot = ObjectTracker()
    detections = [{"xyxy": [0, 0, 2, 2], "class_probs": {"class1": 0.9}}]
    img_size = (640, 480)
    updated_tracks = ot.update(detections, img_size)
    assert len(updated_tracks) == 1
    assert "id" in updated_tracks[0]
    assert "classification" in updated_tracks[0]
    assert "xyxy" in updated_tracks[0]

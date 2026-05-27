from functools import lru_cache
from ultralytics import YOLO


@lru_cache(maxsize=1)
def get_yolo_model():
    return YOLO("yolov8n.pt")
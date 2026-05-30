import cv2
import numpy as np


def analyze_scene_from_objects(detected_objects: list):
    person_count = sum(
        1 for obj in detected_objects
        if obj["label"] == "person"
    )

    vehicle_labels = [
        "car",
        "truck",
        "bus",
        "motorcycle",
        "bicycle"
    ]

    vehicle_count = sum(
        1 for obj in detected_objects
        if obj["label"] in vehicle_labels
    )

    total_count = person_count + vehicle_count

    if person_count >= 50:
        density_tier = "CRITICAL"

    elif person_count >= 25:
        density_tier = "HIGH"

    elif person_count >= 10:
        density_tier = "MEDIUM"

    else:
        density_tier = "LOW"

    return {
        "person_count": person_count,
        "vehicle_count": vehicle_count,
        "total_entities": total_count,
        "density_tier": density_tier,
        "abnormal_cluster_detected": person_count >= 25
    }
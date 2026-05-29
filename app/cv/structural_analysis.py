import cv2
import numpy as np


def analyze_structure(image_path: str, detected_objects: list = None):
    image = cv2.imread(image_path)

    if image is None:
        return {
            "error": "Image could not be loaded"
        }

    max_width = 1000

    height, width = image.shape[:2]

    if width > max_width:
        scale = max_width / width
        new_height = int(height * scale)
        image = cv2.resize(image, (max_width, new_height))

    if detected_objects is None:
        detected_objects = []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 40, 130)

    edge_density = np.sum(edges > 0) / edges.size

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=40,
        minLineLength=25,
        maxLineGap=12
    )

    angle_variance = 0
    line_count = 0

    if lines is not None:
        line_count = len(lines)

        angles = []

        for line in lines:
            x1, y1, x2, y2 = line[0]

            angle = np.degrees(
                np.arctan2(y2 - y1, x2 - x1)
            )

            angles.append(angle)

        angle_variance = np.var(angles)

    labels = [
        obj["label"]
        for obj in detected_objects
    ]

    vehicle_labels = [
        "car",
        "truck",
        "bus",
        "motorcycle",
        "bicycle"
    ]

    vehicle_count = sum(
        1 for label in labels
        if label in vehicle_labels
    )

    person_count = labels.count("person")

    structural_scene_detected = (
        line_count >= 20
        or edge_density >= 0.02
        or angle_variance >= 300
    )

    damage_score = (
        edge_density * 220
        + min(angle_variance / 40, 30)
        + min(line_count / 180, 12)
    )

    if person_count >= 3 and not structural_scene_detected:
        damage_score *= 0.5

    if vehicle_count >= 8:
        damage_score *= 0.35

    elif vehicle_count >= 5:
        damage_score *= 0.50

    damage_score = min(
        round(float(damage_score), 2),
        100
    )

    if not structural_scene_detected:
        damage_tier = "UNKNOWN"

    elif damage_score >= 50:
        damage_tier = "SEVERE"

    elif damage_score >= 40:
        damage_tier = "MODERATE"

    elif damage_score >= 15:
        damage_tier = "MINOR"

    else:
        damage_tier = "NONE"

    return {
        "damage_score": damage_score,
        "edge_density": round(float(edge_density), 4),
        "line_count": line_count,
        "line_angle_variance": round(float(angle_variance), 2),
        "damage_tier": damage_tier
    }
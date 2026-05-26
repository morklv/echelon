import cv2
import numpy as np


def analyze_fire_smoke(image_path: str):
    image = cv2.imread(image_path)

    if image is None:
        return {
            "error": "Image could not be read"
        }

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    total_pixels = image.shape[0] * image.shape[1]

    fire_lower_1 = np.array([0, 100, 130])
    fire_upper_1 = np.array([25, 255, 255])

    fire_lower_2 = np.array([170, 100, 130])
    fire_upper_2 = np.array([180, 255, 255])

    fire_mask_1 = cv2.inRange(hsv, fire_lower_1, fire_upper_1)
    fire_mask_2 = cv2.inRange(hsv, fire_lower_2, fire_upper_2)

    fire_mask = cv2.bitwise_or(fire_mask_1, fire_mask_2)

    smoke_lower = np.array([0, 0, 25])
    smoke_upper = np.array([180, 65, 190])

    smoke_mask = cv2.inRange(hsv, smoke_lower, smoke_upper)

    kernel = np.ones((5, 5), np.uint8)

    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
    smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, kernel)
    smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_CLOSE, kernel)

    fire_pixels = cv2.countNonZero(fire_mask)
    smoke_pixels = cv2.countNonZero(smoke_mask)

    fire_ratio = fire_pixels / total_pixels
    smoke_ratio = smoke_pixels / total_pixels

    texture_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    mean_brightness = float(np.mean(gray))

    fire_score = min(fire_ratio * 220, 1.0)
    smoke_score = min(smoke_ratio * 5.5, 1.0)

    vehicle_scene_detected = (
        smoke_ratio > 0.45
        and texture_variance > 1500
    )

    if mean_brightness > 135 and smoke_ratio < 0.30:
        smoke_score *= 0.45

    if texture_variance > 900 and fire_ratio < 0.002:
        smoke_score *= 0.45

    if vehicle_scene_detected:
        smoke_score *= 0.15
        fire_score *= 0.25

    if fire_ratio < 0.002:
        fire_score *= 0.35

    real_fire_signal = (
        fire_ratio >= 0.0025
        and fire_score >= 0.40
    )

    real_smoke_signal = (
        smoke_ratio >= 0.12
        and smoke_score >= 0.45
        and mean_brightness < 175
    )

    hazard_confidence = max(fire_score, smoke_score)

    if real_fire_signal and real_smoke_signal:
        hazard_tier = "ACTIVE_FIRE"

    elif real_fire_signal:
        hazard_tier = "FIRE_VISIBLE"

    elif real_smoke_signal:
        hazard_tier = "SMOKE_PRESENT"

    elif hazard_confidence > 0.35:
        hazard_tier = "POSSIBLE_HAZARD"

    else:
        hazard_tier = "NO_VISIBLE_FIRE_SMOKE"

    return {
        "fire_pixel_ratio": round(fire_ratio, 4),
        "smoke_pixel_ratio": round(smoke_ratio, 4),
        "texture_variance": round(texture_variance, 2),
        "mean_brightness": round(mean_brightness, 2),
        "fire_score": round(fire_score, 3),
        "smoke_score": round(smoke_score, 3),
        "hazard_confidence": round(hazard_confidence, 3),
        "hazard_tier": hazard_tier
    }
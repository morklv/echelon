import cv2
import numpy as np


def analyze_fire_smoke(image_path: str):
    image = cv2.imread(image_path)

    if image is None:
        return {"error": "Image could not be read"}

    max_width = 1000

    height, width = image.shape[:2]

    if width > max_width:
        scale = max_width / width
        new_height = int(height * scale)
        image = cv2.resize(image, (max_width, new_height))

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = image.shape[:2]
    total_pixels = height * width

    h, s, v = cv2.split(hsv)

    # More restrictive fire detection:
    # Requires bright red/orange/yellow, not just red paint.
    fire_red = cv2.inRange(hsv, np.array([0, 140, 170]), np.array([18, 255, 255]))
    fire_orange = cv2.inRange(hsv, np.array([18, 120, 180]), np.array([45, 255, 255]))

    fire_mask = cv2.bitwise_or(fire_red, fire_orange)

    # Smoke detection:
    # Gray, medium brightness, low saturation.
    smoke_mask = cv2.inRange(hsv, np.array([0, 0, 60]), np.array([180, 55, 185]))

    # Suppress very bright sky/cloud regions.
    bright_sky_mask = cv2.inRange(hsv, np.array([0, 0, 185]), np.array([180, 70, 255]))
    smoke_mask[bright_sky_mask > 0] = 0

    # Suppress bottom road/asphalt zone unless there is fire nearby.
    bottom_start = int(height * 0.65)
    smoke_mask[bottom_start:, :] = 0

    kernel = np.ones((5, 5), np.uint8)

    fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
    smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_OPEN, kernel)
    smoke_mask = cv2.morphologyEx(smoke_mask, cv2.MORPH_CLOSE, kernel)

    # Remove huge flat background regions from smoke mask.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(smoke_mask)

    filtered_smoke = np.zeros_like(smoke_mask)

    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h_box = stats[i, cv2.CC_STAT_HEIGHT]

        area_ratio = area / total_pixels
        width_ratio = w / width
        height_ratio = h_box / height

        # Reject massive sky/road-like regions.
        if area_ratio > 0.35:
            continue

        # Reject long horizontal bands.
        if width_ratio > 0.55 and height_ratio < 0.25:
            continue

        # Reject tiny noise.
        if area_ratio < 0.001:
            continue

        filtered_smoke[labels == i] = 255

    smoke_mask = filtered_smoke

    fire_pixels = cv2.countNonZero(fire_mask)
    smoke_pixels = cv2.countNonZero(smoke_mask)

    fire_ratio = fire_pixels / total_pixels
    smoke_ratio = smoke_pixels / total_pixels

    texture_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    mean_brightness = float(np.mean(gray))

    # Fire should not be triggered by red infrastructure alone.
    fire_score = min(fire_ratio * 40, 1.0)

    # Smoke needs meaningful filtered smoke area.
    smoke_score = min(smoke_ratio * 8, 1.0)

    # Extra penalty when scene has weak fire evidence.
    if fire_ratio < 0.006:
        fire_score *= 0.35

    if smoke_ratio < 0.015:
        smoke_score *= 0.35

    real_fire_signal = fire_score >= 0.40 and fire_ratio >= 0.006
    real_smoke_signal = smoke_score >= 0.35 and smoke_ratio >= 0.015

    hazard_confidence = max(fire_score, smoke_score)
    strong_smoke_signal = smoke_score >= 0.75 and smoke_ratio >= 0.08
    meaningful_fire_signal = fire_score >= 0.30 and fire_ratio >= 0.006

    if strong_smoke_signal and meaningful_fire_signal:
        hazard_tier = "ACTIVE_FIRE"

    elif real_fire_signal and real_smoke_signal:
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
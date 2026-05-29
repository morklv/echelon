import cv2

import numpy as np

def analyze_hazard(image_path: str, detected_objects: list = None):
    image = cv2.imread(image_path) #loads image from disk into opencv matrix
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
    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #converts image from BGR color space to HSV

    
    fire_lower = np.array([0, 120, 180])
    fire_upper = np.array([30, 255, 255])

    fire_mask = cv2.inRange(hsv, fire_lower, fire_upper)
    #creates binary mask: whire pixels = fire-colored regions

    fire_ratio = np.sum(fire_mask >0) / fire_mask.size
    #computes the fraction of image classified as fire-colored

    
    
    smoke_lower = np.array([0, 0, 40])
    # lower HSV boundary for smoke-like gray/dark pixels

    smoke_upper = np.array([180, 80, 220])
    # upper HSV boundary for smoke-like low-saturation pixels

    smoke_mask = cv2.inRange(hsv, smoke_lower, smoke_upper)
    # creates mask for smoke-colored pixels

    smoke_ratio = np.sum(smoke_mask > 0) / smoke_mask.size
    # calculates fraction of image that looks smoke-like

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # converts to grayscale

    labels = [obj["label"] for obj in detected_objects]


    traffic_light_count = labels.count("traffic light")

    person_count = labels.count("person")
    vehicle_labels = ["car", "truck", "bus", "motorcycle", "bicycle"]
    vehicle_count = sum(
        1 for label in labels
        if label in vehicle_labels
    )
    urban_scene_detected = person_count >= 3 and vehicle_count >= 1

    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    

    hazard_tier = "NONE"
    # default fallback classification

    hazard_confidence = 0.0


    if traffic_light_count >= 2 and fire_ratio < 0.05:
        hazard_tier = "NONE"
        hazard_confidence = 0.0

        return {
            "fire_pixel_ratio": round(float(fire_ratio), 4),
            "smoke_pixel_ratio": round(float(smoke_ratio), 4),
            "texture_variance": round(float(variance), 2),
            "hazard_confidence": hazard_confidence,
            "hazard_tier": hazard_tier
        }

    if urban_scene_detected and fire_ratio < 0.04:
        hazard_tier = "NONE"
        hazard_confidence = 0.0
        return {
            "fire_pixel_ratio": round(float(fire_ratio), 4),
            "smoke_pixel_ratio": round(float(smoke_ratio), 4),
            "texture_variance": round(float(variance), 2),
            "hazard_confidence": hazard_confidence,
            "hazard_tier": hazard_tier
        }

    if fire_ratio > 0.08:
        hazard_tier = "ACTIVE_FIRE"

    elif fire_ratio > 0.04 and variance > 120:
        hazard_tier = "ACTIVE_FIRE"

    elif fire_ratio > 0.005:
        hazard_tier = "SMOKE_OR_HEAT"

    elif smoke_ratio > 0.25 and fire_ratio < 0.01:
        hazard_tier = "SMOKE_OR_HEAT"

    else:
        hazard_tier = "NONE"



    fire_score = min(fire_ratio / 0.08, 1.0)

    texture_score = min(variance / 500, 1.0)

    hazard_confidence = (fire_score * 0.7) + (texture_score * 0.3)    

    return {
        "fire_pixel_ratio": round(float(fire_ratio), 4),

        "smoke_pixel_ratio": round(float(smoke_ratio), 4),


        "texture_variance": round(float(variance), 2),


        "hazard_confidence": round(float(hazard_confidence), 2),


        "hazard_tier": hazard_tier

    }
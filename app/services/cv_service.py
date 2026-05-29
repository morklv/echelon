import cv2

from app.services.yolo_model import get_yolo_model
from app.cv.hazard_detection import analyze_hazard
from app.cv.structural_analysis import analyze_structure
from app.cv.intelligence_fusion import fuse_intelligence
from app.cv.crowd_analysis import analyze_scene_from_objects
from app.cv.traffic_activity import analyze_traffic_activity
from app.services.fire_smoke_service import analyze_fire_smoke


def analyze_image(image_path: str):
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

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = blur_score < 100

    model = get_yolo_model()

    results = model(
        image,
        imgsz=416,
        verbose=False
    )

    detected_objects = []

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        label = model.names[class_id]

        if confidence >= 0.50:
            detected_objects.append({
                "label": label,
                "confidence": round(confidence, 2)
            })

    scene_analysis = analyze_scene_from_objects(detected_objects)
    hazard_analysis = analyze_hazard(image_path, detected_objects)
    structural_analysis = analyze_structure(image_path, detected_objects)
    traffic_activity = analyze_traffic_activity(detected_objects)
    fire_smoke_analysis = analyze_fire_smoke(image_path)

    image_analysis = {
        "blur_score": round(float(blur_score), 2),
        "is_blurry": bool(is_blurry),
        "detected_objects": detected_objects,
        "hazard_analysis": hazard_analysis,
        "structural_analysis": structural_analysis,
        "scene_analysis": scene_analysis,
        "traffic_activity": traffic_activity,
        "fire_smoke_analysis": fire_smoke_analysis,
    }

    intelligence_fusion = fuse_intelligence(image_analysis)

    return {
        **image_analysis,
        "intelligence_fusion": intelligence_fusion
    }
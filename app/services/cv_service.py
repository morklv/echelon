import cv2
from ultralytics import YOLO

from app.cv.hazard_detection import analyze_hazard

from app.cv.structural_analysis import analyze_structure

from app.cv.intelligence_fusion import fuse_intelligence
# imports the module that combines CV outputs into one risk score

from app.cv.crowd_analysis import analyze_scene_from_objects
# imports scene assessment module that counts people/vehicles from YOLO results

from app.cv.traffic_activity import analyze_traffic_activity
# imports road/traffic activity analyzer

from app.services.fire_smoke_service import analyze_fire_smoke

model = YOLO("yolov8n.pt")

def analyze_image(image_path: str):
    image = cv2.imread(image_path)

    if image is None:
        return {
            "error": "Image could not be loaded"
        }

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = blur_score < 100
    
    results = model(image)

    detected_objects = []

    # uses YOLO detected objects to count people/vehicles

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
    # analyzes road activity using YOLO labels

    image_analysis = {
        "blur_score": round(float(blur_score), 2),
        # image quality score

        "is_blurry": bool(is_blurry),
        # true/false blur flag

        "detected_objects": detected_objects,
        # YOLO object detection results

        "hazard_analysis": hazard_analysis,
        # fire/smoke analysis

        "structural_analysis": structural_analysis,
        # structural damage analysis

        "scene_analysis": scene_analysis,
        # crowd/vehicle scene assessment

        "traffic_activity": traffic_activity,

        "fire_smoke_analysis": fire_smoke_analysis,

    }

    intelligence_fusion = fuse_intelligence(image_analysis)
    # combines all CV modules into one operational risk result

    return {
        **image_analysis,
        # includes all original image analysis fields

        "intelligence_fusion": intelligence_fusion
        # adds fused operational risk score
    }



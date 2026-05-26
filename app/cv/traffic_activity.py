def analyze_traffic_activity(detected_objects: list):
    # analyzes traffic and road activity using YOLO detections

    vehicle_labels = [
        "car",
        "truck",
        "bus",
        "motorcycle",
        "bicycle"
    ]
    # labels considered road vehicles

    vehicle_count = sum(
        1 for obj in detected_objects
        if obj["label"] in vehicle_labels
    )
    # counts detected vehicles

    person_count = sum(
        1 for obj in detected_objects
        if obj["label"] == "person"
    )
    # counts detected people

    total_road_entities = vehicle_count + person_count
    # total road-related entities

    if vehicle_count >= 8:
        traffic_density = "CRITICAL"
        # very crowded traffic scene

    elif vehicle_count >= 5:
        traffic_density = "HIGH"
        # heavy traffic activity

    elif vehicle_count >= 2:
        traffic_density = "MEDIUM"
        # moderate road activity

    elif vehicle_count >= 1:
        traffic_density = "LOW"
        # light traffic activity

    else:
        traffic_density = "NONE"
        # no meaningful traffic activity

    return {
        "vehicle_count": vehicle_count,
        # total vehicles detected

        "person_count": person_count,
        # total people detected

        "total_road_entities": total_road_entities,
        # total road-related entities

        "traffic_density": traffic_density,
        # overall road activity level

        "road_activity_detected": vehicle_count >= 1
        # whether meaningful road activity exists
    }
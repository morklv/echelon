def analyze_traffic_activity(detected_objects: list):

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

    person_count = sum(
        1 for obj in detected_objects
        if obj["label"] == "person"
    )

    total_road_entities = vehicle_count + person_count

    if vehicle_count >= 8:
        traffic_density = "CRITICAL"

    elif vehicle_count >= 5:
        traffic_density = "HIGH"

    elif vehicle_count >= 2:
        traffic_density = "MEDIUM"

    elif vehicle_count >= 1:
        traffic_density = "LOW"

    else:
        traffic_density = "NONE"

    return {
        "vehicle_count": vehicle_count,

        "person_count": person_count,

        "total_road_entities": total_road_entities,

        "traffic_density": traffic_density,

        "road_activity_detected": vehicle_count >= 1
    }
def fuse_intelligence(image_analysis: dict):

    traffic = image_analysis.get("traffic_activity") or {}
    traffic_density = traffic.get("traffic_density", "NONE")
    scene = image_analysis.get("scene_analysis") or {}
    density_tier = scene.get("density_tier", "LOW")
    hazard = image_analysis.get("hazard_analysis") or {}
    fire_smoke = image_analysis.get("fire_smoke_analysis") or {}
    structural = image_analysis.get("structural_analysis") or {}
    hazard_tier = hazard.get("hazard_tier", "NONE")
    fire_smoke_tier = fire_smoke.get("hazard_tier", "NONE")
    damage_tier = structural.get("damage_tier", "NONE")
    risk_score = 0

    if density_tier == "CRITICAL":
        risk_score += 10

    elif density_tier == "HIGH":
        risk_score += 8

    elif density_tier == "MEDIUM":
        risk_score += 7

    if hazard_tier == "ACTIVE_FIRE":
        risk_score += 45

    elif hazard_tier in ["SMOKE_OR_HEAT", "SMOKE_PRESENT"]:
        risk_score += 15

    if fire_smoke_tier == "ACTIVE_FIRE":
        risk_score += 55

    elif fire_smoke_tier == "SMOKE_PRESENT":
        risk_score += 10

    elif fire_smoke_tier == "POSSIBLE_HAZARD":
        risk_score += 5

    if damage_tier == "SEVERE":
        risk_score += 50

    elif damage_tier == "MODERATE":
        risk_score += 20

    elif damage_tier == "MINOR":
        risk_score += 10

    if traffic_density == "CRITICAL":
        risk_score += 10

    elif traffic_density == "HIGH":
        risk_score += 5

    elif traffic_density == "MEDIUM":
        risk_score += 3

    risk_score = min(risk_score, 100)


    if risk_score >= 50:
        risk_tier = "CRITICAL"


    elif risk_score >= 40:
        risk_tier = "HIGH"


    elif risk_score >= 25:
        risk_tier = "MEDIUM"


    else:
        risk_tier = "LOW"

    primary_hazard = fire_smoke_tier


    if primary_hazard in ["NONE", "NO_VISIBLE_FIRE_SMOKE", "UNKNOWN"]:
        primary_hazard = hazard_tier
 

    if risk_score >= 65:
        recommended_action = "Escalate immediately and dispatch field verification"


    elif risk_score >= 50:
        recommended_action = "Escalate for operator review"


    elif risk_score >= 25:
        recommended_action = "Monitor and verify with additional evidence"


    else:
        recommended_action = "Log and monitor"

    return {
        "overall_risk_score": risk_score,
        "risk_tier": risk_tier,
        "primary_hazard": primary_hazard,
        "fire_smoke_tier": fire_smoke_tier,
        "structural_damage": damage_tier,
        "recommended_action": recommended_action,
        "scene_density": density_tier,
        "traffic_density": traffic_density
    }
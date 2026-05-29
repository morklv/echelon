def fuse_intelligence(image_analysis: dict):
    # combines outputs from multiple CV modules into one operational risk score

    traffic = image_analysis.get("traffic_activity") or {}
    # extracts traffic activity analysis

    traffic_density = traffic.get("traffic_density", "NONE")
    # gets traffic density tier

    scene = image_analysis.get("scene_analysis") or {}
    # extracts crowd/vehicle scene assessment section

    density_tier = scene.get("density_tier", "LOW")
    # gets crowd density tier

    hazard = image_analysis.get("hazard_analysis") or {}
    # extracts old hazard/fire analysis section

    fire_smoke = image_analysis.get("fire_smoke_analysis") or {}
    # extracts dedicated fire/smoke analysis section

    structural = image_analysis.get("structural_analysis") or {}
    # extracts structural damage analysis section

    hazard_tier = hazard.get("hazard_tier", "NONE")
    # gets old hazard classification

    fire_smoke_tier = fire_smoke.get("hazard_tier", "NONE")
    # gets dedicated fire/smoke classification

    damage_tier = structural.get("damage_tier", "NONE")
    # gets structural damage classification

    risk_score = 0
    # starts total risk score at 0

    if density_tier == "CRITICAL":
        risk_score += 10
        # critical crowd density adds major operational risk

    elif density_tier == "HIGH":
        risk_score += 8
        # high crowd density adds meaningful risk

    elif density_tier == "MEDIUM":
        risk_score += 7
        # medium crowd density adds minor risk

    if hazard_tier == "ACTIVE_FIRE":
        risk_score += 45
        # old hazard module detects active fire

    elif hazard_tier in ["SMOKE_OR_HEAT", "SMOKE_PRESENT"]:
        risk_score += 15
        # old hazard module detects smoke/heat

    if fire_smoke_tier == "ACTIVE_FIRE":
        risk_score += 55
        # dedicated fire/smoke module detects active fire

    elif fire_smoke_tier == "SMOKE_PRESENT":
        risk_score += 10
        # dedicated fire/smoke module detects smoke

    elif fire_smoke_tier == "POSSIBLE_HAZARD":
        risk_score += 5
        # weak fire/smoke signal

    if damage_tier == "SEVERE":
        risk_score += 50
        # severe structure damage is major risk

    elif damage_tier == "MODERATE":
        risk_score += 20
        # moderate damage adds meaningful risk

    elif damage_tier == "MINOR":
        risk_score += 10
        # minor damage adds small risk

    if traffic_density == "CRITICAL":
        risk_score += 10
        # critical traffic activity adds major operational risk

    elif traffic_density == "HIGH":
        risk_score += 5
        # high traffic activity adds moderate operational risk

    elif traffic_density == "MEDIUM":
        risk_score += 3
        # medium traffic activity adds small operational risk

    risk_score = min(risk_score, 100)
    # caps risk score at 100

    if risk_score >= 50:
        risk_tier = "CRITICAL"
        # highest operational priority

    elif risk_score >= 40:
        risk_tier = "HIGH"
        # serious but not maximum priority

    elif risk_score >= 25:
        risk_tier = "MEDIUM"
        # moderate concern

    else:
        risk_tier = "LOW"
        # low operational risk

    primary_hazard = fire_smoke_tier
    # dedicated fire/smoke module becomes primary hazard source

    if primary_hazard in ["NONE", "NO_VISIBLE_FIRE_SMOKE", "UNKNOWN"]:
        # if fire/smoke module found nothing useful

        primary_hazard = hazard_tier
        # fall back to old hazard module

    if risk_score >= 65:
        recommended_action = "Escalate immediately and dispatch field verification"
        # critical action

    elif risk_score >= 50:
        recommended_action = "Escalate for operator review"
        # high-priority action

    elif risk_score >= 25:
        recommended_action = "Monitor and verify with additional evidence"
        # medium action

    else:
        recommended_action = "Log and monitor"
        # low-priority action

    return {
        "overall_risk_score": risk_score,
        # final numeric risk score

        "risk_tier": risk_tier,
        # final risk label

        "primary_hazard": primary_hazard,
        # main hazard from fire/smoke or fallback hazard module

        "fire_smoke_tier": fire_smoke_tier,
        # dedicated fire/smoke result

        "structural_damage": damage_tier,
        # main structural concern

        "recommended_action": recommended_action,
        # operational recommendation

        "scene_density": density_tier,
        # includes crowd/scene density

        "traffic_density": traffic_density
        # includes traffic risk
    }
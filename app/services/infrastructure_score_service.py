def calculate_infrastructure_score(nearby_assets):

    score = 0
    direct_count = 0
    cascade_count = 0
    critical_count = 0
    affected_types = []

    for asset in nearby_assets:

        asset_type = asset.get("asset_type", "")
        status = asset.get("operational_status", "NORMAL")
        risk_status = asset.get("risk_status", "NORMAL")
        criticality = asset.get("criticality", "MEDIUM")
        affected_types.append(asset_type)

        if risk_status == "DIRECT_RISK":
            direct_count += 1
            score += 15


        if risk_status == "CASCADE_RISK":
            cascade_count += 1
            score += 10


        if criticality == "CRITICAL":
            critical_count += 1
            score += 15


        if status == "DEGRADED":
            score += 20


        if status == "OFFLINE":
            score += 35

        if asset_type == "hospital":
            score += 20

        elif asset_type == "airport":
            score += 18

        elif asset_type == "bridge":
            score += 18

        elif asset_type == "power_station":
            score += 25

        elif asset_type == "telecom_site":
            score += 15

    if len(nearby_assets) >= 3:
        score += 10
        
    score = min(score, 100)


    return {
        "infrastructure_risk_score": score,
        "direct_asset_count": direct_count,
        "cascade_asset_count": cascade_count,
        "critical_asset_count": critical_count,
        "affected_asset_types": list(set(affected_types))
    }
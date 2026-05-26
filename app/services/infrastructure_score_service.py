def calculate_infrastructure_score(nearby_assets):
    # calculates operational infrastructure risk score from affected assets

    score = 0
    # starts score at 0

    direct_count = 0
    # counts directly affected assets

    cascade_count = 0
    # counts indirectly affected assets

    critical_count = 0
    # counts critical infrastructure assets

    affected_types = []
    # stores affected asset types like bridge, airport, hospital

    for asset in nearby_assets:
        # checks every affected infrastructure asset

        asset_type = asset.get("asset_type", "")
        # safely gets asset type

        status = asset.get("operational_status", "NORMAL")
        # safely gets operational status

        risk_status = asset.get("risk_status", "NORMAL")
        # safely gets direct/cascade risk type

        criticality = asset.get("criticality", "MEDIUM")
        # safely gets asset criticality

        affected_types.append(asset_type)
        # stores asset type for final summary

        if risk_status == "DIRECT_RISK":
            # directly affected infrastructure is more serious

            direct_count += 1
            # increases direct asset counter

            score += 15
            # adds direct risk score

        if risk_status == "CASCADE_RISK":
            # cascade affected infrastructure shows dependency propagation

            cascade_count += 1
            # increases cascade counter

            score += 10
            # adds cascade risk score

        if criticality == "CRITICAL":
            # critical assets matter more operationally

            critical_count += 1
            # increases critical asset counter

            score += 15
            # adds critical infrastructure score

        if status == "DEGRADED":
            # degraded assets have reduced function

            score += 20
            # adds degradation score

        if status == "OFFLINE":
            # offline assets are severe

            score += 35
            # adds severe outage score

        if asset_type == "hospital":
            # hospital impact is highly sensitive

            score += 20

        elif asset_type == "airport":
            # airport impact affects logistics and evacuation

            score += 18

        elif asset_type == "bridge":
            # bridge impact affects transport corridors

            score += 18

        elif asset_type == "power_station":
            # power impact can cascade broadly

            score += 25

        elif asset_type == "telecom_site":
            # telecom affects communication reliability

            score += 15

    if len(nearby_assets) >= 3:
        # multiple affected assets means wider operational impact

        score += 10
        # adds multi-asset escalation bonus

    score = min(score, 100)
    # caps score at 100

    return {
        "infrastructure_risk_score": score,
        "direct_asset_count": direct_count,
        "cascade_asset_count": cascade_count,
        "critical_asset_count": critical_count,
        "affected_asset_types": list(set(affected_types))
    }
    # returns structured infrastructure risk summary
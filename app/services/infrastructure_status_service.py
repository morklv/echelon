def normalize_text(value):

    if value is None:
        return ""
    
    return value.lower().strip()


def evaluate_asset_operational_status(
    incident,
    asset,
    distance_km
):
    incident_category = normalize_text(incident.category)
    severity = incident.severity
    asset_type = normalize_text(asset.asset_type)


    if incident_category == "fire":

        if asset_type == "airport" and severity >= 5 and distance_km < 1.0:
            return "DEGRADED"

        if asset_type == "hospital" and severity >= 5 and distance_km < 0.7:
            return "AT_RISK"

        if asset_type == "power_station" and severity >= 4 and distance_km < 1.0:
            return "DEGRADED"

        if distance_km < 1.0:
            return "AT_RISK"


        

    if incident_category == "road_accident":

        if asset_type == "bridge" and severity >= 4 and distance_km < 0.8:
            return "DEGRADED"

        if asset_type == "hospital" and severity >= 4 and distance_km < 0.6:
            return "AT_RISK"

        if asset_type == "airport" and severity >= 4 and distance_km < 0.8:
            return "AT_RISK"



    if incident_category == "power_failure":

        if asset_type == "hospital" and severity >= 4 and distance_km < 2.0:
            return "DEGRADED"

        if asset_type == "telecom_site" and severity >= 4 and distance_km < 2.0:
            return "DEGRADED"

        if asset_type == "airport" and severity >= 4 and distance_km < 2.0:

            return "AT_RISK"

        if asset_type == "coast_guard_base" and severity >= 4 and distance_km < 2.0:
            return "AT_RISK"
        if asset_type == "coast_guard_base" and severity >= 4 and distance_km < 3.0:
            return "DEGRADED"


    if incident_category == "hazmat":
        if asset_type in ["hospital", "airport", "telecom_site"] and distance_km < 1.0:
            return "AT_RISK"



    if incident_category == "flooding":

        if asset_type in ["power_station", "bridge", "telecom_site"] and distance_km < 1.5:
            return "DEGRADED"


        if asset_type in ["hospital", "airport"] and distance_km < 1.5:
            return "AT_RISK"



    if incident_category == "structural_damage":

        if asset_type == "bridge" and severity >= 3 and distance_km < 2.0:
            return "DEGRADED"

        if distance_km < 0.5:
            return "AT_RISK"

    if incident_category == "infrastructure":

        if asset_type == "bridge" and distance_km < 1.0:

            if incident.status == "resolved":
                return "NORMAL"

            if severity >= 4:
                return "DEGRADED"

            if severity >= 3:
                return "AT_RISK"

            return "NORMAL"

    return "NORMAL"

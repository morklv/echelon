def normalize_text(value):
    # converts None or text into safe lowercase text

    if value is None:
        # handles missing values safely

        return ""
        # returns empty text if value does not exist

    return value.lower().strip()
    # lowercases text and removes extra spaces


def evaluate_asset_operational_status(
    incident,
    asset,
    distance_km
):
    # determines operational condition of infrastructure asset

    incident_category = normalize_text(incident.category)
    # gets incident category in clean lowercase form

    severity = incident.severity
    # gets numeric incident severity

    asset_type = normalize_text(asset.asset_type)
    # gets infrastructure type in clean lowercase form

    # -----------------------------
    # FIRE
    # -----------------------------

    if incident_category == "fire":
        # fire can threaten nearby critical infrastructure


        if asset_type == "airport" and severity >= 5 and distance_km < 1.0:
            # severe fire very close to airport

            return "DEGRADED"
            # airport operations may be partially disrupted

        if asset_type == "hospital" and severity >= 5 and distance_km < 0.7:
            # severe fire close to hospital

            return "AT_RISK"
            # hospital access or safety perimeter may be affected

        if asset_type == "power_station" and severity >= 4 and distance_km < 1.0:
            # major fire near power infrastructure

            return "DEGRADED"
            # power infrastructure may be disrupted

        if distance_km < 1.0:
            # general fire near any infrastructure asset

            return "AT_RISK"
            # asset needs monitoring

        

    # -----------------------------
    # ROAD ACCIDENT
    # -----------------------------

    if incident_category == "road_accident":
        # road accidents mostly affect access routes and transport assets

        if asset_type == "bridge" and severity >= 4 and distance_km < 0.8:
            # serious crash near bridge

            return "DEGRADED"
            # bridge flow may be partially blocked

        if asset_type == "hospital" and severity >= 4 and distance_km < 0.6:
            # serious crash near hospital

            return "AT_RISK"
            # emergency access may be slowed

        if asset_type == "airport" and severity >= 4 and distance_km < 0.8:
            # serious crash near airport access

            return "AT_RISK"
            # airport traffic/logistics access may be affected

    # -----------------------------
    # POWER FAILURE
    # -----------------------------

    if incident_category == "power_failure":
        # power failures can affect dependent critical services

        if asset_type == "hospital" and severity >= 4 and distance_km < 2.0:
            # major power issue near hospital

            return "DEGRADED"
            # hospital may depend on backup power

        if asset_type == "telecom_site" and severity >= 4 and distance_km < 2.0:
            # major power issue near telecom infrastructure

            return "DEGRADED"
            # telecom service may be unstable

        if asset_type == "airport" and severity >= 4 and distance_km < 2.0:
            # power issue near airport

            return "AT_RISK"
            # airport systems may require monitoring

        if asset_type == "coast_guard_base" and severity >= 4 and distance_km < 2.0:
            return "AT_RISK"
        if asset_type == "coast_guard_base" and severity >= 4 and distance_km < 3.0:
            return "DEGRADED"

    # -----------------------------
    # HAZMAT
    # -----------------------------

    if incident_category == "hazmat":
        # hazardous material incidents affect safety perimeters

        if asset_type in ["hospital", "airport", "telecom_site"] and distance_km < 1.0:
            # hazmat near sensitive infrastructure

            return "AT_RISK"
            # asset may need safety monitoring

    # -----------------------------
    # FLOODING
    # -----------------------------

    if incident_category == "flooding":
        # flooding can degrade utility and transport infrastructure

        if asset_type in ["power_station", "bridge", "telecom_site"] and distance_km < 1.5:
            # flood near vulnerable infrastructure

            return "DEGRADED"
            # asset may lose partial function

        if asset_type in ["hospital", "airport"] and distance_km < 1.5:
            # flood near critical service asset

            return "AT_RISK"
            # asset requires monitoring

    # -----------------------------
    # STRUCTURAL DAMAGE
    # -----------------------------

    if incident_category == "structural_damage":
        # structural damage is most dangerous for bridges and transport assets

        if asset_type == "bridge" and severity >= 3 and distance_km < 2.0:
            # serious structural issue near bridge

            return "DEGRADED"
            # bridge may need inspection or restriction

        if distance_km < 0.5:
            # structural damage very close to any asset

            return "AT_RISK"
            # asset may require verification
    
    if incident_category == "infrastructure":
    # infrastructure incidents affect transport/utilities directly

        if asset_type == "bridge" and distance_km < 1.0:
            # nearby bridge impacted by infrastructure incident

            if incident.status == "resolved":
                return "NORMAL"
                # resolved incident restores normal bridge state

            if severity >= 4:
                return "DEGRADED"
                # major infrastructure incident damages bridge operations

            if severity >= 3:
                return "AT_RISK"
                # moderate infrastructure incident requires monitoring

            return "NORMAL"
            # low-severity incident does not affect bridge

    return "NORMAL"
    # default state when no risk rule matched
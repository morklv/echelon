import math
import json
import asyncio

from app import models

from app.services.infrastructure_status_service import (
    evaluate_asset_operational_status
)

from app.services.infrastructure_cascade_service import apply_cascade_effects

from app.services.websocket_service import broadcast_event


def calculate_distance_km(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371

    diff_lat = math.radians(lat2 - lat1)
    diff_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(diff_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(diff_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


def calculate_distance_to_line_km(
    point_lat,
    point_lon,
    line_coordinates
):
    shortest_distance = None

    for coordinate in line_coordinates:
        line_lat = coordinate[0]
        line_lon = coordinate[1]

        distance_km = calculate_distance_km(
            point_lat,
            point_lon,
            line_lat,
            line_lon
        )

        if shortest_distance is None or distance_km < shortest_distance:
            shortest_distance = distance_km

    return shortest_distance


def find_nearby_assets(db, incident, radius_km: float = 8.0):
    assets = db.query(models.InfrastructureAsset).all()

    nearby_assets = []

    for asset in assets:
        if asset.geometry_type == "line" and asset.geometry_coordinates:
            line_coordinates = json.loads(asset.geometry_coordinates)

            distance_km = calculate_distance_to_line_km(
                incident.latitude,
                incident.longitude,
                line_coordinates
            )

        else:
            distance_km = calculate_distance_km(
                incident.latitude,
                incident.longitude,
                asset.latitude,
                asset.longitude
            )

        if distance_km <= radius_km:
            previous_status = asset.operational_status
            previous_risk = asset.risk_status

            operational_status = evaluate_asset_operational_status(
                incident,
                asset,
                distance_km
            )

            asset.operational_status = operational_status
            asset.risk_status = "DIRECT_RISK"

            db.add(asset)

            nearby_assets.append({
                "id": asset.id,
                "name": asset.name,
                "asset_type": asset.asset_type,
                "criticality": asset.criticality,
                "operational_status": operational_status,
                "previous_operational_status": previous_status,
                "latitude": asset.latitude,
                "longitude": asset.longitude,
                "distance_km": round(distance_km, 3),
                "risk_status": "DIRECT_RISK",
                "previous_risk_status": previous_risk,
                "incident_severity": incident.severity,
                "impact_type": "DIRECT"
            })

    cascade_impacts = apply_cascade_effects(
        db,
        nearby_assets
    )

    for cascade in cascade_impacts:
        dependent_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == cascade["asset_id"]
        ).first()

        if not dependent_asset:
            continue

        source_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == cascade["source_asset_id"]
        ).first()

        already_added = any(
            asset["id"] == dependent_asset.id
            for asset in nearby_assets
        )

        if already_added:
            continue

        previous_status = dependent_asset.operational_status
        previous_risk = dependent_asset.risk_status

        dependent_asset.operational_status = cascade["new_status"]
        dependent_asset.risk_status = "CASCADE_RISK"

        db.add(dependent_asset)

        dependency_distance_km = None

        if source_asset:
            dependency_distance_km = round(
                calculate_distance_km(
                    source_asset.latitude,
                    source_asset.longitude,
                    dependent_asset.latitude,
                    dependent_asset.longitude
                ),
                3
            )

        nearby_assets.append({
            "id": dependent_asset.id,
            "name": dependent_asset.name,
            "asset_type": dependent_asset.asset_type,
            "criticality": dependent_asset.criticality,
            "operational_status": cascade["new_status"],
            "previous_operational_status": previous_status,
            "latitude": dependent_asset.latitude,
            "longitude": dependent_asset.longitude,
            "risk_status": "CASCADE_RISK",
            "previous_risk_status": previous_risk,
            "impact_type": "CASCADE",
            "source_asset_id": source_asset.id if source_asset else None,
            "source_asset_name": source_asset.name if source_asset else "Unknown source",
            "dependency_type": cascade.get("dependency_type", "dependency"),
            "dependency_distance_km": dependency_distance_km,
            "distance_km": None,
            "cascade_reason": cascade["reason"]
        })

    db.commit()

    critical_assets = 0
    cascade_assets = 0
    operational_risk_score = 0

    for asset in nearby_assets:
        if asset["criticality"] in ["HIGH", "CRITICAL"]:
            critical_assets += 1

        if asset.get("risk_status") == "CASCADE_RISK":
            cascade_assets += 1

        if asset["asset_type"] == "hospital":
            operational_risk_score += 20

        elif asset["asset_type"] == "airport":
            operational_risk_score += 25

        elif asset["asset_type"] == "bridge":
            operational_risk_score += 30

        elif asset["asset_type"] in ["substation", "power_station"]:
            operational_risk_score += 35

        elif asset["asset_type"] == "seaport":
            operational_risk_score += 25

        elif asset["asset_type"] == "refinery":
            operational_risk_score += 35

        elif asset["asset_type"] == "industrial":
            operational_risk_score += 15

        elif asset["asset_type"] == "transit_hub":
            operational_risk_score += 20

        if asset.get("risk_status") == "CASCADE_RISK":
            operational_risk_score += 15

    operational_risk_score = min(
        operational_risk_score,
        100
    )

    changed_assets = [
        asset
        for asset in nearby_assets
        if (
            asset.get("previous_operational_status")
            != asset.get("operational_status")
            or asset.get("previous_risk_status")
            != asset.get("risk_status")
        )
    ]

    if changed_assets:
        affected_asset_names = [
            asset["name"]
            for asset in changed_assets[:3]
        ]

        try:
            asyncio.run(
                broadcast_event({
                    "event_type": "infrastructure_alert",
                    "title": "Infrastructure Risk Update",
                    "message": (
                        "Affected assets: "
                        + ", ".join(affected_asset_names)
                    ),
                    "affected_assets": len(nearby_assets),
                    "changed_assets": len(changed_assets),
                    "critical_assets": critical_assets,
                    "cascade_assets": cascade_assets,
                    "risk_score": operational_risk_score
                })
            )

        except RuntimeError:
            pass

    return {
        "affected_assets": nearby_assets,
        "nearby_assets": nearby_assets,
        "critical_asset_count": critical_assets,
        "cascade_asset_count": cascade_assets,
        "operational_risk_score": operational_risk_score
    }


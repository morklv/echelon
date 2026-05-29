from app.database import SessionLocal
from app import models


def seed_demo_data():
    db = SessionLocal()

    try:
        db.query(models.InfrastructureDependency).delete()
        db.query(models.InfrastructureAsset).delete()
        db.query(models.Incident).delete()
        db.commit()

        assets = [
            {
                "name": "Golden Gate Bridge",
                "asset_type": "bridge",
                "latitude": 37.8199,
                "longitude": -122.4783,
                "criticality": "CRITICAL",
                "description": "Major transportation and emergency access bridge connecting San Francisco and Marin County.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Port of Oakland",
                "asset_type": "seaport",
                "latitude": 37.7955,
                "longitude": -122.2780,
                "criticality": "CRITICAL",
                "description": "Major cargo and logistics seaport serving Northern California.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "San Jose Mineta International Airport",
                "asset_type": "airport",
                "latitude": 37.3639,
                "longitude": -121.9289,
                "criticality": "HIGH",
                "description": "Primary Silicon Valley commercial airport.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "San Francisco International Airport",
                "asset_type": "airport",
                "latitude": 37.6213,
                "longitude": -122.3790,
                "criticality": "HIGH",
                "description": "Major regional air transportation hub.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Oakland International Airport",
                "asset_type": "airport",
                "latitude": 37.7126,
                "longitude": -122.2197,
                "criticality": "MEDIUM",
                "description": "Regional airport and logistics node.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "U.S. Coast Guard Base Alameda",
                "asset_type": "coast_guard_base",
                "latitude": 37.7726,
                "longitude": -122.3008,
                "criticality": "HIGH",
                "description": (
                    "Major United States Coast Guard operational installation supporting "
                    "maritime security, emergency response, search and rescue operations, "
                    "logistics coordination, and regional coastal infrastructure protection."
                ),
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Tesla Fremont Factory",
                "asset_type": "industrial",
                "latitude": 37.4949,
                "longitude": -121.9440,
                "criticality": "HIGH",
                "description": "Major electric vehicle manufacturing facility.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "PG&E Metcalf Substation",
                "asset_type": "industrial",
                "latitude": 37.2370,
                "longitude": -121.8500,
                "criticality": "CRITICAL",
                "description": "Critical Silicon Valley electrical transmission substation.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Chevron Richmond Refinery",
                "asset_type": "refinery",
                "latitude": 37.9362,
                "longitude": -122.3880,
                "criticality": "CRITICAL",
                "description": "Large petroleum refinery supporting Bay Area fuel supply.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Transbay Transit Center",
                "asset_type": "transit_hub",
                "latitude": 37.7890,
                "longitude": -122.3969,
                "criticality": "HIGH",
                "description": "Major public transportation hub in San Francisco.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "San Francisco-Oakland Bay Bridge",
                "asset_type": "bridge",
                "latitude": 37.7983,
                "longitude": -122.3778,
                "criticality": "HIGH",
                "description": "Critical transportation corridor between San Francisco and Oakland.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {
                "name": "Zuckerberg San Francisco General Hospital",
                "asset_type": "hospital",
                "latitude": 37.7558,
                "longitude": -122.4058,
                "criticality": "HIGH",
                "description": "Major emergency medical facility.",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            },
            {   
                "name": "Hayward Power Grid Station",
                "asset_type": "power_station",
                "latitude": 37.6368,
                "longitude": -122.0985,
                "criticality": "HIGH",
                "description": "A regional power infrastructure node",
                "operational_status": "NORMAL",
                "risk_status": "NORMAL",
            }

        ]

        asset_objects = {}

        for asset_data in assets:
            asset = models.InfrastructureAsset(**asset_data)
            db.add(asset)
            asset_objects[asset_data["name"]] = asset

        db.commit()

        for asset in asset_objects.values():
            db.refresh(asset)

        dependencies = [
            {
                "source_asset": "PG&E Metcalf Substation",
                "dependent_asset": "San Jose Mineta International Airport",
                "dependency_type": "power",
                "description": "Airport operations depend on regional electrical transmission infrastructure.",
            },
            {
                "source_asset": "Port of Oakland",
                "dependent_asset": "Chevron Richmond Refinery",
                "dependency_type": "fuel_logistics",
                "description": "Fuel and industrial cargo transport routed through maritime logistics channels.",
            },
            {
                "source_asset": "San Francisco-Oakland Bay Bridge",
                "dependent_asset": "Port of Oakland",
                "dependency_type": "transportation",
                "description": "Cargo distribution depends on bridge transportation corridor.",
            },
            {
                "source_asset": "PG&E Metcalf Substation",
                "dependent_asset": "Tesla Fremont Factory",
                "dependency_type": "power",
                "description": "Manufacturing operations depend on stable regional power infrastructure.",
            },
            {
                "source_asset": "Hayward Power Grid Station",
                "dependent_asset": "Tesla Fremont Factory",
                "dependency_type": "power_supply",
                "description": (
                    "Tesla Fremont Factory depends on uninterrupted electrical power "
                    "for robotic manufacturing systems, automated assembly lines, "
                    "industrial cooling systems, battery-related operations, "
                    "logistics coordination, and facility-wide production continuity."
                )
            },
            {
                "source_asset": "Hayward Power Grid Station",
                "dependent_asset": "Oakland International Airport",
                "dependency_type": "power_supply",
                "description": (
                    "Oakland International Airport depends on continuous electrical "
                    "power for runway lighting, radar systems, terminal operations, "
                    "communications infrastructure, fuel systems, baggage handling, "
                    "and emergency coordination capabilities."
                )
            },
            {
                "source_asset": "Hayward Power Grid Station",
                "dependent_asset": "U.S. Coast Guard Base Alameda",
                "dependency_type": "power_supply",
                "description": ("U.S. Coast Guard Base Alameda depends on stable electrical power for "
                    "maritime command operations, communications systems, vessel support "
                    "infrastructure, emergency coordination capabilities, security systems, "
                    "maintenance facilities, and regional coastal response readiness."
                )
            },
            {
                "source_asset": "Transbay Transit Center",
                "dependent_asset": "San Francisco International Airport",
                "dependency_type": "public_transport",
                "description": "Passenger transit movement linked to airport access infrastructure.",
            },
            {
                "source_asset": "San Francisco-Oakland Bay Bridge",
                "dependent_asset": "Transbay Transit Center",
                "dependency_type": "transportation",
                "description": (
                            "Regional transit movement and commuter flow depend on Bay Bridge "
                            "transportation connectivity between San Francisco and the East Bay."
                )
            },
        ]

        for dependency_data in dependencies:
            source_asset = asset_objects.get(dependency_data["source_asset"])
            dependent_asset = asset_objects.get(dependency_data["dependent_asset"])

            if source_asset and dependent_asset:
                dependency = models.InfrastructureDependency(
                    source_asset_id=source_asset.id,
                    dependent_asset_id=dependent_asset.id,
                    dependency_type=dependency_data["dependency_type"],
                    description=dependency_data["description"],
                )
                db.add(dependency)

        incidents = [
            {
                "title": "Unauthorized Drone Near Bay Bridge",
                "description": "Low-altitude drone activity detected near the San Francisco-Oakland Bay Bridge transport corridor.",
                "category": "airspace",
                "severity": 4,
                "status": "open",
                "latitude": 37.8048,
                "longitude": -122.3382,
                "owner_id": 1,
            },

            {
                "title": "Critical Traffic Congestion",
                "description": "Heavy vehicle congestion impacting regional traffic flow.",
                "category": "transportation",
                "severity": 3,
                "status": "open",
                "latitude": 37.8040,
                "longitude": -122.2711,
                "owner_id": 1,
            },

            {
                "title": "Structural Damage Report",
                "description": "Visible structural damage detected near infrastructure corridor.",
                "category": "infrastructure",
                "severity": 5,
                "status": "open",
                "latitude": 37.7980,
                "longitude": -122.3770,
                "owner_id": 1,
            },

            {
                "title": "Industrial Hazard Alert",
                "description": "Potential hazardous activity detected near industrial zone.",
                "category": "hazmat",
                "severity": 4,
                "status": "open",
                "latitude": 37.9370,
                "longitude": -122.3890,
                "owner_id": 1,
            },

            {
                "title": "Smoke Detection Event",
                "description": "Smoke plume observed near critical infrastructure area.",
                "category": "smoke",
                "severity": 4,
                "status": "open",
                "latitude": 37.2365,
                "longitude": -121.8490,
                "owner_id": 1,
            },
            {
                "title": "Golden Gate Protest Gathering",
                "description": "Large protest crowd gathering detected near Golden Gate Bridge access corridor.",
                "category": "public_safety",
                "severity": 4,
                "status": "open",
                "latitude": 37.8199,
                "longitude": -122.4783,
                "owner_id": 1,
            },
            {
                "title": "Hospital Smoke Alert",
                "description": "Smoke detected near hospital infrastructure zone.",
                "category": "smoke",
                "severity": 4,
                "status": "open",
                "latitude": 37.7558,
                "longitude": -122.4058,
                "owner_id": 1,
            },
        ]

        for incident_data in incidents:
            incident = models.Incident(**incident_data)
            db.add(incident)

        db.commit()

        print("Demo infrastructure seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
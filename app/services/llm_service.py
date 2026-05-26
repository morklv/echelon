import json
# lets us convert image_analysis JSON string into Python dictionary

import os 
#to read enviroment variables env

from dotenv import load_dotenv
#to load variables from .env into python

from openai import OpenAI
#imports openai sdk (software development kit)

load_dotenv() 
#loads .env file into enviroment

client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)


def generate_incident_summary(
    title,
    description,
    category,
    severity,
    image_analysis,
    nearby_assets=None
):
    # creates readable operational summary for incident

    data = json.loads(image_analysis)
    # converts image_analysis from JSON string into Python dictionary

    hazard = data.get("hazard_analysis", {})
    # extracts fire/smoke hazard analysis

    fire_smoke = data.get("hazard_analysis", {})

    structural = data.get("structural_analysis", {})
    # extracts structural damage analysis

    fusion = data.get("intelligence_fusion", {})
    # extracts composite intelligence/risk scoring

    objects = data.get("detected_objects", [])
    # extracts YOLO detected objects list

    detected_labels = [obj["label"] for obj in objects]
    # creates simple list of detected object names

    traffic = data.get("traffic_activity", {})

    object_labels = ", ".join(
        obj.get("label", "unknown")
        for obj in objects
    )
    # converts detected object labels into readable text
    nearby_assets = nearby_assets or []

    asset_lines = []
    for asset in nearby_assets:
        asset_lines.append(
            f"{asset['name']} ({asset['asset_type']}): "
            f"{asset['operational_status']} / {asset.get('risk_status', 'UNKNOWN')}"
        )

    infrastructure_context = "\n".join(asset_lines) or "No affected infrastructure detected."

    prompt = f"""
    You are an operational intelligence assistant for emergency coordination.

    Create a concise operator brief from this incident data.

    Incident:
    Title: {title}
    Description: {description}
    Category: {category}
    Severity: {severity}
    Affected Infrastructure:
    {infrastructure_context}

    Operational Analysis:
    Risk Tier: {fusion.get('risk_tier', 'UNKNOWN')}
    Overall Risk Score: {fusion.get('overall_risk_score', 'N/A')}
    Hazard Tier: {hazard.get('hazard_tier', 'UNKNOWN')}
    Fire/Smoke Tier: {fire_smoke.get('hazard_tier', 'UNKNOWN')}
    Fire Score: {fire_smoke.get('fire_score', 'N/A')}
    Smoke Score: {fire_smoke.get('smoke_score', 'N/A')}
    Structural Status: {structural.get('damage_tier', 'UNKNOWN')}
    Crowd Density: {fusion.get('scene_density', 'UNKNOWN')}
    Traffic Density: {fusion.get('traffic_density', 'UNKNOWN')}
    Detected Objects: {object_labels}
    Recommended Action: {fusion.get('recommended_action', 'Monitor and verify')}

    Format:
    SITUATION:
    RISK:
    EVIDENCE:
    RECOMMENDED ACTION:
    """
    # builds structured operational prompt

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        # low-cost OpenAI model

        messages=[
            {
                "role": "system",
                "content": (
                    "You generate concise operational intelligence briefs. "
                    "Do not invent facts. "
                    "Keep output tactical, structured, and professional. "
                    "Do not use markdown, bold symbols, bullet points, or asterisks."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.2
        # low creativity for stable operational outputs
    )

    return response.choices[0].message.content
    # returns generated AI brief


def generate_infrastructure_recommendation(
        incident,
        nearby_assets
):
    if not nearby_assets:
        return "No nearby infrastructure assets are currently affected."
    
    asset_lines = []
    # empty list for asset summaries

    for asset in nearby_assets:

        distance = asset.get("distance_km")

        if distance is None:
            distance = asset.get("dependency_distance_km")

        distance_text = (
            f"{round(distance, 2)} km"
            if distance is not None
            else "N/A"
        )

        asset_lines.append(
            f"- {asset['name']} "
            f"({asset['asset_type']}), "
            f"status: {asset['operational_status']}, "
            f"distance: {distance_text}"
        )

    assets_text = "\n".join(asset_lines)
    #to combine all asset line into one text block

    return (
        "Infrastructure Impact Brief:\n\n"
        f"Incident: {incident.title}\n"
        f"Category: {incident.category}\n"
        f"Severity: {incident.severity}\n\n"
        "Affected infrastructure:\n"
        f"{assets_text}\n\n"
        "Operational Assessment:\n"
        "Nearby infrastructure may require monitoring based on incident type, severity, and distance.\n\n"
        "Recommended Actions:\n"
        "- Verify the incident status with field evidence.\n"
        "- Notify the responsible infrastructure operator if status is AT_RISK or DEGRADED.\n"
        "- Monitor access routes and emergency response corridors.\n"
        "- Escalate if conditions worsen or additional hazards are detected."
    )
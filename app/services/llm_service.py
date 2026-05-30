import json
import os 
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv() 

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

    data = json.loads(image_analysis)

    hazard = data.get("hazard_analysis", {})

    fire_smoke = data.get("hazard_analysis", {})

    structural = data.get("structural_analysis", {})

    fusion = data.get("intelligence_fusion", {})

    objects = data.get("detected_objects", [])

    detected_labels = [obj["label"] for obj in objects]

    traffic = data.get("traffic_activity", {})

    object_labels = ", ".join(
        obj.get("label", "unknown")
        for obj in objects
    )

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

    response = client.chat.completions.create(
        model="gpt-4o-mini",

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
    )

    return response.choices[0].message.content


def generate_infrastructure_recommendation(
        incident,
        nearby_assets
):
    if not nearby_assets:
        return "No nearby infrastructure assets are currently affected."
    
    asset_lines = []
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
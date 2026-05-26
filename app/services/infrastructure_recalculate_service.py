from sqlalchemy.orm import Session

from app import models
from app.services.infrastructure_risk_service import find_nearby_assets


def recalculate_infrastructure_risk(db: Session):
    assets = db.query(models.InfrastructureAsset).all()

    for asset in assets:
        asset.operational_status = "NORMAL"
        asset.risk_status = "NORMAL"
        db.add(asset)

    db.commit()

    active_incidents = db.query(models.Incident).filter(
        models.Incident.status == "open"
    ).all()

    for incident in active_incidents:
        find_nearby_assets(
            db=db,
            incident=incident,
            radius_km=3.0
        )
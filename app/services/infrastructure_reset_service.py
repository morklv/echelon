from sqlalchemy.orm import Session

from app import models


def reset_infrastructure_risk(db: Session):
    assets = db.query(models.InfrastructureAsset).all()

    for asset in assets:
        asset.operational_status = "NORMAL"
        asset.risk_status = "NORMAL"

        db.add(asset)

    db.commit()
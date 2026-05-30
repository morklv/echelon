from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import models
from app.database import get_db


router = APIRouter(
    prefix="/infrastructure-dependencies",
    tags=["infrastructure-dependencies"]
)


@router.get("/")
def get_infrastructure_dependencies(
    db: Session = Depends(get_db)
):
    dependencies = db.query(models.InfrastructureDependency).all()
  

    graph_edges = []

    for dependency in dependencies:

        source_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == dependency.source_asset_id
        ).first()


        dependent_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == dependency.dependent_asset_id
        ).first()


        if not source_asset or not dependent_asset:


            continue

        graph_edges.append({
            "dependency_id": dependency.id,
            "dependency_type": dependency.dependency_type,
            "description": dependency.description,

            "source": {
                "id": source_asset.id,
                "name": source_asset.name,
                "asset_type": source_asset.asset_type,
                "latitude": source_asset.latitude,
                "longitude": source_asset.longitude,
                "operational_status": source_asset.operational_status,
                "risk_status": source_asset.risk_status
            },

            "dependent": {
                "id": dependent_asset.id,
                "name": dependent_asset.name,
                "asset_type": dependent_asset.asset_type,
                "latitude": dependent_asset.latitude,
                "longitude": dependent_asset.longitude,
                "operational_status": dependent_asset.operational_status,
                "risk_status": dependent_asset.risk_status
            }
        })

    return {
        "dependency_count": len(graph_edges),
        "dependencies": graph_edges
    }

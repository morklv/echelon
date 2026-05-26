from fastapi import APIRouter, Depends
# imports router and dependency injection

from sqlalchemy.orm import Session
# imports database session type

from app import models
# imports database models

from app.database import get_db
# imports database dependency


router = APIRouter(
    prefix="/infrastructure-dependencies",
    tags=["infrastructure-dependencies"]
)
# creates dependency graph router


@router.get("/")
def get_infrastructure_dependencies(
    db: Session = Depends(get_db)
):
    # returns infrastructure dependency graph for frontend visualization

    dependencies = db.query(models.InfrastructureDependency).all()
    # loads all dependency relationships

    graph_edges = []
    # stores frontend-ready graph edges

    for dependency in dependencies:
        # loops through each dependency relationship

        source_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == dependency.source_asset_id
        ).first()
        # loads source asset

        dependent_asset = db.query(models.InfrastructureAsset).filter(
            models.InfrastructureAsset.id == dependency.dependent_asset_id
        ).first()
        # loads dependent asset

        if not source_asset or not dependent_asset:
            # skips broken dependency rows

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
        # creates frontend-ready dependency edge

    return {
        "dependency_count": len(graph_edges),
        "dependencies": graph_edges
    }
    # returns graph data
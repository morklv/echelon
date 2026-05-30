from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from app.repositories import incident_repository
from app.services import incident_service
from fastapi import UploadFile, File
from app.services import websocket_service
from fastapi import BackgroundTasks

from app.services.infrastructure_risk_service import find_nearby_assets
from app.services.llm_service import generate_infrastructure_recommendation


router = APIRouter(
    prefix = "/incidents",
    tags = ["incidents"]
)


@router.get("/test-auth")
def test_auth_route(
    current_user: models.User = Depends(get_current_user)
):
    return {
        "message": "You are authenticated.",
        "username": current_user.username,
        "role": current_user.role
    }

@router.post(
    "/",
    response_model=schemas.IncidentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_incident(
    incident_request: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await incident_service.create_incident(
        incident_request=incident_request,
        db=db,
        current_user=current_user
    )

@router.get("/", response_model = List[schemas.IncidentResponse])
def get_my_incidents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return incident_service.get_my_incidents(
        db=db,
        current_user=current_user
    )

@router.get("/{incident_id}", response_model = schemas.IncidentResponse)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return incident_service.get_incident(
    incident_id=incident_id,
    db=db,
    current_user=current_user
)

@router.delete("/{incident_id}")
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await incident_service.delete_incident(
    incident_id=incident_id,
    db=db,
    current_user=current_user
)

    return {
        "message": "Incident deleted successfully"
    }

@router.post("/{incident_id}/upload-image")
def upload_incident_image(
    incident_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),

    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return incident_service.upload_and_analyze_incident_image(
    incident_id=incident_id,
    file=file,
    background_tasks=background_tasks,
    db=db,
    current_user=current_user
    )

@router.patch("/{incident_id}", response_model = schemas.IncidentResponse)
# PATCH means partial update
async def update_incident(
    incident_id: int,
    update_data: schemas.IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await incident_service.update_incident(
        incident_id=incident_id,
        update_data=update_data,
        db=db,
        current_user=current_user
    )

@router.get("/{incident_id}/nearby-infrastructure")
def get_nearby_infrastructure_for_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):

    incident = db.query(models.Incident).filter(
        models.Incident.id == incident_id
    ).first()

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    infrastructure_result = find_nearby_assets(
        db=db,
        incident=incident,
        radius_km = 2.0
    )

    affected_assets = infrastructure_result["affected_assets"]

    infrastructure_recommendation = generate_infrastructure_recommendation(
        incident,
        affected_assets
    )

    return {
        "incident_id": incident.id,
        "nearby_assets": affected_assets,
        "asset_count": len(affected_assets),
        "critical_asset_count": infrastructure_result["critical_asset_count"],
        "cascade_asset_count": infrastructure_result["cascade_asset_count"],
        "operational_risk_score": infrastructure_result["operational_risk_score"],
        "infrastructure_recommendation": infrastructure_recommendation
    }

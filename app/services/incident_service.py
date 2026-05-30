import json
import shutil
from pathlib import Path
from app.services.infrastructure_risk_service import find_nearby_assets
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app import models
from app.repositories import incident_repository
from app.services.cv_service import analyze_image
from app.services.llm_service import generate_incident_summary
from app import schemas
from app.services import websocket_service
from app.database import SessionLocal
from fastapi import BackgroundTasks
import asyncio
from app.core.logging_config import logger
from uuid import uuid4
from app.core.permissions import require_roles
from app.services.infrastructure_reset_service import reset_infrastructure_risk
from app.services.infrastructure_recalculate_service import recalculate_infrastructure_risk

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

MAX_FILE_SIZE = 5 * 1024 * 1024 #max file size is 5 mp since (1024*1024 = 1 mb)


UPLOAD_DIR = Path("uploads")
# folder where uploaded images are stored

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def upload_and_analyze_incident_image(
    incident_id: int,
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session,
    current_user: models.User
):
    require_roles(
        current_user,
        ["operator", "admin"]
    )

    incident = db.query(models.Incident).filter(
        models.Incident.id == incident_id
    ).first()

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, and WEBP images are allowed"
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file is too large. Maximum size is 5 MB"
        )

    file_extension = Path(file.filename).suffix

    safe_filename = f"incident_{incident_id}_{uuid4().hex}{file_extension}"

    file_path = UPLOAD_DIR / safe_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    logger.info(
        f"Image uploaded for incident {incident.id}"
    )

    incident.image_path = f"/uploads/{safe_filename}"

    db.commit()
    db.refresh(incident)

    background_tasks.add_task(
        process_uploaded_image,
        incident.id,
        str(file_path),
    )

    return {
        "message": "Image uploaded and analysis started",
        "incident_id": incident.id,
        "image_path": incident.image_path
    }
    

async def create_incident(
        incident_request: schemas.IncidentCreate,
        db : Session,
        current_user: models.User
):
    require_roles(
    current_user,
    ["operator", "admin"]
    )

    incident = incident_repository.create_incident(
        db = db,
        incident_request = incident_request,
        owner_id = current_user.id
    )

    logger.info(
        f"Incident created: {incident.id} by user {current_user.username}"
    )

    await websocket_service.broadcast_event({
    "event": "incident_created",
    "incident_id": incident.id
    })

    recalculate_infrastructure_risk(db)

    await websocket_service.broadcast_event({
        "event": "infrastructure_updated"
    })

    return incident

def get_my_incidents(
    db: Session,
    current_user: models.User
):
    recalculate_infrastructure_risk(db)

    incidents = db.query(models.Incident).all()

    return incidents


def get_incident(
    incident_id: int,
    db: Session,
    current_user: models.User
):

    if current_user.role == "admin":

        incident = db.query(models.Incident).filter(
            models.Incident.id == incident_id
        ).first()

    else:

        incident = incident_repository.get_incident_by_id_and_owner(
            db=db,
            incident_id=incident_id,
            owner_id=current_user.id
        )

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    return incident

async def delete_incident(
    incident_id: int,
    db: Session,
    current_user: models.User
):
    require_roles(
    current_user,
    ["admin"]
    )

    incident = get_incident(
        incident_id=incident_id,
        db=db,
        current_user=current_user
    )

    incident_repository.delete_incident(
        db=db,
        incident=incident
    )
    reset_infrastructure_risk(db)

    logger.info(
    f"Incident deleted: {incident_id} by user {current_user.username}"
    )

    recalculate_infrastructure_risk(db)

    await websocket_service.broadcast_event({
    "event": "incident_deleted",
    "incident_id": incident_id
    })


    return {
        "message": "Incident deleted successfully"
    }



async def update_incident(
        incident_id: int,

        update_data: schemas.IncidentUpdate,
        
        db: Session,

        current_user: models.User
):
    require_roles(
    current_user,
    ["operator", "admin"]
    )

    incident = get_incident(
        incident_id = incident_id,
        db = db,
        current_user = current_user
    )
    
    updated_incident = incident_repository.update_incident(
        db=db,
        incident = incident,
        update_data = update_data
    )

    if update_data.status in ["resolved", "closed"]:
        reset_infrastructure_risk(db)

    logger.info(
    f"Incident updated: {updated_incident.id} by user {current_user.username}"
    )

    recalculate_infrastructure_risk(db)

    await websocket_service.broadcast_event({
    "event": "incident_updated",
    "incident_id": updated_incident.id
    })
    return updated_incident


def process_uploaded_image(
        incident_id: int,
        file_path: str
):

    db = SessionLocal()

    try:
        incident = db.query(models.Incident).filter(
            models.Incident.id == incident_id
        ).first()
  
        if incident is None:

            logger.error(
                f"Incident {incident_id} not found during image processing"
            )

            return

        analysis_result = analyze_image(file_path)

        infrastructure_result = find_nearby_assets(db, incident)

        nearby_assets = infrastructure_result["affected_assets"]

        incident.image_analysis = json.dumps(analysis_result)

        incident.llm_summary = generate_incident_summary(
            title=incident.title,
            description=incident.description,
            category=incident.category,
            severity=incident.severity,
            image_analysis=incident.image_analysis,
            nearby_assets=nearby_assets
        )

        db.commit()

        logger.info(
            f"Image analysis completed for incident {incident.id}"
        )

        asyncio.run(
            websocket_service.broadcast_event({
                "event": "analysis_completed",
                "incident_id": incident.id
            })
        )
    except Exception as e:
        logger.error(
            f"Image analysis failed for incident {incident_id}: {str(e)}"
        )

    finally:
        db.close()
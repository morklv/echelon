from sqlalchemy.orm import Session
from app import models, schemas

def create_incident(
        db: Session,
        incident_request: schemas.IncidentCreate,
        owner_id: int
):
    incident = models.Incident(
        title = incident_request.title,
        category = incident_request.category,
        severity = incident_request.severity,
        latitude = incident_request.latitude,
        longitude = incident_request.longitude,
        owner_id = owner_id
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident

def get_incidents_by_owner(db: Session, owner_id: int):
    return db.query(models.Incident).filter(models.Incident.owner_id == owner_id).order_by(models.Incident.id.asc()).all()


def get_incident_by_id_and_owner(
    db: Session,
    incident_id: int,
    owner_id: int
):
    return db.query(models.Incident).filter(
        models.Incident.id == incident_id,
        models.Incident.owner_id == owner_id
    ).first()


def delete_incident(
    db: Session,
    incident: models.Incident
):
    db.delete(incident)
    db.commit()

    
def update_incident(
        db: Session,
        incident: models.Incident,
        update_data: schemas.IncidentUpdate
):  
    if update_data.status is not None:
        incident.status = update_data.status

    if update_data.title is not None:
        # checks if frontend sent a new title

        incident.title = update_data.title
        # updates incident title


    if update_data.description is not None:
        # checks if frontend sent a new description

        incident.description = update_data.description
        # updates incident description


    if update_data.category is not None:
        # checks if frontend sent a new category

        incident.category = update_data.category
        # updates incident category
    

    if update_data.severity is not None:
        incident.severity = update_data.severity
    
    db.commit()

    db.refresh(incident)

    return incident
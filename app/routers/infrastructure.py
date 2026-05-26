from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
# gets logged-in user from JWT token

from app.core.permissions import require_roles
# checks whether user has allowed role


router = APIRouter(
    prefix = "/infrastructure",
    tags = ["infrastructure"]
)
# creates router group, all routes here start with /infrastructure


@router.post("/", response_model = schemas.InfrastructureAssetResponse)
def create_infrastructure_asset(
    asset: schemas.InfrastructureAssetCreate,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)
):
    require_roles(
        current_user,
        ["admin"]
    )
    # only admins can create infrastructure assets

    new_asset = models.InfrastructureAsset(
        name = asset.name,
        asset_type = asset.asset_type,
        latitude = asset.latitude,
        longitude = asset.longitude,
        criticality = asset.criticality,
        description = asset.description,
        operational_status = asset.operational_status,
        geometry_type = asset.geometry_type,
        geometry_coordinates = asset.geometry_coordinates
    )
    #converts request schema into sqlalchemy database model

    db.add(new_asset)
    # to stage a new asset for database insertion   

    db.commit()

    db.refresh(new_asset)
    #reloads the asset with generated id

    return new_asset


@router.get("/", response_model = list[schemas.InfrastructureAssetResponse])
def get_infrastructure_assets(
    db: Session = Depends(get_db)
):
    assets = db.query(models.InfrastructureAsset).all()
    #selects all assets rows from database

    return assets


@router.patch("/{asset_id}")
def update_infrastructure_asset(
    asset_id: int,

    asset_update: schemas.InfrastructureAssetCreate,

    db: Session = Depends(get_db),

    current_user: models.User = Depends(get_current_user)
):
    require_roles(
        current_user,
        ["admin"]
    )
    # only admins can update infrastructure assets

    asset = db.query(models.InfrastructureAsset).filter(
        models.InfrastructureAsset.id == asset_id
    ).first()

    if not asset:
        raise HTTPException(
            status_code = 404,
            detail = "Infrastructure asset not found"
        )
    
    asset.name = asset_update.name
    asset.asset_type = asset_update.asset_type
    asset.latitude = asset_update.latitude
    asset.longitude = asset_update.longitude
    asset.criticality = asset_update.criticality
    # updates permanent importance level

    asset.description = asset_update.description
    # updates asset description

    asset.operational_status = asset_update.operational_status
    # updates current operational state

    asset.geometry_type = asset_update.geometry_type
    # updates point/line geometry type

    asset.geometry_coordinates = asset_update.geometry_coordinates
    # updates optional bridge/route geometry coordinates

    db.commit()
    # saves changes into PostgreSQL

    db.refresh(asset)
    # reloads updated asset from database

    return asset
    # returns updated infrastructure asset
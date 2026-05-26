from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(
        Integer,
        primary_key = True,
        index = True
    )

    username = Column(
        String,
        unique = True,
        index = True,
        nullable = False
    )

    email = Column(
        String,
        unique = True,
        index = True,
        nullable = False
    )

    hashed_password = Column(
        String,
        nullable = False
    )

    role = Column(
        String,
        default = "user"
    )

    is_active = Column(
        Boolean,
        default = True
    )

    incidents = relationship(
        "Incident",
        back_populates = "owner"
    )

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key = True,
        index = True
    )

    title = Column(
        String,
        nullable = False
    )

    description = Column(
        Text,
        nullable = True
    )

    category = Column(
        String,
        nullable = False
    )

    severity = Column(
        Integer,
        default = 1
    )

    status = Column(
        String,
        default = "open"
    )

    latitude = Column(
        Float,
        nullable = True
    )

    longitude = Column(
        Float,
        nullable = True
    )

    image_path = Column(
        String,
        nullable = True
    )

    image_analysis = Column(
        Text,
        nullable = True
    )

    created_at = Column(
        DateTime,
        default = datetime.utcnow
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    owner = relationship(
        "User",
        back_populates = "incidents"
    )

    image_analysis = Column(
        Text, nullable = True
    )
    
    llm_summary = Column(
        Text, nullable = True
    )

    
class InfrastructureAsset(Base):
    __tablename__ = "infrastructure_assets"
    #actual postgresql table name

    id = Column(Integer, primary_key = True, index = True)
    # unique numeric id for each asset
    # primary_key=True makes it the main identifier
    # index=True speeds up database lookups

    name = Column(String, nullable = False)

    asset_type = Column(String, nullable = False)
    
    latitude = Column(Float, nullable = False)

    longitude = Column(Float, nullable = False)

    criticality = Column(String, default = "MEDIUM")

    description = Column(String, nullable = True)

    operational_status = Column(String, default="NORMAL")
    
    risk_status = Column(String, default="NORMAL")
    # stores whether asset is normal, directly affected, or cascade affected

    #for the Bridge-like problem (not a point asset)
    geometry_type = Column(String, default = "point")
    #tells backend if our asset is a point or a ine

    geometry_coordinates = Column(String, nullable = True)
    #stores line coordinates as JSON text for bridges and ROUTES


class InfrastructureDependency(Base):
    __tablename__ = "infrastructure_dependencies"
    id = Column(Integer, primary_key = True, index = True)
    source_asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"))
    dependent_asset_id = Column(Integer, ForeignKey("infrastructure_assets.id"))
    dependency_type = Column(String, default = "operational")
    description = Column(String, nullable = True)

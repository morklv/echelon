from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional



class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "operator"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = ConfigDict(
        from_attributes = True
    )


class IncidentCreate(BaseModel):
    title: str = Field(
        min_length = 3,
        max_length = 100
    )

    description: Optional[str] = Field(
        min_length = 5,
        max_length = 1000
    )

    category: str = Field(
        min_length = 3,
        max_length = 50
    )

    severity: int = Field(ge = 1, le= 5)

    latitude:  Optional[float] = Field(
        ge = -90,
        le = 90
    ) #valid Earth latitude range

    longitude: Optional[float] = Field(
        ge = -180,
        le=180
    ) #valid Earth longitude range


class IncidentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    severity: int
    status: str

    latitude: Optional[float]
    longitude: Optional[float]

    image_path: Optional[str] = None
    image_analysis: Optional[str] = None

    owner_id: int

    model_config = ConfigDict(
        from_attributes = True
    )
    
    llm_summary: Optional[str] = None


class IncidentUpdate(BaseModel):
    # schema for partially updating an incident

    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )
    # optional new title

    description: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=1000
    )
    # optional new description

    category: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50
    )
    # optional new category

    status: Optional[str] = None
    # optional new status

    severity: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )
    # optional severity from 1 to 5

class InfrastructureAssetCreate(BaseModel):
    #schema to create a new asset from api request
    
    name: str
    asset_type: str
    latitude: float
    longitude: float
    criticality: str = "MEDIUM"
    description: str | None = None
    operational_status: str = "NORMAL"
    geometry_type: str = "point"
    #tells if an asset is a point or a line
    geometry_coordinates: str | None = None
    #stores bridge/route coordinates as JSON text

class InfrastructureAssetResponse(InfrastructureAssetCreate):
    # schema for sending infrastructure asset back to frontend

    id: int
    # database id created by PostgreSQL

    risk_status: str = "NORMAL"
    # sends NORMAL, DIRECT_RISK, or CASCADE_RISK to frontend

    model_config = ConfigDict(
        from_attributes = True
    )
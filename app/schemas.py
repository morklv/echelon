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
    ) 

    longitude: Optional[float] = Field(
        ge = -180,
        le=180
    ) 

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

    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )


    description: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=1000
    )


    category: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50
    )


    status: Optional[str] = None


    severity: Optional[int] = Field(
        default=None,
        ge=1,
        le=5
    )


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
    geometry_coordinates: str | None = None

class InfrastructureAssetResponse(InfrastructureAssetCreate):

    id: int

    risk_status: str = "NORMAL"

    model_config = ConfigDict(
        from_attributes = True
    )
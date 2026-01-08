from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    workspace_id: int

    class Config:
        from_attributes = True


class WorkspaceOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PipelineCreate(BaseModel):
    name: str


class PipelineOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class StageCreate(BaseModel):
    name: str
    position: int = 0


class StageOut(BaseModel):
    id: int
    pipeline_id: int
    name: str
    position: int

    class Config:
        from_attributes = True


class DealCreate(BaseModel):
    title: str
    value: float = 0
    stage_id: int
    notes: Optional[str] = None


class DealOut(BaseModel):
    id: int
    pipeline_id: int
    stage_id: int
    title: str
    value: float
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DealUpdate(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    notes: Optional[str] = None


class DealStageUpdate(BaseModel):
    stage_id: int

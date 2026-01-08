from pydantic import BaseModel


class StageBase(BaseModel):
    name: str
    position: int
    pipeline_id: int


class StageCreate(StageBase):
    pass


class StageUpdate(BaseModel):
    name: str | None = None
    position: int | None = None


class StageOut(StageBase):
    id: int

    class Config:
        from_attributes = True

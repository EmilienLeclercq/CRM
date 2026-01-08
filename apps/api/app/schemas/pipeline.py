from pydantic import BaseModel


class PipelineBase(BaseModel):
    name: str


class PipelineCreate(PipelineBase):
    pass


class PipelineOut(PipelineBase):
    id: int

    class Config:
        from_attributes = True

import datetime

from pydantic import BaseModel


class DealBase(BaseModel):
    title: str
    amount: float
    currency: str = "EUR"
    stage_id: int
    owner_id: int | None = None
    priority: int = 1
    expected_close_date: datetime.date | None = None


class DealCreate(DealBase):
    pass


class DealUpdate(BaseModel):
    title: str | None = None
    amount: float | None = None
    currency: str | None = None
    stage_id: int | None = None
    owner_id: int | None = None
    priority: int | None = None
    expected_close_date: datetime.date | None = None


class DealOut(DealBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class DealStageUpdate(BaseModel):
    stage_id: int

import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(10), default="EUR")
    priority: Mapped[int] = mapped_column(Integer, default=1)
    expected_close_date: Mapped[datetime.date | None] = mapped_column(Date)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )
    stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"))
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"))

    stage: Mapped["Stage"] = relationship(back_populates="deals")
    owner: Mapped["User"] = relationship(back_populates="deals")
    workspace: Mapped["Workspace"] = relationship(back_populates="deals")
    stage_history: Mapped[list["DealStageHistory"]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )

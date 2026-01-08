import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DealStageHistory(Base):
    __tablename__ = "deal_stage_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"))
    from_stage_id: Mapped[int | None] = mapped_column(ForeignKey("stages.id"))
    to_stage_id: Mapped[int] = mapped_column(ForeignKey("stages.id"))
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.utcnow
    )

    deal: Mapped["Deal"] = relationship(back_populates="stage_history")

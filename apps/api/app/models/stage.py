from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    position: Mapped[int] = mapped_column(Integer)
    pipeline_id: Mapped[int] = mapped_column(ForeignKey("pipelines.id"))

    pipeline: Mapped["Pipeline"] = relationship(back_populates="stages")
    deals: Mapped[list["Deal"]] = relationship(back_populates="stage")

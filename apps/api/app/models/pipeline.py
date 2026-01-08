from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"))

    workspace: Mapped["Workspace"] = relationship(back_populates="pipelines")
    stages: Mapped[list["Stage"]] = relationship(
        back_populates="pipeline", order_by="Stage.position", cascade="all, delete-orphan"
    )

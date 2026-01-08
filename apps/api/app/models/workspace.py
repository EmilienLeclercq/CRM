from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="workspace")
    pipelines: Mapped[list["Pipeline"]] = relationship(back_populates="workspace")
    deals: Mapped[list["Deal"]] = relationship(back_populates="workspace")

"""SQLAlchemy model for schools."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CHAR, TIMESTAMP, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.school_class import SchoolClass
    from src.models.teacher import Teacher


class School(Base):
    """Educational institution registered in EduMove."""

    __tablename__ = "schools"

    school_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(CHAR(14), unique=True)
    email: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("1"),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    teachers: Mapped[list["Teacher"]] = relationship(back_populates="school")
    classes: Mapped[list["SchoolClass"]] = relationship(back_populates="school")

    def __repr__(self) -> str:
        return f"School(school_id={self.school_id!r}, name={self.name!r})"

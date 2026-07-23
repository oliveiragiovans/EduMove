"""SQLAlchemy model for teachers."""

from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment import Assessment
    from src.models.school import School
    from src.models.school_class import SchoolClass


class TeacherRole(str, PythonEnum):
    """Access profiles supported by the teachers table."""

    ADMINISTRATOR = "Administrador"
    TEACHER = "Professor"
    COORDINATOR = "Coordenador"


class Teacher(Base):
    """Teacher and school access profile registered in EduMove."""

    __tablename__ = "teachers"

    teacher_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.school_id", name="fk_teacher_school"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[TeacherRole] = mapped_column(
        Enum(
            TeacherRole,
            values_callable=lambda roles: [role.value for role in roles],
            name="teacher_role",
            validate_strings=True,
        ),
        nullable=False,
        server_default=text("'Professor'"),
    )
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

    school: Mapped["School"] = relationship(back_populates="teachers")
    classes: Mapped[list["SchoolClass"]] = relationship(back_populates="teacher")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="teacher")

    def __repr__(self) -> str:
        return f"Teacher(teacher_id={self.teacher_id!r}, name={self.name!r})"

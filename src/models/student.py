"""SQLAlchemy model for students."""

from datetime import date, datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment import Assessment
    from src.models.school_class import SchoolClass


class StudentSex(str, PythonEnum):
    """Sex values supported by the students table."""

    MALE = "Masculino"
    FEMALE = "Feminino"


class Student(Base):
    """Student currently enrolled in a school class."""

    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.class_id", name="fk_student_class"),
        nullable=False,
    )
    registration_number: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[StudentSex] = mapped_column(
        Enum(
            StudentSex,
            values_callable=lambda values: [value.value for value in values],
            name="student_sex",
            validate_strings=True,
        ),
        nullable=False,
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

    school_class: Mapped["SchoolClass"] = relationship(back_populates="students")
    assessments: Mapped[list["Assessment"]] = relationship(back_populates="student")

    def __repr__(self) -> str:
        return f"Student(student_id={self.student_id!r}, name={self.name!r})"

"""SQLAlchemy model for school classes."""

from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CHAR,
    Enum,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT, YEAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment import Assessment
    from src.models.school import School
    from src.models.student import Student
    from src.models.teacher import Teacher


class EducationLevel(str, PythonEnum):
    """Education levels supported by EduMove classes."""

    EARLY_CHILDHOOD = "Educação Infantil"
    ELEMENTARY_I = "Ensino Fundamental I"
    ELEMENTARY_II = "Ensino Fundamental II"
    HIGH_SCHOOL = "Ensino Médio"


class SchoolShift(str, PythonEnum):
    """School shifts supported by EduMove."""

    MORNING = "Manhã"
    AFTERNOON = "Tarde"
    FULL_TIME = "Integral"
    NIGHT = "Noite"


class SchoolClass(Base):
    """A school class for a specific grade, section, and academic year."""

    __tablename__ = "classes"
    __table_args__ = (
        UniqueConstraint(
            "school_id",
            "grade_number",
            "section",
            "academic_year",
            name="uq_class",
        ),
    )

    class_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(
        ForeignKey("schools.school_id", name="fk_class_school"),
        nullable=False,
    )
    teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.teacher_id", name="fk_class_teacher"),
    )
    grade_number: Mapped[int] = mapped_column(TINYINT, nullable=False)
    education_level: Mapped[EducationLevel] = mapped_column(
        Enum(
            EducationLevel,
            values_callable=lambda levels: [level.value for level in levels],
            name="education_level",
            validate_strings=True,
        ),
        nullable=False,
    )
    section: Mapped[str] = mapped_column(CHAR(1), nullable=False)
    academic_year: Mapped[int] = mapped_column(YEAR, nullable=False)
    shift: Mapped[SchoolShift] = mapped_column(
        Enum(
            SchoolShift,
            values_callable=lambda shifts: [shift.value for shift in shifts],
            name="school_shift",
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

    school: Mapped["School"] = relationship(back_populates="classes")
    teacher: Mapped["Teacher | None"] = relationship(back_populates="classes")
    students: Mapped[list["Student"]] = relationship(back_populates="school_class")
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="school_class"
    )

    def __repr__(self) -> str:
        return (
            "SchoolClass("
            f"class_id={self.class_id!r}, "
            f"grade_number={self.grade_number!r}, "
            f"section={self.section!r}, "
            f"academic_year={self.academic_year!r}"
            ")"
        )

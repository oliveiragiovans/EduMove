"""SQLAlchemy model for student assessments."""

from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Numeric,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import conv

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment_result import AssessmentResult
    from src.models.school_class import SchoolClass
    from src.models.student import Student
    from src.models.teacher import Teacher


class Assessment(Base):
    """Assessment event performed for one student."""

    __tablename__ = "assessments"
    __table_args__ = (
        CheckConstraint(
            "weight_kg IS NULL OR weight_kg > 0",
            name=conv("chk_assessment_weight"),
        ),
        CheckConstraint(
            "height_cm IS NULL OR height_cm > 0",
            name=conv("chk_assessment_height"),
        ),
    )

    assessment_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.student_id", name="fk_assessment_student"),
        nullable=False,
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.teacher_id", name="fk_assessment_teacher"),
        nullable=False,
    )
    class_id: Mapped[int] = mapped_column(
        ForeignKey("classes.class_id", name="fk_assessment_class"),
        nullable=False,
    )
    assessment_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)
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

    student: Mapped["Student"] = relationship(back_populates="assessments")
    teacher: Mapped["Teacher"] = relationship(back_populates="assessments")
    school_class: Mapped["SchoolClass"] = relationship(back_populates="assessments")
    results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="assessment"
    )

    @property
    def bmi(self) -> Decimal | None:
        """Calculate BMI from the assessment's mass and height."""

        if (
            self.weight_kg is None
            or self.height_cm is None
            or self.weight_kg <= 0
            or self.height_cm <= 0
        ):
            return None

        height_m = self.height_cm / Decimal("100")
        return (self.weight_kg / height_m**2).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def __repr__(self) -> str:
        return (
            "Assessment("
            f"assessment_id={self.assessment_id!r}, "
            f"student_id={self.student_id!r}, "
            f"assessment_date={self.assessment_date!r}"
            ")"
        )

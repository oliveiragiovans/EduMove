"""SQLAlchemy model for individual motor-test attempts."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Numeric,
    String,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import conv

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment import Assessment
    from src.models.motor_test import MotorTest


class AssessmentResult(Base):
    """One attempt for one motor test within an assessment."""

    __tablename__ = "assessment_results"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "motor_test_id",
            "attempt_number",
            name="uq_assessment_test_attempt",
        ),
        CheckConstraint(
            "result_value >= 0",
            name=conv("chk_result_value"),
        ),
        CheckConstraint(
            "attempt_number > 0",
            name=conv("chk_attempt_number"),
        ),
    )

    assessment_result_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "assessments.assessment_id",
            name="fk_result_assessment",
        ),
        nullable=False,
    )
    motor_test_id: Mapped[int] = mapped_column(
        ForeignKey(
            "motor_tests.motor_test_id",
            name="fk_result_motor_test",
        ),
        nullable=False,
    )
    attempt_number: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        server_default=text("1"),
    )
    result_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(String(255))
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

    assessment: Mapped["Assessment"] = relationship(back_populates="results")
    motor_test: Mapped["MotorTest"] = relationship(back_populates="results")

    def __repr__(self) -> str:
        return (
            "AssessmentResult("
            f"assessment_result_id={self.assessment_result_id!r}, "
            f"assessment_id={self.assessment_id!r}, "
            f"motor_test_id={self.motor_test_id!r}, "
            f"attempt_number={self.attempt_number!r}, "
            f"result_value={self.result_value!r}"
            ")"
        )

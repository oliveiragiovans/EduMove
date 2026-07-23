"""SQLAlchemy model for configurable motor tests."""

from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    String,
    Text,
    TIMESTAMP,
    text,
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import conv

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.assessment_result import AssessmentResult


class ResultDirection(str, PythonEnum):
    """How a motor-test result should be interpreted."""

    HIGHER = "higher"
    LOWER = "lower"
    NEUTRAL = "neutral"


class ResultType(str, PythonEnum):
    """How each attempt is recorded."""

    MEASUREMENT = "measurement"
    BINARY = "binary"


class AggregationMethod(str, PythonEnum):
    """How multiple attempts are combined into a final result."""

    MAXIMUM = "maximum"
    MINIMUM = "minimum"
    SUM = "sum"
    AVERAGE = "average"


class MotorTest(Base):
    """Motor-test definition and protocol metadata."""

    __tablename__ = "motor_tests"
    __table_args__ = (
        CheckConstraint(
            (
                "min_attempts > 0 "
                "AND max_attempts >= min_attempts "
                "AND default_attempts BETWEEN min_attempts AND max_attempts"
            ),
            name=conv("chk_motor_test_attempts"),
        ),
    )

    motor_test_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    result_direction: Mapped[ResultDirection] = mapped_column(
        Enum(
            ResultDirection,
            values_callable=lambda values: [value.value for value in values],
            name="result_direction",
            validate_strings=True,
        ),
        nullable=False,
        server_default=text("'higher'"),
    )
    result_type: Mapped[ResultType] = mapped_column(
        Enum(
            ResultType,
            values_callable=lambda values: [value.value for value in values],
            name="motor_test_result_type",
            validate_strings=True,
        ),
        nullable=False,
        server_default=text("'measurement'"),
    )
    aggregation_method: Mapped[AggregationMethod] = mapped_column(
        Enum(
            AggregationMethod,
            values_callable=lambda values: [value.value for value in values],
            name="aggregation_method",
            validate_strings=True,
        ),
        nullable=False,
        server_default=text("'maximum'"),
    )
    default_attempts: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        server_default=text("2"),
    )
    min_attempts: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        server_default=text("2"),
    )
    max_attempts: Mapped[int] = mapped_column(
        TINYINT(unsigned=True),
        nullable=False,
        server_default=text("2"),
    )
    protocol_name: Mapped[str | None] = mapped_column(String(100))
    protocol_version: Mapped[str | None] = mapped_column(String(50))
    protocol_source: Mapped[str | None] = mapped_column(String(255))
    protocol_description: Mapped[str | None] = mapped_column(Text)
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

    results: Mapped[list["AssessmentResult"]] = relationship(
        back_populates="motor_test"
    )

    def __repr__(self) -> str:
        return (
            "MotorTest("
            f"motor_test_id={self.motor_test_id!r}, "
            f"code={self.code!r}, "
            f"name={self.name!r}"
            ")"
        )

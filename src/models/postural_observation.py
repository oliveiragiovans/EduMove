"""SQLAlchemy models for educational postural observations."""

from datetime import datetime
from enum import Enum as PythonEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Integer,
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


class PosturalRegion(str, PythonEnum):
    """Body regions included in the educational posture screening."""

    SHOULDERS = "shoulders"
    SPINE = "spine"
    KNEES = "knees"
    FEET = "feet"


class PosturalView(str, PythonEnum):
    """Viewing positions used by the postural option catalog."""

    FRONTAL = "frontal"
    LATERAL = "lateral"
    REFERENCE = "reference"


class PosturalObservationOption(Base):
    """One selectable pedagogical observation from the posture catalog."""

    __tablename__ = "postural_observation_options"
    __table_args__ = (
        CheckConstraint(
            "sort_order > 0",
            name=conv("chk_postural_option_sort_order"),
        ),
    )

    postural_option_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    code: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
    )
    region: Mapped[PosturalRegion] = mapped_column(
        Enum(
            PosturalRegion,
            values_callable=lambda values: [value.value for value in values],
            name="postural_region",
            validate_strings=True,
        ),
        nullable=False,
    )
    view_position: Mapped[PosturalView] = mapped_column(
        Enum(
            PosturalView,
            values_callable=lambda values: [value.value for value in values],
            name="postural_view",
            validate_strings=True,
        ),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    reference_image_path: Mapped[str | None] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(
        Integer().with_variant(TINYINT(unsigned=True), "mysql"),
        nullable=False,
        server_default=text("1"),
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

    observations: Mapped[list["AssessmentPosturalObservation"]] = relationship(
        back_populates="option"
    )

    def __repr__(self) -> str:
        return (
            "PosturalObservationOption("
            f"postural_option_id={self.postural_option_id!r}, "
            f"code={self.code!r}"
            ")"
        )


class AssessmentPosturalObservation(Base):
    """One selected postural option within an assessment."""

    __tablename__ = "assessment_postural_observations"
    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "postural_option_id",
            name="uq_assessment_postural_option",
        ),
    )

    postural_observation_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )
    assessment_id: Mapped[int] = mapped_column(
        ForeignKey(
            "assessments.assessment_id",
            name="fk_postural_observation_assessment",
        ),
        nullable=False,
    )
    postural_option_id: Mapped[int] = mapped_column(
        ForeignKey(
            "postural_observation_options.postural_option_id",
            name="fk_postural_observation_option",
        ),
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

    assessment: Mapped["Assessment"] = relationship(
        back_populates="postural_observations"
    )
    option: Mapped[PosturalObservationOption] = relationship(
        back_populates="observations"
    )

    def __repr__(self) -> str:
        return (
            "AssessmentPosturalObservation("
            f"postural_observation_id={self.postural_observation_id!r}, "
            f"assessment_id={self.assessment_id!r}, "
            f"postural_option_id={self.postural_option_id!r}"
            ")"
        )

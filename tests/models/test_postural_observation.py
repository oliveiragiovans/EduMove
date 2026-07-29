"""Tests for the educational postural-observation models."""

from sqlalchemy import CheckConstraint, Enum, UniqueConstraint, inspect
from sqlalchemy.dialects.mysql import TINYINT, dialect

from src.models.assessment import Assessment
from src.models.postural_observation import (
    AssessmentPosturalObservation,
    PosturalObservationOption,
    PosturalRegion,
    PosturalView,
)


def test_postural_option_uses_expected_columns() -> None:
    assert PosturalObservationOption.__tablename__ == (
        "postural_observation_options"
    )
    assert set(PosturalObservationOption.__table__.columns.keys()) == {
        "postural_option_id",
        "code",
        "region",
        "view_position",
        "label",
        "description",
        "reference_image_path",
        "sort_order",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_postural_option_enums_match_catalog_values() -> None:
    columns = PosturalObservationOption.__table__.c

    assert isinstance(columns.region.type, Enum)
    assert columns.region.type.enums == [
        "shoulders",
        "spine",
        "knees",
        "feet",
    ]
    assert isinstance(columns.view_position.type, Enum)
    assert columns.view_position.type.enums == [
        "frontal",
        "lateral",
        "reference",
    ]
    assert set(PosturalRegion) == {
        PosturalRegion.SHOULDERS,
        PosturalRegion.SPINE,
        PosturalRegion.KNEES,
        PosturalRegion.FEET,
    }
    assert set(PosturalView) == {
        PosturalView.FRONTAL,
        PosturalView.LATERAL,
        PosturalView.REFERENCE,
    }


def test_postural_option_lengths_and_sort_order_match_schema() -> None:
    columns = PosturalObservationOption.__table__.c
    mysql_type = columns.sort_order.type.dialect_impl(dialect())

    assert columns.code.type.length == 80
    assert columns.label.type.length == 120
    assert columns.description.type.length == 255
    assert columns.reference_image_path.type.length == 255
    assert isinstance(mysql_type, TINYINT)
    assert mysql_type.unsigned is True
    check = next(
        constraint
        for constraint in PosturalObservationOption.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    )
    assert check.name == "chk_postural_option_sort_order"
    assert str(check.sqltext) == "sort_order > 0"


def test_postural_observation_uses_expected_columns_and_constraints() -> None:
    assert AssessmentPosturalObservation.__tablename__ == (
        "assessment_postural_observations"
    )
    assert set(AssessmentPosturalObservation.__table__.columns.keys()) == {
        "postural_observation_id",
        "assessment_id",
        "postural_option_id",
        "notes",
        "is_active",
        "created_at",
        "updated_at",
    }
    constraint = next(
        item
        for item in AssessmentPosturalObservation.__table__.constraints
        if isinstance(item, UniqueConstraint)
    )
    assert constraint.name == "uq_assessment_postural_option"
    assert [column.name for column in constraint.columns] == [
        "assessment_id",
        "postural_option_id",
    ]


def test_postural_observation_foreign_keys_match_schema() -> None:
    columns = AssessmentPosturalObservation.__table__.c
    assessment_fk = next(iter(columns.assessment_id.foreign_keys))
    option_fk = next(iter(columns.postural_option_id.foreign_keys))

    assert assessment_fk.target_fullname == "assessments.assessment_id"
    assert assessment_fk.constraint.name == (
        "fk_postural_observation_assessment"
    )
    assert option_fk.target_fullname == (
        "postural_observation_options.postural_option_id"
    )
    assert option_fk.constraint.name == "fk_postural_observation_option"


def test_postural_relationships_are_bidirectional() -> None:
    observation_mapper = inspect(AssessmentPosturalObservation)

    assert observation_mapper.relationships.assessment.mapper.class_ is Assessment
    assert (
        observation_mapper.relationships.assessment.back_populates
        == "postural_observations"
    )
    assert (
        inspect(Assessment).relationships.postural_observations.mapper.class_
        is AssessmentPosturalObservation
    )
    assert (
        observation_mapper.relationships.option.mapper.class_
        is PosturalObservationOption
    )
    assert observation_mapper.relationships.option.back_populates == (
        "observations"
    )


def test_postural_defaults_and_timestamps_are_database_managed() -> None:
    option_columns = PosturalObservationOption.__table__.c
    observation_columns = AssessmentPosturalObservation.__table__.c

    assert str(option_columns.sort_order.server_default.arg) == "1"
    assert str(option_columns.is_active.server_default.arg) == "1"
    assert str(observation_columns.is_active.server_default.arg) == "1"
    assert option_columns.created_at.server_default is not None
    assert option_columns.updated_at.server_onupdate is not None
    assert observation_columns.created_at.server_default is not None
    assert observation_columns.updated_at.server_onupdate is not None

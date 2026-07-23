"""Tests for the AssessmentResult SQLAlchemy model."""

from sqlalchemy import CheckConstraint, Numeric, UniqueConstraint, inspect
from sqlalchemy.dialects.mysql import TINYINT

from src.models.assessment import Assessment
from src.models.assessment_result import AssessmentResult
from src.models.motor_test import MotorTest


def test_assessment_result_uses_expected_table_and_columns() -> None:
    assert AssessmentResult.__tablename__ == "assessment_results"
    assert set(AssessmentResult.__table__.columns.keys()) == {
        "assessment_result_id",
        "assessment_id",
        "motor_test_id",
        "attempt_number",
        "result_value",
        "notes",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_assessment_result_required_and_optional_fields_match_schema() -> None:
    columns = AssessmentResult.__table__.c

    assert all(
        column.nullable is False
        for column in (
            columns.assessment_id,
            columns.motor_test_id,
            columns.attempt_number,
            columns.result_value,
            columns.is_active,
        )
    )
    assert columns.notes.nullable is True


def test_assessment_result_value_and_attempt_types_match_schema() -> None:
    columns = AssessmentResult.__table__.c

    assert isinstance(columns.attempt_number.type, TINYINT)
    assert columns.attempt_number.type.unsigned is True
    assert isinstance(columns.result_value.type, Numeric)
    assert (
        columns.result_value.type.precision,
        columns.result_value.type.scale,
    ) == (10, 2)
    assert columns.notes.type.length == 255


def test_assessment_result_unique_constraint_matches_schema() -> None:
    constraint = next(
        item
        for item in AssessmentResult.__table__.constraints
        if isinstance(item, UniqueConstraint)
    )

    assert constraint.name == "uq_assessment_test_attempt"
    assert [column.name for column in constraint.columns] == [
        "assessment_id",
        "motor_test_id",
        "attempt_number",
    ]


def test_assessment_result_check_constraints_match_schema() -> None:
    constraints = {
        item.name: str(item.sqltext)
        for item in AssessmentResult.__table__.constraints
        if isinstance(item, CheckConstraint)
    }

    assert constraints == {
        "chk_result_value": "result_value >= 0",
        "chk_attempt_number": "attempt_number > 0",
    }


def test_assessment_result_foreign_keys_match_schema() -> None:
    assessment_fk = next(
        iter(AssessmentResult.__table__.c.assessment_id.foreign_keys)
    )
    motor_test_fk = next(
        iter(AssessmentResult.__table__.c.motor_test_id.foreign_keys)
    )

    assert assessment_fk.target_fullname == "assessments.assessment_id"
    assert assessment_fk.constraint.name == "fk_result_assessment"
    assert motor_test_fk.target_fullname == "motor_tests.motor_test_id"
    assert motor_test_fk.constraint.name == "fk_result_motor_test"


def test_assessment_result_relationships_are_bidirectional() -> None:
    result_mapper = inspect(AssessmentResult)

    assert result_mapper.relationships.assessment.mapper.class_ is Assessment
    assert result_mapper.relationships.assessment.back_populates == "results"
    assert inspect(Assessment).relationships.results.mapper.class_ is AssessmentResult

    assert result_mapper.relationships.motor_test.mapper.class_ is MotorTest
    assert result_mapper.relationships.motor_test.back_populates == "results"
    assert inspect(MotorTest).relationships.results.mapper.class_ is AssessmentResult


def test_assessment_result_defaults_and_timestamps_are_managed_by_database() -> None:
    columns = AssessmentResult.__table__.c

    assert str(columns.attempt_number.server_default.arg) == "1"
    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

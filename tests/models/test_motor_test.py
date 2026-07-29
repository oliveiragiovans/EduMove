"""Tests for the MotorTest SQLAlchemy model."""

from sqlalchemy import CheckConstraint, Enum, Text
from sqlalchemy.dialects.mysql import TINYINT, dialect

from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultDirection,
    ResultType,
)


def test_motor_test_uses_expected_table_and_columns() -> None:
    assert MotorTest.__tablename__ == "motor_tests"
    assert set(MotorTest.__table__.columns.keys()) == {
        "motor_test_id",
        "code",
        "name",
        "unit",
        "result_direction",
        "result_type",
        "aggregation_method",
        "default_attempts",
        "min_attempts",
        "max_attempts",
        "protocol_name",
        "protocol_version",
        "protocol_source",
        "protocol_description",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_motor_test_required_and_optional_fields_match_schema() -> None:
    columns = MotorTest.__table__.c

    assert all(
        column.nullable is False
        for column in (
            columns.code,
            columns.name,
            columns.unit,
            columns.result_direction,
            columns.result_type,
            columns.aggregation_method,
            columns.default_attempts,
            columns.min_attempts,
            columns.max_attempts,
            columns.is_active,
        )
    )
    assert columns.protocol_name.nullable is True
    assert columns.protocol_version.nullable is True
    assert columns.protocol_source.nullable is True
    assert columns.protocol_description.nullable is True


def test_motor_test_text_fields_match_schema() -> None:
    columns = MotorTest.__table__.c

    assert columns.code.type.length == 50
    assert columns.name.type.length == 150
    assert columns.unit.type.length == 30
    assert columns.protocol_name.type.length == 100
    assert columns.protocol_version.type.length == 50
    assert columns.protocol_source.type.length == 255
    assert isinstance(columns.protocol_description.type, Text)
    assert columns.code.unique is True


def test_motor_test_result_direction_values_match_schema() -> None:
    enum_type = MotorTest.__table__.c.result_direction.type

    assert isinstance(enum_type, Enum)
    assert enum_type.enums == [value.value for value in ResultDirection]


def test_motor_test_result_type_values_match_schema() -> None:
    enum_type = MotorTest.__table__.c.result_type.type

    assert isinstance(enum_type, Enum)
    assert enum_type.enums == [value.value for value in ResultType]


def test_motor_test_aggregation_values_match_schema() -> None:
    enum_type = MotorTest.__table__.c.aggregation_method.type

    assert isinstance(enum_type, Enum)
    assert enum_type.enums == [value.value for value in AggregationMethod]


def test_motor_test_attempt_limits_match_schema() -> None:
    columns = MotorTest.__table__.c
    mysql_dialect = dialect()

    assert all(
        isinstance(column.type.dialect_impl(mysql_dialect), TINYINT)
        and column.type.dialect_impl(mysql_dialect).unsigned is True
        for column in (
            columns.default_attempts,
            columns.min_attempts,
            columns.max_attempts,
        )
    )

    constraint = next(
        item
        for item in MotorTest.__table__.constraints
        if isinstance(item, CheckConstraint)
    )
    assert constraint.name == "chk_motor_test_attempts"
    assert "default_attempts BETWEEN min_attempts AND max_attempts" in str(
        constraint.sqltext
    )


def test_motor_test_defaults_and_timestamps_are_managed_by_database() -> None:
    columns = MotorTest.__table__.c

    assert str(columns.result_direction.server_default.arg) == "'higher'"
    assert str(columns.result_type.server_default.arg) == "'measurement'"
    assert str(columns.aggregation_method.server_default.arg) == "'maximum'"
    assert str(columns.default_attempts.server_default.arg) == "2"
    assert str(columns.min_attempts.server_default.arg) == "2"
    assert str(columns.max_attempts.server_default.arg) == "2"
    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

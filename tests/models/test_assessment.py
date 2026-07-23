"""Tests for the Assessment SQLAlchemy model."""

from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, Text, inspect

from src.models.assessment import Assessment
from src.models.school_class import SchoolClass
from src.models.student import Student
from src.models.teacher import Teacher


def test_assessment_uses_expected_table_and_columns() -> None:
    assert Assessment.__tablename__ == "assessments"
    assert set(Assessment.__table__.columns.keys()) == {
        "assessment_id",
        "student_id",
        "teacher_id",
        "class_id",
        "assessment_date",
        "weight_kg",
        "height_cm",
        "notes",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_assessment_required_and_optional_fields_match_schema() -> None:
    columns = Assessment.__table__.c

    assert all(
        column.nullable is False
        for column in (
            columns.student_id,
            columns.teacher_id,
            columns.class_id,
            columns.assessment_date,
            columns.is_active,
        )
    )
    assert columns.weight_kg.nullable is True
    assert columns.height_cm.nullable is True
    assert columns.notes.nullable is True


def test_assessment_measurement_types_match_schema() -> None:
    columns = Assessment.__table__.c

    assert isinstance(columns.assessment_date.type, Date)
    assert isinstance(columns.weight_kg.type, Numeric)
    assert (columns.weight_kg.type.precision, columns.weight_kg.type.scale) == (5, 2)
    assert isinstance(columns.height_cm.type, Numeric)
    assert (columns.height_cm.type.precision, columns.height_cm.type.scale) == (5, 2)
    assert isinstance(columns.notes.type, Text)


def test_assessment_positive_measurement_constraints_match_schema() -> None:
    check_constraints = {
        constraint.name: str(constraint.sqltext)
        for constraint in Assessment.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert check_constraints == {
        "chk_assessment_weight": "weight_kg IS NULL OR weight_kg > 0",
        "chk_assessment_height": "height_cm IS NULL OR height_cm > 0",
    }


def test_assessment_foreign_keys_match_schema() -> None:
    expected = {
        "student_id": ("students.student_id", "fk_assessment_student"),
        "teacher_id": ("teachers.teacher_id", "fk_assessment_teacher"),
        "class_id": ("classes.class_id", "fk_assessment_class"),
    }

    for column_name, (target, constraint_name) in expected.items():
        foreign_key = next(
            iter(Assessment.__table__.c[column_name].foreign_keys)
        )
        assert foreign_key.target_fullname == target
        assert foreign_key.constraint.name == constraint_name


def test_assessment_relationships_are_bidirectional() -> None:
    assessment_mapper = inspect(Assessment)

    assert assessment_mapper.relationships.student.mapper.class_ is Student
    assert assessment_mapper.relationships.student.back_populates == "assessments"
    assert inspect(Student).relationships.assessments.mapper.class_ is Assessment

    assert assessment_mapper.relationships.teacher.mapper.class_ is Teacher
    assert assessment_mapper.relationships.teacher.back_populates == "assessments"
    assert inspect(Teacher).relationships.assessments.mapper.class_ is Assessment

    assert assessment_mapper.relationships.school_class.mapper.class_ is SchoolClass
    assert (
        assessment_mapper.relationships.school_class.back_populates == "assessments"
    )
    assert (
        inspect(SchoolClass).relationships.assessments.mapper.class_ is Assessment
    )


def test_assessment_calculates_bmi_with_two_decimal_places() -> None:
    assessment = Assessment(
        weight_kg=Decimal("53.50"),
        height_cm=Decimal("173.50"),
    )

    assert assessment.bmi == Decimal("17.77")


def test_assessment_bmi_requires_positive_mass_and_height() -> None:
    assert Assessment(weight_kg=None, height_cm=Decimal("170")).bmi is None
    assert Assessment(weight_kg=Decimal("60"), height_cm=None).bmi is None
    assert Assessment(weight_kg=Decimal("60"), height_cm=Decimal("0")).bmi is None


def test_assessment_status_and_timestamps_are_managed_by_database() -> None:
    columns = Assessment.__table__.c

    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

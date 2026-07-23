"""Tests for the Student SQLAlchemy model."""

from sqlalchemy import Date, Enum, inspect

from src.models.school_class import SchoolClass
from src.models.student import Student, StudentSex


def test_student_uses_expected_table_and_columns() -> None:
    assert Student.__tablename__ == "students"
    assert set(Student.__table__.columns.keys()) == {
        "student_id",
        "class_id",
        "registration_number",
        "name",
        "birth_date",
        "sex",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_student_required_and_optional_fields_match_schema() -> None:
    columns = Student.__table__.c

    assert columns.registration_number.nullable is True
    assert all(
        column.nullable is False
        for column in (
            columns.class_id,
            columns.name,
            columns.birth_date,
            columns.sex,
            columns.is_active,
        )
    )


def test_student_field_types_and_lengths_match_schema() -> None:
    columns = Student.__table__.c

    assert columns.registration_number.type.length == 20
    assert columns.name.type.length == 100
    assert isinstance(columns.birth_date.type, Date)


def test_student_sex_values_match_database_enum() -> None:
    sex_type = Student.__table__.c.sex.type

    assert isinstance(sex_type, Enum)
    assert sex_type.enums == [value.value for value in StudentSex]


def test_student_registration_number_is_unique() -> None:
    assert Student.__table__.c.registration_number.unique is True


def test_student_references_school_class() -> None:
    foreign_key = next(iter(Student.__table__.c.class_id.foreign_keys))

    assert foreign_key.target_fullname == "classes.class_id"
    assert foreign_key.constraint.name == "fk_student_class"


def test_student_and_school_class_relationship_is_bidirectional() -> None:
    student_class = inspect(Student).relationships.school_class
    class_students = inspect(SchoolClass).relationships.students

    assert student_class.mapper.class_ is SchoolClass
    assert student_class.back_populates == "students"
    assert student_class.uselist is False

    assert class_students.mapper.class_ is Student
    assert class_students.back_populates == "school_class"
    assert class_students.uselist is True


def test_student_status_and_timestamps_are_managed_by_database() -> None:
    columns = Student.__table__.c

    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

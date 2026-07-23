"""Tests for the Teacher SQLAlchemy model."""

from sqlalchemy import Enum, inspect

from src.models.school import School
from src.models.teacher import Teacher, TeacherRole


def test_teacher_uses_expected_table_and_columns() -> None:
    assert Teacher.__tablename__ == "teachers"
    assert set(Teacher.__table__.columns.keys()) == {
        "teacher_id",
        "school_id",
        "name",
        "email",
        "password_hash",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_teacher_required_fields_match_schema() -> None:
    columns = Teacher.__table__.c

    assert all(
        column.nullable is False
        for column in (
            columns.school_id,
            columns.name,
            columns.email,
            columns.password_hash,
            columns.role,
            columns.is_active,
        )
    )
    assert columns.email.unique is True


def test_teacher_text_field_lengths_match_schema() -> None:
    columns = Teacher.__table__.c

    assert columns.name.type.length == 100
    assert columns.email.type.length == 100
    assert columns.password_hash.type.length == 255


def test_teacher_roles_match_database_enum() -> None:
    role_type = Teacher.__table__.c.role.type

    assert isinstance(role_type, Enum)
    assert role_type.enums == [
        TeacherRole.ADMINISTRATOR.value,
        TeacherRole.TEACHER.value,
        TeacherRole.COORDINATOR.value,
    ]
    assert str(Teacher.__table__.c.role.server_default.arg) == "'Professor'"


def test_teacher_references_school() -> None:
    foreign_key = next(iter(Teacher.__table__.c.school_id.foreign_keys))

    assert foreign_key.target_fullname == "schools.school_id"
    assert foreign_key.constraint.name == "fk_teacher_school"


def test_teacher_and_school_relationship_is_bidirectional() -> None:
    teacher_school = inspect(Teacher).relationships.school
    school_teachers = inspect(School).relationships.teachers

    assert teacher_school.mapper.class_ is School
    assert teacher_school.back_populates == "teachers"
    assert teacher_school.uselist is False

    assert school_teachers.mapper.class_ is Teacher
    assert school_teachers.back_populates == "school"
    assert school_teachers.uselist is True


def test_teacher_status_and_timestamps_are_managed_by_database() -> None:
    columns = Teacher.__table__.c

    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

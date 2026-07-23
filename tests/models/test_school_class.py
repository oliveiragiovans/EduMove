"""Tests for the SchoolClass SQLAlchemy model."""

from sqlalchemy import Enum, UniqueConstraint, inspect
from sqlalchemy.dialects.mysql import TINYINT, YEAR

from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.teacher import Teacher


def test_school_class_uses_expected_table_and_columns() -> None:
    assert SchoolClass.__tablename__ == "classes"
    assert set(SchoolClass.__table__.columns.keys()) == {
        "class_id",
        "school_id",
        "teacher_id",
        "grade_number",
        "education_level",
        "section",
        "academic_year",
        "shift",
        "is_active",
        "created_at",
        "updated_at",
    }


def test_school_class_required_and_optional_fields_match_schema() -> None:
    columns = SchoolClass.__table__.c

    assert columns.teacher_id.nullable is True
    assert all(
        column.nullable is False
        for column in (
            columns.school_id,
            columns.grade_number,
            columns.education_level,
            columns.section,
            columns.academic_year,
            columns.shift,
            columns.is_active,
        )
    )


def test_school_class_specialized_types_match_schema() -> None:
    columns = SchoolClass.__table__.c

    assert isinstance(columns.grade_number.type, TINYINT)
    assert columns.section.type.length == 1
    assert isinstance(columns.academic_year.type, YEAR)


def test_school_class_enums_match_schema() -> None:
    education_level_type = SchoolClass.__table__.c.education_level.type
    shift_type = SchoolClass.__table__.c.shift.type

    assert isinstance(education_level_type, Enum)
    assert education_level_type.enums == [level.value for level in EducationLevel]
    assert isinstance(shift_type, Enum)
    assert shift_type.enums == [shift.value for shift in SchoolShift]


def test_school_class_foreign_keys_match_schema() -> None:
    school_fk = next(iter(SchoolClass.__table__.c.school_id.foreign_keys))
    teacher_fk = next(iter(SchoolClass.__table__.c.teacher_id.foreign_keys))

    assert school_fk.target_fullname == "schools.school_id"
    assert school_fk.constraint.name == "fk_class_school"
    assert teacher_fk.target_fullname == "teachers.teacher_id"
    assert teacher_fk.constraint.name == "fk_class_teacher"


def test_school_class_unique_constraint_matches_business_rule() -> None:
    unique_constraints = [
        constraint
        for constraint in SchoolClass.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    ]
    class_constraint = next(
        constraint
        for constraint in unique_constraints
        if constraint.name == "uq_class"
    )

    assert [column.name for column in class_constraint.columns] == [
        "school_id",
        "grade_number",
        "section",
        "academic_year",
    ]


def test_school_class_relationships_are_bidirectional() -> None:
    class_mapper = inspect(SchoolClass)
    school_mapper = inspect(School)
    teacher_mapper = inspect(Teacher)

    assert class_mapper.relationships.school.mapper.class_ is School
    assert class_mapper.relationships.school.back_populates == "classes"
    assert class_mapper.relationships.school.uselist is False

    assert class_mapper.relationships.teacher.mapper.class_ is Teacher
    assert class_mapper.relationships.teacher.back_populates == "classes"
    assert class_mapper.relationships.teacher.uselist is False

    assert school_mapper.relationships.classes.mapper.class_ is SchoolClass
    assert school_mapper.relationships.classes.back_populates == "school"
    assert school_mapper.relationships.classes.uselist is True

    assert teacher_mapper.relationships.classes.mapper.class_ is SchoolClass
    assert teacher_mapper.relationships.classes.back_populates == "teacher"
    assert teacher_mapper.relationships.classes.uselist is True


def test_school_class_status_and_timestamps_are_managed_by_database() -> None:
    columns = SchoolClass.__table__.c

    assert str(columns.is_active.server_default.arg) == "1"
    assert columns.created_at.server_default is not None
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

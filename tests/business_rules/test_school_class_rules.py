"""Tests for school-class validation and normalization rules."""

import pytest

from src.business_rules.school_class_rules import (
    SchoolClassValidationError,
    normalize_school_class_changes,
    normalize_school_class_data,
)
from src.models.school_class import EducationLevel, SchoolShift


def test_normalize_school_class_data_cleans_and_converts_fields() -> None:
    data = normalize_school_class_data(
        teacher_id=7,
        grade_number=5,
        education_level=" ensino fundamental i ",
        section=" a ",
        academic_year=2026,
        shift=" manhã ",
    )

    assert data == {
        "teacher_id": 7,
        "grade_number": 5,
        "education_level": EducationLevel.ELEMENTARY_I,
        "section": "A",
        "academic_year": 2026,
        "shift": SchoolShift.MORNING,
    }


def test_normalize_school_class_data_accepts_enums_and_no_teacher() -> None:
    data = normalize_school_class_data(
        grade_number=2,
        education_level=EducationLevel.EARLY_CHILDHOOD,
        section="B",
        academic_year=2027,
        shift=SchoolShift.FULL_TIME,
    )

    assert data["teacher_id"] is None
    assert data["education_level"] is EducationLevel.EARLY_CHILDHOOD
    assert data["shift"] is SchoolShift.FULL_TIME


@pytest.mark.parametrize("value", [0, 100, True, "5"])
def test_normalize_school_class_data_rejects_invalid_grade(
    value: object,
) -> None:
    with pytest.raises(SchoolClassValidationError) as error:
        normalize_school_class_data(
            grade_number=value,
            education_level=EducationLevel.ELEMENTARY_I,
            section="A",
            academic_year=2026,
            shift=SchoolShift.MORNING,
        )

    assert error.value.field == "grade_number"


@pytest.mark.parametrize("value", [1999, 2101, False, "2026"])
def test_normalize_school_class_data_rejects_invalid_academic_year(
    value: object,
) -> None:
    with pytest.raises(SchoolClassValidationError) as error:
        normalize_school_class_data(
            grade_number=5,
            education_level=EducationLevel.ELEMENTARY_I,
            section="A",
            academic_year=value,
            shift=SchoolShift.MORNING,
        )

    assert error.value.field == "academic_year"


@pytest.mark.parametrize("value", ["", "AB", "1", None])
def test_normalize_school_class_data_rejects_invalid_section(
    value: object,
) -> None:
    with pytest.raises(SchoolClassValidationError) as error:
        normalize_school_class_data(
            grade_number=5,
            education_level=EducationLevel.ELEMENTARY_I,
            section=value,
            academic_year=2026,
            shift=SchoolShift.MORNING,
        )

    assert error.value.field == "section"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("education_level", "Ensino Superior"),
        ("shift", "Madrugada"),
        ("teacher_id", 0),
    ],
)
def test_normalize_school_class_data_rejects_other_invalid_fields(
    field: str,
    value: object,
) -> None:
    data = {
        "teacher_id": 1,
        "grade_number": 5,
        "education_level": EducationLevel.ELEMENTARY_I,
        "section": "A",
        "academic_year": 2026,
        "shift": SchoolShift.MORNING,
    }
    data[field] = value

    with pytest.raises(SchoolClassValidationError) as error:
        normalize_school_class_data(**data)

    assert error.value.field == field


def test_normalize_school_class_changes_accepts_partial_updates() -> None:
    assert normalize_school_class_changes(
        {
            "teacher_id": None,
            "section": " c ",
            "shift": "TARDE",
        }
    ) == {
        "teacher_id": None,
        "section": "C",
        "shift": SchoolShift.AFTERNOON,
    }


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"school_id": 2},
        {"class_id": 3},
        {"is_active": False},
    ],
)
def test_normalize_school_class_changes_rejects_invalid_updates(
    changes: dict[str, object],
) -> None:
    with pytest.raises(SchoolClassValidationError) as error:
        normalize_school_class_changes(changes)

    assert error.value.field == "changes"

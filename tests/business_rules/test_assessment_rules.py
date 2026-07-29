"""Tests for assessment validation and normalization rules."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from src.business_rules.assessment_rules import (
    AssessmentValidationError,
    normalize_assessment_changes,
    normalize_assessment_data,
    normalize_assessment_date_range,
    validate_assessment_not_before_birth,
)


def test_normalize_assessment_data_converts_measurements_and_notes() -> None:
    data = normalize_assessment_data(
        student_id=3,
        teacher_id=4,
        assessment_date=date(2026, 7, 20),
        weight_kg=" 32,456 ",
        height_cm=142.345,
        notes="  Primeira avaliação.  ",
    )

    assert data == {
        "student_id": 3,
        "teacher_id": 4,
        "assessment_date": date(2026, 7, 20),
        "weight_kg": Decimal("32.46"),
        "height_cm": Decimal("142.35"),
        "notes": "Primeira avaliação.",
    }


@pytest.mark.parametrize("value", [None, "", "   "])
def test_normalize_assessment_data_accepts_empty_optional_fields(
    value: str | None,
) -> None:
    data = normalize_assessment_data(
        student_id=3,
        teacher_id=4,
        assessment_date=date(2026, 7, 20),
        weight_kg=value,
        height_cm=value,
        notes=value,
    )

    assert data["weight_kg"] is None
    assert data["height_cm"] is None
    assert data["notes"] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("student_id", 0),
        ("student_id", True),
        ("teacher_id", -1),
        ("teacher_id", "4"),
    ],
)
def test_normalize_assessment_data_rejects_invalid_ids(
    field: str,
    value: object,
) -> None:
    data = {
        "student_id": 3,
        "teacher_id": 4,
        "assessment_date": date(2026, 7, 20),
    }
    data[field] = value

    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_data(**data)

    assert error.value.field == field


@pytest.mark.parametrize(
    "value",
    [
        "2026-07-20",
        datetime(2026, 7, 20, 10, 30),
        date.today() + timedelta(days=1),
    ],
)
def test_normalize_assessment_data_rejects_invalid_date(
    value: object,
) -> None:
    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_data(
            student_id=3,
            teacher_id=4,
            assessment_date=value,
        )

    assert error.value.field == "assessment_date"


@pytest.mark.parametrize(
    "value",
    [0, -1, True, "abc", "NaN", "Infinity", 1000],
)
@pytest.mark.parametrize("field", ["weight_kg", "height_cm"])
def test_normalize_assessment_data_rejects_invalid_measurements(
    field: str,
    value: object,
) -> None:
    data = {
        "student_id": 3,
        "teacher_id": 4,
        "assessment_date": date(2026, 7, 20),
        field: value,
    }

    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_data(**data)

    assert error.value.field == field


def test_normalize_assessment_data_rejects_non_text_notes() -> None:
    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_data(
            student_id=3,
            teacher_id=4,
            assessment_date=date(2026, 7, 20),
            notes=123,
        )

    assert error.value.field == "notes"


def test_normalize_assessment_changes_accepts_partial_updates() -> None:
    assert normalize_assessment_changes(
        {
            "teacher_id": 5,
            "weight_kg": "33,5",
            "height_cm": None,
            "notes": "  Evolução observada. ",
        }
    ) == {
        "teacher_id": 5,
        "weight_kg": Decimal("33.50"),
        "height_cm": None,
        "notes": "Evolução observada.",
    }


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"student_id": 2},
        {"class_id": 3},
        {"assessment_id": 4},
        {"is_active": False},
    ],
)
def test_normalize_assessment_changes_rejects_identity_updates(
    changes: dict[str, object],
) -> None:
    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_changes(changes)

    assert error.value.field == "changes"


def test_validate_assessment_not_before_birth_rejects_invalid_date() -> None:
    with pytest.raises(AssessmentValidationError) as error:
        validate_assessment_not_before_birth(
            date(2015, 5, 11),
            date(2015, 5, 12),
        )

    assert error.value.field == "assessment_date"


def test_normalize_assessment_date_range_accepts_chronological_range() -> None:
    assert normalize_assessment_date_range(
        date(2026, 6, 1),
        date(2026, 7, 20),
    ) == (date(2026, 6, 1), date(2026, 7, 20))


def test_normalize_assessment_date_range_rejects_inverted_range() -> None:
    with pytest.raises(AssessmentValidationError) as error:
        normalize_assessment_date_range(
            date(2026, 7, 20),
            date(2026, 6, 1),
        )

    assert error.value.field == "date_range"

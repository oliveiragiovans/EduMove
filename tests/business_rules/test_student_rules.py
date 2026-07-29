"""Tests for student validation and normalization rules."""

from datetime import date, datetime, timedelta

import pytest

from src.business_rules.student_rules import (
    StudentValidationError,
    normalize_birth_date,
    normalize_student_changes,
    normalize_student_data,
    normalize_student_search_name,
)
from src.models.student import StudentSex


def test_normalize_student_data_cleans_and_converts_fields() -> None:
    data = normalize_student_data(
        class_id=3,
        registration_number=" ab 123 ",
        name="  Ana   Beatriz ",
        birth_date=date(2016, 5, 12),
        sex=" feminino ",
    )

    assert data == {
        "class_id": 3,
        "registration_number": "AB 123",
        "name": "Ana Beatriz",
        "birth_date": date(2016, 5, 12),
        "sex": StudentSex.FEMALE,
    }


@pytest.mark.parametrize("value", [None, "", "   "])
def test_normalize_student_data_accepts_empty_registration_number(
    value: str | None,
) -> None:
    data = normalize_student_data(
        class_id=3,
        registration_number=value,
        name="Ana Beatriz",
        birth_date=date(2016, 5, 12),
        sex=StudentSex.FEMALE,
    )

    assert data["registration_number"] is None
    assert data["sex"] is StudentSex.FEMALE


@pytest.mark.parametrize("value", [0, -1, True, "3", None])
def test_normalize_student_data_rejects_invalid_class_id(
    value: object,
) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_data(
            class_id=value,
            name="Ana Beatriz",
            birth_date=date(2016, 5, 12),
            sex=StudentSex.FEMALE,
        )

    assert error.value.field == "class_id"


@pytest.mark.parametrize("value", ["", " " * 3, "A" * 101, None])
def test_normalize_student_data_rejects_invalid_name(value: object) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_data(
            class_id=3,
            name=value,
            birth_date=date(2016, 5, 12),
            sex=StudentSex.FEMALE,
        )

    assert error.value.field == "name"


@pytest.mark.parametrize("value", [123, "A" * 21])
def test_normalize_student_data_rejects_invalid_registration_number(
    value: object,
) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_data(
            class_id=3,
            registration_number=value,
            name="Ana Beatriz",
            birth_date=date(2016, 5, 12),
            sex=StudentSex.FEMALE,
        )

    assert error.value.field == "registration_number"


@pytest.mark.parametrize(
    "value",
    [
        "2016-05-12",
        datetime(2016, 5, 12, 10, 30),
        date.today() + timedelta(days=1),
    ],
)
def test_normalize_student_data_rejects_invalid_birth_date(
    value: object,
) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_data(
            class_id=3,
            name="Ana Beatriz",
            birth_date=value,
            sex=StudentSex.FEMALE,
        )

    assert error.value.field == "birth_date"


def test_normalize_birth_date_accepts_reference_date() -> None:
    reference_date = date(2026, 7, 29)

    assert normalize_birth_date(
        reference_date,
        today=reference_date,
    ) == reference_date


@pytest.mark.parametrize("value", ["", "Outro", None])
def test_normalize_student_data_rejects_invalid_sex(value: object) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_data(
            class_id=3,
            name="Ana Beatriz",
            birth_date=date(2016, 5, 12),
            sex=value,
        )

    assert error.value.field == "sex"


def test_normalize_student_changes_accepts_partial_updates() -> None:
    assert normalize_student_changes(
        {
            "class_id": 4,
            "registration_number": " nova-10 ",
            "name": "  Ana   Clara ",
            "sex": "MASCULINO",
        }
    ) == {
        "class_id": 4,
        "registration_number": "NOVA-10",
        "name": "Ana Clara",
        "sex": StudentSex.MALE,
    }


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"school_id": 2},
        {"student_id": 3},
        {"is_active": False},
    ],
)
def test_normalize_student_changes_rejects_invalid_updates(
    changes: dict[str, object],
) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_changes(changes)

    assert error.value.field == "changes"


@pytest.mark.parametrize("value", ["", "A" * 101, None])
def test_normalize_student_search_name_rejects_invalid_value(
    value: object,
) -> None:
    with pytest.raises(StudentValidationError) as error:
        normalize_student_search_name(value)

    assert error.value.field == "name"

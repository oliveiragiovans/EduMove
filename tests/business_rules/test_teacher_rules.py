"""Tests for teacher validation and normalization rules."""

import pytest

from src.business_rules.teacher_rules import (
    TeacherValidationError,
    normalize_teacher_changes,
    normalize_teacher_data,
)
from src.models.teacher import TeacherRole


def test_normalize_teacher_data_cleans_fields_and_uses_default_role() -> None:
    data = normalize_teacher_data(
        name="  Giovana   Oliveira ",
        email=" GIOVANA@EXEMPLO.COM ",
        password_hash=" $argon2id$hash-de-teste ",
    )

    assert data == {
        "name": "Giovana Oliveira",
        "email": "giovana@exemplo.com",
        "password_hash": "$argon2id$hash-de-teste",
        "role": TeacherRole.TEACHER,
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Administrador", TeacherRole.ADMINISTRATOR),
        (" professor ", TeacherRole.TEACHER),
        ("COORDENADOR", TeacherRole.COORDINATOR),
        (TeacherRole.TEACHER, TeacherRole.TEACHER),
    ],
)
def test_normalize_teacher_data_accepts_supported_roles(
    value: str | TeacherRole,
    expected: TeacherRole,
) -> None:
    data = normalize_teacher_data(
        name="Giovana Oliveira",
        email="giovana@exemplo.com",
        password_hash="$argon2id$hash-de-teste",
        role=value,
    )

    assert data["role"] is expected


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("email", "email-invalido"),
        ("password_hash", " "),
        ("role", "Diretor"),
    ],
)
def test_normalize_teacher_data_rejects_invalid_fields(
    field: str,
    value: str,
) -> None:
    data = {
        "name": "Giovana Oliveira",
        "email": "giovana@exemplo.com",
        "password_hash": "$argon2id$hash-de-teste",
        "role": TeacherRole.TEACHER,
    }
    data[field] = value

    with pytest.raises(TeacherValidationError) as error:
        normalize_teacher_data(**data)

    assert error.value.field == field


def test_normalize_teacher_changes_accepts_partial_updates() -> None:
    assert normalize_teacher_changes(
        {
            "name": "  Giovana   Luciano ",
            "email": " NOVO@EXEMPLO.COM ",
            "role": "Coordenador",
        }
    ) == {
        "name": "Giovana Luciano",
        "email": "novo@exemplo.com",
        "role": TeacherRole.COORDINATOR,
    }


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"school_id": 2},
        {"password_hash": "novo-hash"},
        {"is_active": False},
    ],
)
def test_normalize_teacher_changes_rejects_invalid_updates(
    changes: dict[str, object],
) -> None:
    with pytest.raises(TeacherValidationError) as error:
        normalize_teacher_changes(changes)

    assert error.value.field == "changes"

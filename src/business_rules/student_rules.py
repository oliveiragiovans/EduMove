"""Validation and normalization rules for student data."""

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from src.models.student import StudentSex


class StudentValidationError(ValueError):
    """Raised when student data violates a domain validation rule."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_EDITABLE_FIELDS = {
    "class_id",
    "registration_number",
    "name",
    "birth_date",
    "sex",
}


def _required_text(value: Any, *, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StudentValidationError(field, f"{field} é obrigatório.")

    normalized = " ".join(value.split())

    if len(normalized) > max_length:
        raise StudentValidationError(
            field,
            f"{field} deve possuir no máximo {max_length} caracteres.",
        )

    return normalized


def normalize_class_id(value: Any) -> int:
    """Return a positive school-class identifier."""

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise StudentValidationError(
            "class_id",
            "class_id deve ser um número inteiro positivo.",
        )

    return value


def normalize_registration_number(value: Any) -> str | None:
    """Return an optional normalized school registration number."""

    if value is None:
        return None

    if not isinstance(value, str):
        raise StudentValidationError(
            "registration_number",
            "registration_number deve ser um texto.",
        )

    normalized = " ".join(value.split()).upper()

    if not normalized:
        return None

    if len(normalized) > 20:
        raise StudentValidationError(
            "registration_number",
            "registration_number deve possuir no máximo 20 caracteres.",
        )

    return normalized


def normalize_student_name(value: Any) -> str:
    """Return a required student name without excess whitespace."""

    return _required_text(value, field="name", max_length=100)


def normalize_birth_date(value: Any, *, today: date | None = None) -> date:
    """Return a date of birth that is not in the future."""

    if isinstance(value, datetime) or not isinstance(value, date):
        raise StudentValidationError(
            "birth_date",
            "birth_date deve ser uma data válida.",
        )

    reference_date = today or date.today()

    if value > reference_date:
        raise StudentValidationError(
            "birth_date",
            "birth_date não pode estar no futuro.",
        )

    return value


def normalize_student_sex(value: Any) -> StudentSex:
    """Return a supported StudentSex value."""

    if isinstance(value, StudentSex):
        return value

    if not isinstance(value, str) or not value.strip():
        raise StudentValidationError("sex", "sex é obrigatório.")

    normalized = value.strip().casefold()

    for student_sex in StudentSex:
        if student_sex.value.casefold() == normalized:
            return student_sex

    supported_values = ", ".join(value.value for value in StudentSex)
    raise StudentValidationError(
        "sex",
        f"sex deve ser um dos seguintes valores: {supported_values}.",
    )


def normalize_student_search_name(value: Any) -> str:
    """Return a validated partial name used in student searches."""

    return _required_text(value, field="name", max_length=100)


def normalize_student_data(
    *,
    class_id: Any,
    registration_number: Any = None,
    name: Any,
    birth_date: Any,
    sex: Any,
) -> dict[str, int | str | date | StudentSex | None]:
    """Normalize all fields required to create a student."""

    return {
        "class_id": normalize_class_id(class_id),
        "registration_number": normalize_registration_number(
            registration_number
        ),
        "name": normalize_student_name(name),
        "birth_date": normalize_birth_date(birth_date),
        "sex": normalize_student_sex(sex),
    }


def normalize_student_changes(
    changes: Mapping[str, Any],
) -> dict[str, int | str | date | StudentSex | None]:
    """Validate a partial set of editable student fields."""

    if not changes:
        raise StudentValidationError(
            "changes",
            "ao menos um campo deve ser informado para atualização.",
        )

    unknown_fields = set(changes) - _EDITABLE_FIELDS

    if unknown_fields:
        field_list = ", ".join(sorted(unknown_fields))
        raise StudentValidationError(
            "changes",
            f"campos não permitidos para atualização: {field_list}.",
        )

    normalizers = {
        "class_id": normalize_class_id,
        "registration_number": normalize_registration_number,
        "name": normalize_student_name,
        "birth_date": normalize_birth_date,
        "sex": normalize_student_sex,
    }

    return {
        field: normalizers[field](value)
        for field, value in changes.items()
    }

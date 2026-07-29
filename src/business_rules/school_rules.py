"""Validation and normalization rules for school data."""

from collections.abc import Mapping
import re
from typing import Any


class SchoolValidationError(ValueError):
    """Raised when school data violates a domain validation rule."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_STATE_PATTERN = re.compile(r"^[A-Za-z]{2}$")
_CNPJ_ALLOWED_PATTERN = re.compile(r"^[\d./-]+$")

_EDITABLE_FIELDS = {
    "name",
    "cnpj",
    "email",
    "phone",
    "city",
    "state",
}


def _required_text(value: Any, *, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchoolValidationError(field, f"{field} é obrigatório.")

    normalized = " ".join(value.split())

    if len(normalized) > max_length:
        raise SchoolValidationError(
            field,
            f"{field} deve possuir no máximo {max_length} caracteres.",
        )

    return normalized


def _optional_text(
    value: Any,
    *,
    field: str,
    max_length: int,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise SchoolValidationError(field, f"{field} deve ser um texto.")

    normalized = " ".join(value.split())

    if not normalized:
        return None

    if len(normalized) > max_length:
        raise SchoolValidationError(
            field,
            f"{field} deve possuir no máximo {max_length} caracteres.",
        )

    return normalized


def normalize_cnpj(value: Any) -> str | None:
    """Return a CNPJ containing only its 14 digits."""

    normalized = _optional_text(value, field="cnpj", max_length=18)

    if normalized is None:
        return None

    if not _CNPJ_ALLOWED_PATTERN.fullmatch(normalized):
        raise SchoolValidationError(
            "cnpj",
            "cnpj deve conter somente números e os sinais de formatação.",
        )

    digits = re.sub(r"\D", "", normalized)

    if len(digits) != 14:
        raise SchoolValidationError("cnpj", "cnpj deve possuir 14 dígitos.")

    return digits


def normalize_email(value: Any) -> str | None:
    """Return a lowercase email address or None."""

    normalized = _optional_text(value, field="email", max_length=100)

    if normalized is None:
        return None

    normalized = normalized.lower()

    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise SchoolValidationError("email", "email possui formato inválido.")

    return normalized


def normalize_state(value: Any) -> str:
    """Return a two-letter uppercase Brazilian state code."""

    normalized = _required_text(value, field="state", max_length=2)

    if not _STATE_PATTERN.fullmatch(normalized):
        raise SchoolValidationError(
            "state",
            "state deve possuir a sigla do estado com duas letras.",
        )

    return normalized.upper()


def normalize_school_data(
    *,
    name: Any,
    city: Any,
    state: Any,
    cnpj: Any = None,
    email: Any = None,
    phone: Any = None,
) -> dict[str, str | None]:
    """Normalize all fields required to create a school."""

    return {
        "name": _required_text(name, field="name", max_length=150),
        "cnpj": normalize_cnpj(cnpj),
        "email": normalize_email(email),
        "phone": _optional_text(phone, field="phone", max_length=20),
        "city": _required_text(city, field="city", max_length=100),
        "state": normalize_state(state),
    }


def normalize_school_changes(
    changes: Mapping[str, Any],
) -> dict[str, str | None]:
    """Validate a partial set of editable school fields."""

    if not changes:
        raise SchoolValidationError(
            "changes",
            "ao menos um campo deve ser informado para atualização.",
        )

    unknown_fields = set(changes) - _EDITABLE_FIELDS

    if unknown_fields:
        field_list = ", ".join(sorted(unknown_fields))
        raise SchoolValidationError(
            "changes",
            f"campos não permitidos para atualização: {field_list}.",
        )

    normalized: dict[str, str | None] = {}

    for field, value in changes.items():
        if field == "name":
            normalized[field] = _required_text(
                value,
                field=field,
                max_length=150,
            )
        elif field == "city":
            normalized[field] = _required_text(
                value,
                field=field,
                max_length=100,
            )
        elif field == "state":
            normalized[field] = normalize_state(value)
        elif field == "cnpj":
            normalized[field] = normalize_cnpj(value)
        elif field == "email":
            normalized[field] = normalize_email(value)
        elif field == "phone":
            normalized[field] = _optional_text(
                value,
                field=field,
                max_length=20,
            )

    return normalized

"""Validation and normalization rules for teacher data."""

from collections.abc import Mapping
import re
from typing import Any

from src.models.teacher import TeacherRole


class TeacherValidationError(ValueError):
    """Raised when teacher data violates a domain validation rule."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_EDITABLE_FIELDS = {"name", "email", "role"}


def _required_text(value: Any, *, field: str, max_length: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TeacherValidationError(field, f"{field} é obrigatório.")

    normalized = " ".join(value.split())

    if len(normalized) > max_length:
        raise TeacherValidationError(
            field,
            f"{field} deve possuir no máximo {max_length} caracteres.",
        )

    return normalized


def normalize_teacher_email(value: Any) -> str:
    """Return a validated lowercase teacher email."""

    normalized = _required_text(value, field="email", max_length=100).lower()

    if not _EMAIL_PATTERN.fullmatch(normalized):
        raise TeacherValidationError("email", "email possui formato inválido.")

    return normalized


def normalize_teacher_role(value: Any) -> TeacherRole:
    """Return a supported TeacherRole from an enum or Portuguese value."""

    if isinstance(value, TeacherRole):
        return value

    if not isinstance(value, str) or not value.strip():
        raise TeacherValidationError("role", "role é obrigatório.")

    normalized = value.strip().casefold()

    for role in TeacherRole:
        if role.value.casefold() == normalized:
            return role

    supported_roles = ", ".join(role.value for role in TeacherRole)
    raise TeacherValidationError(
        "role",
        f"role deve ser um dos seguintes perfis: {supported_roles}.",
    )


def normalize_password_hash(value: Any) -> str:
    """Validate a precomputed password hash without changing its contents."""

    if not isinstance(value, str) or not value.strip():
        raise TeacherValidationError(
            "password_hash",
            "password_hash é obrigatório.",
        )

    normalized = value.strip()

    if len(normalized) > 255:
        raise TeacherValidationError(
            "password_hash",
            "password_hash deve possuir no máximo 255 caracteres.",
        )

    return normalized


def normalize_teacher_data(
    *,
    name: Any,
    email: Any,
    password_hash: Any,
    role: Any = TeacherRole.TEACHER,
) -> dict[str, str | TeacherRole]:
    """Normalize all fields required to create a teacher."""

    return {
        "name": _required_text(name, field="name", max_length=100),
        "email": normalize_teacher_email(email),
        "password_hash": normalize_password_hash(password_hash),
        "role": normalize_teacher_role(role),
    }


def normalize_teacher_changes(
    changes: Mapping[str, Any],
) -> dict[str, str | TeacherRole]:
    """Validate a partial set of editable teacher fields."""

    if not changes:
        raise TeacherValidationError(
            "changes",
            "ao menos um campo deve ser informado para atualização.",
        )

    unknown_fields = set(changes) - _EDITABLE_FIELDS

    if unknown_fields:
        field_list = ", ".join(sorted(unknown_fields))
        raise TeacherValidationError(
            "changes",
            f"campos não permitidos para atualização: {field_list}.",
        )

    normalized: dict[str, str | TeacherRole] = {}

    for field, value in changes.items():
        if field == "name":
            normalized[field] = _required_text(
                value,
                field=field,
                max_length=100,
            )
        elif field == "email":
            normalized[field] = normalize_teacher_email(value)
        elif field == "role":
            normalized[field] = normalize_teacher_role(value)

    return normalized

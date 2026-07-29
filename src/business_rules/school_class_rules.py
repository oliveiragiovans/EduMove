"""Validation and normalization rules for school-class data."""

from collections.abc import Mapping
import re
from typing import Any

from src.models.school_class import EducationLevel, SchoolShift


class SchoolClassValidationError(ValueError):
    """Raised when school-class data violates a domain validation rule."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_SECTION_PATTERN = re.compile(r"^[A-Za-z]$")
_EDITABLE_FIELDS = {
    "teacher_id",
    "grade_number",
    "education_level",
    "section",
    "academic_year",
    "shift",
}


def _bounded_integer(
    value: Any,
    *,
    field: str,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchoolClassValidationError(
            field,
            f"{field} deve ser um número inteiro.",
        )

    if not minimum <= value <= maximum:
        raise SchoolClassValidationError(
            field,
            f"{field} deve estar entre {minimum} e {maximum}.",
        )

    return value


def normalize_grade_number(value: Any) -> int:
    """Return a grade number supported by the current generic model."""

    return _bounded_integer(
        value,
        field="grade_number",
        minimum=1,
        maximum=99,
    )


def normalize_academic_year(value: Any) -> int:
    """Return a four-digit academic year in the supported project range."""

    return _bounded_integer(
        value,
        field="academic_year",
        minimum=2000,
        maximum=2100,
    )


def normalize_section(value: Any) -> str:
    """Return a one-letter uppercase class section."""

    if not isinstance(value, str):
        raise SchoolClassValidationError(
            "section",
            "section deve ser um texto.",
        )

    normalized = value.strip()

    if not _SECTION_PATTERN.fullmatch(normalized):
        raise SchoolClassValidationError(
            "section",
            "section deve possuir uma única letra.",
        )

    return normalized.upper()


def normalize_education_level(value: Any) -> EducationLevel:
    """Return a supported EducationLevel."""

    if isinstance(value, EducationLevel):
        return value

    if not isinstance(value, str) or not value.strip():
        raise SchoolClassValidationError(
            "education_level",
            "education_level é obrigatório.",
        )

    normalized = value.strip().casefold()

    for education_level in EducationLevel:
        if education_level.value.casefold() == normalized:
            return education_level

    supported_levels = ", ".join(level.value for level in EducationLevel)
    raise SchoolClassValidationError(
        "education_level",
        f"education_level deve ser um dos níveis: {supported_levels}.",
    )


def normalize_school_shift(value: Any) -> SchoolShift:
    """Return a supported SchoolShift."""

    if isinstance(value, SchoolShift):
        return value

    if not isinstance(value, str) or not value.strip():
        raise SchoolClassValidationError("shift", "shift é obrigatório.")

    normalized = value.strip().casefold()

    for shift in SchoolShift:
        if shift.value.casefold() == normalized:
            return shift

    supported_shifts = ", ".join(shift.value for shift in SchoolShift)
    raise SchoolClassValidationError(
        "shift",
        f"shift deve ser um dos turnos: {supported_shifts}.",
    )


def normalize_teacher_id(value: Any) -> int | None:
    """Return an optional positive teacher identifier."""

    if value is None:
        return None

    return _bounded_integer(
        value,
        field="teacher_id",
        minimum=1,
        maximum=2_147_483_647,
    )


def normalize_school_class_data(
    *,
    teacher_id: Any = None,
    grade_number: Any,
    education_level: Any,
    section: Any,
    academic_year: Any,
    shift: Any,
) -> dict[str, int | str | EducationLevel | SchoolShift | None]:
    """Normalize all fields required to create a school class."""

    return {
        "teacher_id": normalize_teacher_id(teacher_id),
        "grade_number": normalize_grade_number(grade_number),
        "education_level": normalize_education_level(education_level),
        "section": normalize_section(section),
        "academic_year": normalize_academic_year(academic_year),
        "shift": normalize_school_shift(shift),
    }


def normalize_school_class_changes(
    changes: Mapping[str, Any],
) -> dict[str, int | str | EducationLevel | SchoolShift | None]:
    """Validate a partial set of editable school-class fields."""

    if not changes:
        raise SchoolClassValidationError(
            "changes",
            "ao menos um campo deve ser informado para atualização.",
        )

    unknown_fields = set(changes) - _EDITABLE_FIELDS

    if unknown_fields:
        field_list = ", ".join(sorted(unknown_fields))
        raise SchoolClassValidationError(
            "changes",
            f"campos não permitidos para atualização: {field_list}.",
        )

    normalizers = {
        "teacher_id": normalize_teacher_id,
        "grade_number": normalize_grade_number,
        "education_level": normalize_education_level,
        "section": normalize_section,
        "academic_year": normalize_academic_year,
        "shift": normalize_school_shift,
    }

    return {
        field: normalizers[field](value)
        for field, value in changes.items()
    }

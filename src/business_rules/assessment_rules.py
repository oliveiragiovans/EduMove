"""Validation and normalization rules for assessment data."""

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


class AssessmentValidationError(ValueError):
    """Raised when assessment data violates a domain validation rule."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_EDITABLE_FIELDS = {
    "teacher_id",
    "assessment_date",
    "weight_kg",
    "height_cm",
    "notes",
}
_MEASUREMENT_QUANTUM = Decimal("0.01")
_MAX_MEASUREMENT = Decimal("999.99")


def normalize_assessment_id(value: Any, *, field: str) -> int:
    """Return a positive entity identifier used by an assessment."""

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AssessmentValidationError(
            field,
            f"{field} deve ser um número inteiro positivo.",
        )

    return value


def normalize_assessment_date(
    value: Any,
    *,
    today: date | None = None,
) -> date:
    """Return an assessment date that is not in the future."""

    if isinstance(value, datetime) or not isinstance(value, date):
        raise AssessmentValidationError(
            "assessment_date",
            "assessment_date deve ser uma data válida.",
        )

    if value > (today or date.today()):
        raise AssessmentValidationError(
            "assessment_date",
            "assessment_date não pode estar no futuro.",
        )

    return value


def normalize_measurement(value: Any, *, field: str) -> Decimal | None:
    """Return an optional positive measurement with two decimal places."""

    if value is None:
        return None

    if isinstance(value, bool):
        raise AssessmentValidationError(
            field,
            f"{field} deve ser um número positivo.",
        )

    candidate = value.strip().replace(",", ".") if isinstance(value, str) else value

    if candidate == "":
        return None

    try:
        normalized = Decimal(str(candidate))
    except (InvalidOperation, ValueError):
        raise AssessmentValidationError(
            field,
            f"{field} deve ser um número positivo.",
        ) from None

    if not normalized.is_finite() or normalized <= 0:
        raise AssessmentValidationError(
            field,
            f"{field} deve ser um número positivo.",
        )

    try:
        normalized = normalized.quantize(
            _MEASUREMENT_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    except InvalidOperation:
        raise AssessmentValidationError(
            field,
            f"{field} deve ser menor ou igual a {_MAX_MEASUREMENT}.",
        ) from None

    if normalized > _MAX_MEASUREMENT:
        raise AssessmentValidationError(
            field,
            f"{field} deve ser menor ou igual a {_MAX_MEASUREMENT}.",
        )

    return normalized


def normalize_notes(value: Any) -> str | None:
    """Return optional teacher notes while preserving internal formatting."""

    if value is None:
        return None

    if not isinstance(value, str):
        raise AssessmentValidationError("notes", "notes deve ser um texto.")

    normalized = value.strip()
    return normalized or None


def validate_assessment_not_before_birth(
    assessment_date: date,
    birth_date: date,
) -> None:
    """Reject an assessment dated before the student's birth."""

    if assessment_date < birth_date:
        raise AssessmentValidationError(
            "assessment_date",
            "assessment_date não pode ser anterior ao nascimento do aluno.",
        )


def normalize_assessment_data(
    *,
    student_id: Any,
    teacher_id: Any,
    assessment_date: Any,
    weight_kg: Any = None,
    height_cm: Any = None,
    notes: Any = None,
) -> dict[str, int | date | Decimal | str | None]:
    """Normalize all fields required to create an assessment."""

    return {
        "student_id": normalize_assessment_id(
            student_id,
            field="student_id",
        ),
        "teacher_id": normalize_assessment_id(
            teacher_id,
            field="teacher_id",
        ),
        "assessment_date": normalize_assessment_date(assessment_date),
        "weight_kg": normalize_measurement(weight_kg, field="weight_kg"),
        "height_cm": normalize_measurement(height_cm, field="height_cm"),
        "notes": normalize_notes(notes),
    }


def normalize_assessment_changes(
    changes: Mapping[str, Any],
) -> dict[str, int | date | Decimal | str | None]:
    """Validate a partial set of editable assessment fields."""

    if not changes:
        raise AssessmentValidationError(
            "changes",
            "ao menos um campo deve ser informado para atualização.",
        )

    unknown_fields = set(changes) - _EDITABLE_FIELDS

    if unknown_fields:
        field_list = ", ".join(sorted(unknown_fields))
        raise AssessmentValidationError(
            "changes",
            f"campos não permitidos para atualização: {field_list}.",
        )

    normalizers = {
        "teacher_id": lambda value: normalize_assessment_id(
            value,
            field="teacher_id",
        ),
        "assessment_date": normalize_assessment_date,
        "weight_kg": lambda value: normalize_measurement(
            value,
            field="weight_kg",
        ),
        "height_cm": lambda value: normalize_measurement(
            value,
            field="height_cm",
        ),
        "notes": normalize_notes,
    }

    return {
        field: normalizers[field](value)
        for field, value in changes.items()
    }


def normalize_assessment_date_range(
    date_from: Any = None,
    date_to: Any = None,
) -> tuple[date | None, date | None]:
    """Return an optional chronological date range for assessment queries."""

    normalized_from = (
        normalize_assessment_date(date_from)
        if date_from is not None
        else None
    )
    normalized_to = (
        normalize_assessment_date(date_to)
        if date_to is not None
        else None
    )

    if (
        normalized_from is not None
        and normalized_to is not None
        and normalized_from > normalized_to
    ):
        raise AssessmentValidationError(
            "date_range",
            "date_from não pode ser posterior a date_to.",
        )

    return normalized_from, normalized_to

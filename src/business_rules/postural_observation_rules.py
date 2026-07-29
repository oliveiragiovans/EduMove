"""Validation rules for educational postural observations."""

from enum import Enum
from typing import Any, TypeVar

from src.models.postural_observation import PosturalRegion, PosturalView


class PosturalObservationValidationError(ValueError):
    """Raised when a postural-observation value is invalid."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


EnumType = TypeVar("EnumType", bound=Enum)


def normalize_postural_entity_id(value: Any, *, field: str) -> int:
    """Return a positive identifier used by posture workflows."""

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise PosturalObservationValidationError(
            field,
            f"{field} deve ser um número inteiro positivo.",
        )

    return value


def normalize_postural_notes(value: Any) -> str | None:
    """Normalize the optional pedagogical note saved with one choice."""

    if value is None:
        return None

    if not isinstance(value, str):
        raise PosturalObservationValidationError(
            "notes",
            "notes deve ser um texto.",
        )

    normalized = value.strip()

    if len(normalized) > 255:
        raise PosturalObservationValidationError(
            "notes",
            "notes deve possuir no máximo 255 caracteres.",
        )

    return normalized or None


def normalize_postural_region(value: Any) -> PosturalRegion | None:
    """Normalize an optional body-region filter."""

    return _normalize_optional_enum(
        value,
        enum_type=PosturalRegion,
        field="region",
        message="region deve ser shoulders, spine, knees ou feet.",
    )


def normalize_postural_view(value: Any) -> PosturalView | None:
    """Normalize an optional viewing-position filter."""

    return _normalize_optional_enum(
        value,
        enum_type=PosturalView,
        field="view_position",
        message="view_position deve ser frontal, lateral ou reference.",
    )


def _normalize_optional_enum(
    value: Any,
    *,
    enum_type: type[EnumType],
    field: str,
    message: str,
) -> EnumType | None:
    if value is None:
        return None

    if isinstance(value, enum_type):
        return value

    if isinstance(value, str):
        try:
            return enum_type(value.strip().casefold())
        except ValueError:
            pass

    raise PosturalObservationValidationError(field, message)

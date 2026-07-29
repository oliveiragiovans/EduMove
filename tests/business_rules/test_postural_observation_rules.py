"""Tests for postural-observation validation rules."""

import pytest

from src.business_rules.postural_observation_rules import (
    PosturalObservationValidationError,
    normalize_postural_entity_id,
    normalize_postural_notes,
    normalize_postural_region,
    normalize_postural_view,
)
from src.models.postural_observation import PosturalRegion, PosturalView


@pytest.mark.parametrize("value", [0, -1, True, "1", None])
def test_postural_entity_id_requires_positive_integer(value: object) -> None:
    with pytest.raises(
        PosturalObservationValidationError,
        match="número inteiro positivo",
    ) as error:
        normalize_postural_entity_id(value, field="assessment_id")

    assert error.value.field == "assessment_id"


def test_postural_notes_are_trimmed_and_blank_becomes_none() -> None:
    assert normalize_postural_notes("  observação pedagógica  ") == (
        "observação pedagógica"
    )
    assert normalize_postural_notes("   ") is None
    assert normalize_postural_notes(None) is None


def test_postural_notes_validate_type_and_maximum_length() -> None:
    with pytest.raises(PosturalObservationValidationError) as type_error:
        normalize_postural_notes(12)

    assert type_error.value.field == "notes"

    with pytest.raises(PosturalObservationValidationError, match="255"):
        normalize_postural_notes("a" * 256)


def test_region_accepts_enum_and_normalized_string() -> None:
    assert normalize_postural_region(PosturalRegion.KNEES) is (
        PosturalRegion.KNEES
    )
    assert normalize_postural_region("  FEET ") is PosturalRegion.FEET
    assert normalize_postural_region(None) is None


def test_view_accepts_enum_and_normalized_string() -> None:
    assert normalize_postural_view(PosturalView.FRONTAL) is (
        PosturalView.FRONTAL
    )
    assert normalize_postural_view(" LATERAL ") is PosturalView.LATERAL
    assert normalize_postural_view(None) is None


@pytest.mark.parametrize(
    ("normalizer", "value", "field"),
    [
        (normalize_postural_region, "cabeça", "region"),
        (normalize_postural_view, "posterior", "view_position"),
        (normalize_postural_region, 1, "region"),
        (normalize_postural_view, False, "view_position"),
    ],
)
def test_invalid_catalog_filters_are_rejected(
    normalizer: object,
    value: object,
    field: str,
) -> None:
    with pytest.raises(PosturalObservationValidationError) as error:
        normalizer(value)  # type: ignore[operator]

    assert error.value.field == field

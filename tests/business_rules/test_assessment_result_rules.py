"""Tests for motor-test attempt validation and aggregation rules."""

from decimal import Decimal

import pytest

from src.business_rules.assessment_result_rules import (
    AssessmentResultValidationError,
    aggregate_attempt_values,
    normalize_attempt_notes,
    normalize_attempt_values,
    normalize_result_entity_id,
    normalize_result_value,
)
from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultType,
)


def make_motor_test(
    *,
    code: str = "HORIZONTAL_JUMP",
    name: str = "Salto horizontal",
    result_type: ResultType = ResultType.MEASUREMENT,
    aggregation_method: AggregationMethod = AggregationMethod.MAXIMUM,
    min_attempts: int = 2,
    max_attempts: int = 2,
) -> MotorTest:
    return MotorTest(
        code=code,
        name=name,
        unit="cm",
        result_type=result_type,
        aggregation_method=aggregation_method,
        default_attempts=min_attempts,
        min_attempts=min_attempts,
        max_attempts=max_attempts,
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("120,456", Decimal("120.46")),
        (120.454, Decimal("120.45")),
        (0, Decimal("0.00")),
    ],
)
def test_normalize_measurement_value(
    value: object,
    expected: Decimal,
) -> None:
    assert normalize_result_value(value, make_motor_test()) == expected


@pytest.mark.parametrize("value", [-1, True, "", "abc", "NaN", "Infinity"])
def test_normalize_measurement_value_rejects_invalid_input(
    value: object,
) -> None:
    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_result_value(value, make_motor_test())

    assert error.value.field == "result_value"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, Decimal("1.00")),
        (False, Decimal("0.00")),
        ("acerto", Decimal("1.00")),
        ("ERRO", Decimal("0.00")),
        ("sim", Decimal("1.00")),
        ("não", Decimal("0.00")),
        (1, Decimal("1.00")),
        (0, Decimal("0.00")),
    ],
)
def test_normalize_binary_value(
    value: object,
    expected: Decimal,
) -> None:
    motor_test = make_motor_test(
        code="BALL_RECEPTION",
        name="Recepção de bola",
        result_type=ResultType.BINARY,
        aggregation_method=AggregationMethod.SUM,
        min_attempts=3,
        max_attempts=10,
    )

    assert normalize_result_value(value, motor_test) == expected


@pytest.mark.parametrize("value", [2, -1, "talvez", 0.5, None])
def test_normalize_binary_value_rejects_invalid_input(value: object) -> None:
    motor_test = make_motor_test(
        result_type=ResultType.BINARY,
        min_attempts=3,
        max_attempts=10,
    )

    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_result_value(value, motor_test)

    assert error.value.field == "result_value"


def test_normalize_attempt_values_requires_fixed_protocol_count() -> None:
    motor_test = make_motor_test()

    assert normalize_attempt_values(
        ["120,5", "125,0"],
        motor_test,
    ) == [Decimal("120.50"), Decimal("125.00")]

    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_attempt_values(["120,5"], motor_test)

    assert error.value.field == "values"


@pytest.mark.parametrize("attempt_count", [3, 5, 10])
def test_normalize_attempt_values_accepts_configurable_count(
    attempt_count: int,
) -> None:
    motor_test = make_motor_test(
        result_type=ResultType.BINARY,
        min_attempts=3,
        max_attempts=10,
    )

    assert len(
        normalize_attempt_values([True] * attempt_count, motor_test)
    ) == attempt_count


@pytest.mark.parametrize("attempt_count", [2, 11])
def test_normalize_attempt_values_rejects_out_of_range_count(
    attempt_count: int,
) -> None:
    motor_test = make_motor_test(
        result_type=ResultType.BINARY,
        min_attempts=3,
        max_attempts=10,
    )

    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_attempt_values([True] * attempt_count, motor_test)

    assert error.value.field == "values"


def test_single_leg_balance_is_limited_to_thirty_seconds() -> None:
    motor_test = make_motor_test(
        code="SINGLE_LEG_BALANCE",
        name="Equilíbrio unipodal",
    )

    assert normalize_result_value("30", motor_test) == Decimal("30.00")

    with pytest.raises(AssessmentResultValidationError):
        normalize_result_value("30,01", motor_test)


def test_normalize_attempt_notes_matches_attempt_count() -> None:
    assert normalize_attempt_notes(
        ["  primeira ", ""],
        attempt_count=2,
    ) == ["primeira", None]
    assert normalize_attempt_notes(None, attempt_count=2) == [None, None]


@pytest.mark.parametrize(
    "notes",
    [
        ["somente uma"],
        "observação",
        [123, None],
        ["A" * 256, None],
    ],
)
def test_normalize_attempt_notes_rejects_invalid_notes(
    notes: object,
) -> None:
    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_attempt_notes(notes, attempt_count=2)

    assert error.value.field == "notes"


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        (AggregationMethod.MAXIMUM, Decimal("12.00")),
        (AggregationMethod.MINIMUM, Decimal("8.00")),
        (AggregationMethod.SUM, Decimal("30.00")),
        (AggregationMethod.AVERAGE, Decimal("10.00")),
    ],
)
def test_aggregate_attempt_values_uses_configured_method(
    method: AggregationMethod,
    expected: Decimal,
) -> None:
    assert aggregate_attempt_values(
        [Decimal("10.00"), Decimal("12.00"), Decimal("8.00")],
        method,
    ) == expected


@pytest.mark.parametrize("value", [0, -1, True, "1", None])
def test_normalize_result_entity_id_rejects_invalid_value(
    value: object,
) -> None:
    with pytest.raises(AssessmentResultValidationError) as error:
        normalize_result_entity_id(value, field="assessment_id")

    assert error.value.field == "assessment_id"

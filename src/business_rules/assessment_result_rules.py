"""Validation and aggregation rules for motor-test attempts."""

from collections.abc import Sequence
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultType,
)


class AssessmentResultValidationError(ValueError):
    """Raised when motor-test attempts violate their configured protocol."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(message)


_RESULT_QUANTUM = Decimal("0.01")
_MAX_RESULT_VALUE = Decimal("99999999.99")
_BINARY_TRUE_VALUES = {"1", "true", "sim", "acerto"}
_BINARY_FALSE_VALUES = {"0", "false", "não", "nao", "erro"}
_PROTOCOL_MAX_VALUES = {
    "SINGLE_LEG_BALANCE": Decimal("30.00"),
}


def normalize_result_entity_id(value: Any, *, field: str) -> int:
    """Return a positive identifier used by result-management operations."""

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise AssessmentResultValidationError(
            field,
            f"{field} deve ser um número inteiro positivo.",
        )

    return value


def normalize_result_value(value: Any, motor_test: MotorTest) -> Decimal:
    """Return one attempt value compatible with the motor-test protocol."""

    if motor_test.result_type is ResultType.BINARY:
        return _normalize_binary_value(value)

    return _normalize_measurement_value(value, motor_test)


def _normalize_binary_value(value: Any) -> Decimal:
    if isinstance(value, bool):
        return Decimal("1.00") if value else Decimal("0.00")

    if isinstance(value, str):
        normalized = value.strip().casefold()

        if normalized in _BINARY_TRUE_VALUES:
            return Decimal("1.00")

        if normalized in _BINARY_FALSE_VALUES:
            return Decimal("0.00")

    if isinstance(value, (int, Decimal)) and not isinstance(value, bool):
        if value == 1:
            return Decimal("1.00")

        if value == 0:
            return Decimal("0.00")

    raise AssessmentResultValidationError(
        "result_value",
        "testes binários aceitam apenas acerto ou erro.",
    )


def _normalize_measurement_value(
    value: Any,
    motor_test: MotorTest,
) -> Decimal:
    if isinstance(value, bool):
        raise AssessmentResultValidationError(
            "result_value",
            "result_value deve ser um número maior ou igual a zero.",
        )

    candidate = value.strip().replace(",", ".") if isinstance(value, str) else value

    if candidate == "":
        raise AssessmentResultValidationError(
            "result_value",
            "result_value é obrigatório.",
        )

    try:
        normalized = Decimal(str(candidate))
    except (InvalidOperation, ValueError):
        raise AssessmentResultValidationError(
            "result_value",
            "result_value deve ser um número maior ou igual a zero.",
        ) from None

    if not normalized.is_finite() or normalized < 0:
        raise AssessmentResultValidationError(
            "result_value",
            "result_value deve ser um número maior ou igual a zero.",
        )

    try:
        normalized = normalized.quantize(
            _RESULT_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
    except InvalidOperation:
        raise AssessmentResultValidationError(
            "result_value",
            f"result_value deve ser menor ou igual a {_MAX_RESULT_VALUE}.",
        ) from None

    if normalized > _MAX_RESULT_VALUE:
        raise AssessmentResultValidationError(
            "result_value",
            f"result_value deve ser menor ou igual a {_MAX_RESULT_VALUE}.",
        )

    protocol_maximum = _PROTOCOL_MAX_VALUES.get(motor_test.code)

    if protocol_maximum is not None and normalized > protocol_maximum:
        raise AssessmentResultValidationError(
            "result_value",
            f"{motor_test.name} aceita no máximo {protocol_maximum} {motor_test.unit}.",
        )

    return normalized


def normalize_attempt_values(
    values: Any,
    motor_test: MotorTest,
) -> list[Decimal]:
    """Validate the complete attempt set selected for one motor test."""

    if (
        not isinstance(values, Sequence)
        or isinstance(values, (str, bytes))
    ):
        raise AssessmentResultValidationError(
            "values",
            "values deve ser uma sequência de tentativas.",
        )

    attempt_count = len(values)

    if not motor_test.min_attempts <= attempt_count <= motor_test.max_attempts:
        if motor_test.min_attempts == motor_test.max_attempts:
            message = (
                f"{motor_test.name} exige exatamente "
                f"{motor_test.min_attempts} tentativas."
            )
        else:
            message = (
                f"{motor_test.name} exige entre {motor_test.min_attempts} "
                f"e {motor_test.max_attempts} tentativas."
            )

        raise AssessmentResultValidationError("values", message)

    return [
        normalize_result_value(value, motor_test)
        for value in values
    ]


def normalize_attempt_notes(
    notes: Any,
    *,
    attempt_count: int,
) -> list[str | None]:
    """Return one optional note for every submitted attempt."""

    if notes is None:
        return [None] * attempt_count

    if (
        not isinstance(notes, Sequence)
        or isinstance(notes, (str, bytes))
        or len(notes) != attempt_count
    ):
        raise AssessmentResultValidationError(
            "notes",
            "notes deve possuir uma posição para cada tentativa.",
        )

    normalized_notes: list[str | None] = []

    for value in notes:
        if value is None:
            normalized_notes.append(None)
            continue

        if not isinstance(value, str):
            raise AssessmentResultValidationError(
                "notes",
                "cada observação deve ser um texto.",
            )

        normalized = value.strip()

        if len(normalized) > 255:
            raise AssessmentResultValidationError(
                "notes",
                "cada observação deve possuir no máximo 255 caracteres.",
            )

        normalized_notes.append(normalized or None)

    return normalized_notes


def aggregate_attempt_values(
    values: Sequence[Decimal],
    method: AggregationMethod,
) -> Decimal:
    """Aggregate a non-empty normalized attempt set."""

    if not values:
        raise AssessmentResultValidationError(
            "values",
            "ao menos uma tentativa é necessária para calcular o resultado.",
        )

    if method is AggregationMethod.MAXIMUM:
        return max(values)

    if method is AggregationMethod.MINIMUM:
        return min(values)

    if method is AggregationMethod.SUM:
        return sum(values, start=Decimal("0.00"))

    if method is AggregationMethod.AVERAGE:
        return (
            sum(values, start=Decimal("0.00")) / Decimal(len(values))
        ).quantize(_RESULT_QUANTUM, rounding=ROUND_HALF_UP)

    raise AssessmentResultValidationError(
        "aggregation_method",
        "método de agregação não suportado.",
    )

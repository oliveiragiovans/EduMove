"""Application workflows for motor-test attempts and summaries."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.business_rules.assessment_result_rules import (
    aggregate_attempt_values,
    normalize_attempt_notes,
    normalize_attempt_values,
    normalize_result_entity_id,
)
from src.models.assessment import Assessment
from src.models.assessment_result import AssessmentResult
from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultType,
)
from src.models.school import School
from src.models.school_class import SchoolClass
from src.services.exceptions import EntityNotFoundError


@dataclass(frozen=True)
class AssessmentResultSummary:
    """Aggregated display data for one motor test in one assessment."""

    assessment_id: int
    motor_test_id: int
    code: str
    name: str
    unit: str
    result_type: ResultType
    aggregation_method: AggregationMethod
    attempt_count: int
    aggregate_value: Decimal

    @property
    def display_value(self) -> str:
        """Return a concise value suitable for the future interface."""

        if self.result_type is ResultType.BINARY:
            return f"{int(self.aggregate_value)}/{self.attempt_count} acertos"

        formatted_value = format(self.aggregate_value, "f").rstrip("0").rstrip(".")
        return f"{formatted_value} {self.unit}"


class AssessmentResultService:
    """Manage complete motor-test attempt sets within one school."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_test_results(
        self,
        *,
        school_id: int,
        assessment_id: int,
        motor_test_id: int,
        values: Any,
        notes: Any = None,
    ) -> list[AssessmentResult]:
        """Create or replace the active attempt set for one motor test."""

        self._get_active_school(school_id)
        normalized_assessment_id = normalize_result_entity_id(
            assessment_id,
            field="assessment_id",
        )
        normalized_motor_test_id = normalize_result_entity_id(
            motor_test_id,
            field="motor_test_id",
        )
        self._get_assessment(
            school_id,
            normalized_assessment_id,
            require_active=True,
        )
        motor_test = self._get_motor_test(
            normalized_motor_test_id,
            require_active=True,
        )
        normalized_values = normalize_attempt_values(values, motor_test)
        normalized_notes = normalize_attempt_notes(
            notes,
            attempt_count=len(normalized_values),
        )
        existing_results = list(
            self.session.scalars(
                select(AssessmentResult)
                .where(
                    AssessmentResult.assessment_id
                    == normalized_assessment_id,
                    AssessmentResult.motor_test_id
                    == normalized_motor_test_id,
                )
                .order_by(AssessmentResult.attempt_number)
            )
        )
        results_by_attempt = {
            result.attempt_number: result
            for result in existing_results
        }
        saved_results: list[AssessmentResult] = []

        for attempt_number, (value, note) in enumerate(
            zip(normalized_values, normalized_notes, strict=True),
            start=1,
        ):
            result = results_by_attempt.get(attempt_number)

            if result is None:
                result = AssessmentResult(
                    assessment_id=normalized_assessment_id,
                    motor_test_id=normalized_motor_test_id,
                    attempt_number=attempt_number,
                    result_value=value,
                    notes=note,
                )
                self.session.add(result)
            else:
                result.result_value = value
                result.notes = note
                result.is_active = True

            saved_results.append(result)

        selected_attempts = len(normalized_values)

        for result in existing_results:
            if result.attempt_number > selected_attempts:
                result.is_active = False

        self.session.flush()
        return saved_results

    def get_test_results(
        self,
        school_id: int,
        assessment_id: int,
        motor_test_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[AssessmentResult]:
        """Return attempts for one test, including historical assessments."""

        self._get_active_school(school_id)
        normalized_assessment_id = normalize_result_entity_id(
            assessment_id,
            field="assessment_id",
        )
        normalized_motor_test_id = normalize_result_entity_id(
            motor_test_id,
            field="motor_test_id",
        )
        self._get_assessment(
            school_id,
            normalized_assessment_id,
            require_active=False,
        )
        self._get_motor_test(
            normalized_motor_test_id,
            require_active=False,
        )
        statement = select(AssessmentResult).where(
            AssessmentResult.assessment_id == normalized_assessment_id,
            AssessmentResult.motor_test_id == normalized_motor_test_id,
        )

        if not include_inactive:
            statement = statement.where(
                AssessmentResult.is_active.is_(True)
            )

        statement = statement.order_by(AssessmentResult.attempt_number)
        return list(self.session.scalars(statement))

    def summarize_test_results(
        self,
        school_id: int,
        assessment_id: int,
        motor_test_id: int,
    ) -> AssessmentResultSummary:
        """Aggregate the active attempts according to the test protocol."""

        motor_test = self._get_motor_test(
            normalize_result_entity_id(
                motor_test_id,
                field="motor_test_id",
            ),
            require_active=False,
        )
        results = self.get_test_results(
            school_id,
            assessment_id,
            motor_test_id,
        )

        if not results:
            raise EntityNotFoundError(
                "Nenhuma tentativa ativa encontrada para o teste."
            )

        normalized_values = normalize_attempt_values(
            [result.result_value for result in results],
            motor_test,
        )
        aggregate_value = aggregate_attempt_values(
            normalized_values,
            motor_test.aggregation_method,
        )
        return AssessmentResultSummary(
            assessment_id=assessment_id,
            motor_test_id=motor_test.motor_test_id,
            code=motor_test.code,
            name=motor_test.name,
            unit=motor_test.unit,
            result_type=motor_test.result_type,
            aggregation_method=motor_test.aggregation_method,
            attempt_count=len(normalized_values),
            aggregate_value=aggregate_value,
        )

    def list_assessment_summaries(
        self,
        school_id: int,
        assessment_id: int,
    ) -> list[AssessmentResultSummary]:
        """Return one protocol summary for every test recorded."""

        self._get_active_school(school_id)
        normalized_assessment_id = normalize_result_entity_id(
            assessment_id,
            field="assessment_id",
        )
        self._get_assessment(
            school_id,
            normalized_assessment_id,
            require_active=False,
        )
        motor_test_ids = list(
            self.session.scalars(
                select(AssessmentResult.motor_test_id)
                .where(
                    AssessmentResult.assessment_id
                    == normalized_assessment_id,
                    AssessmentResult.is_active.is_(True),
                )
                .distinct()
                .order_by(AssessmentResult.motor_test_id)
            )
        )
        return [
            self.summarize_test_results(
                school_id,
                normalized_assessment_id,
                motor_test_id,
            )
            for motor_test_id in motor_test_ids
        ]

    def deactivate_test_results(
        self,
        school_id: int,
        assessment_id: int,
        motor_test_id: int,
    ) -> list[AssessmentResult]:
        """Deactivate every attempt for one test without deleting history."""

        self._get_active_school(school_id)
        normalized_assessment_id = normalize_result_entity_id(
            assessment_id,
            field="assessment_id",
        )
        normalized_motor_test_id = normalize_result_entity_id(
            motor_test_id,
            field="motor_test_id",
        )
        self._get_assessment(
            school_id,
            normalized_assessment_id,
            require_active=True,
        )
        self._get_motor_test(
            normalized_motor_test_id,
            require_active=False,
        )
        results = self.get_test_results(
            school_id,
            normalized_assessment_id,
            normalized_motor_test_id,
        )

        if not results:
            raise EntityNotFoundError(
                "Nenhuma tentativa ativa encontrada para o teste."
            )

        for result in results:
            result.is_active = False

        self.session.flush()
        return results

    def _get_active_school(self, school_id: int) -> School:
        school = self.session.scalar(
            select(School).where(
                School.school_id == school_id,
                School.is_active.is_(True),
            )
        )

        if school is None:
            raise EntityNotFoundError("Escola não encontrada ou inativa.")

        return school

    def _get_assessment(
        self,
        school_id: int,
        assessment_id: int,
        *,
        require_active: bool,
    ) -> Assessment:
        statement = (
            select(Assessment)
            .join(
                SchoolClass,
                Assessment.class_id == SchoolClass.class_id,
            )
            .where(
                Assessment.assessment_id == assessment_id,
                SchoolClass.school_id == school_id,
            )
        )

        if require_active:
            statement = statement.where(Assessment.is_active.is_(True))

        assessment = self.session.scalar(statement)

        if assessment is None:
            raise EntityNotFoundError(
                "Avaliação não encontrada na escola ou inativa."
            )

        return assessment

    def _get_motor_test(
        self,
        motor_test_id: int,
        *,
        require_active: bool,
    ) -> MotorTest:
        statement = select(MotorTest).where(
            MotorTest.motor_test_id == motor_test_id
        )

        if require_active:
            statement = statement.where(MotorTest.is_active.is_(True))

        motor_test = self.session.scalar(statement)

        if motor_test is None:
            raise EntityNotFoundError("Teste motor não encontrado ou inativo.")

        return motor_test

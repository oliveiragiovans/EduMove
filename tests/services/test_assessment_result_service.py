"""Integration tests for AssessmentResultService."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.business_rules.assessment_result_rules import (
    AssessmentResultValidationError,
)
from src.models.assessment import Assessment
from src.models.assessment_result import AssessmentResult
from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultDirection,
    ResultType,
)
from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher, TeacherRole
from src.services.assessment_result_service import AssessmentResultService
from src.services.exceptions import EntityNotFoundError


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)
    SchoolClass.__table__.create(engine)
    Student.__table__.create(engine)
    Assessment.__table__.create(engine)
    MotorTest.__table__.create(engine)
    AssessmentResult.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> AssessmentResultService:
    return AssessmentResultService(session)


def create_context(
    session: Session,
    *,
    school_name: str = "Escola Movimento",
) -> tuple[School, Assessment]:
    school = School(
        name=school_name,
        city="São Paulo",
        state="SP",
    )
    session.add(school)
    session.flush()
    teacher = Teacher(
        school_id=school.school_id,
        name="Professora Avaliadora",
        email=f"{school.school_id}@exemplo.com",
        password_hash="$argon2id$hash-de-teste",
        role=TeacherRole.TEACHER,
    )
    session.add(teacher)
    session.flush()
    school_class = SchoolClass(
        school_id=school.school_id,
        teacher_id=teacher.teacher_id,
        grade_number=5,
        education_level=EducationLevel.ELEMENTARY_I,
        section="A",
        academic_year=2026,
        shift=SchoolShift.MORNING,
    )
    session.add(school_class)
    session.flush()
    student = Student(
        class_id=school_class.class_id,
        registration_number=f"MAT-{school.school_id}",
        name="Ana Beatriz",
        birth_date=date(2016, 5, 12),
        sex=StudentSex.FEMALE,
    )
    session.add(student)
    session.flush()
    assessment = Assessment(
        student_id=student.student_id,
        teacher_id=teacher.teacher_id,
        class_id=school_class.class_id,
        assessment_date=date(2026, 7, 20),
    )
    session.add(assessment)
    session.flush()
    return school, assessment


def create_motor_test(
    session: Session,
    *,
    code: str = "HORIZONTAL_JUMP",
    name: str = "Salto horizontal",
    unit: str = "cm",
    result_type: ResultType = ResultType.MEASUREMENT,
    aggregation_method: AggregationMethod = AggregationMethod.MAXIMUM,
    min_attempts: int = 2,
    max_attempts: int = 2,
    is_active: bool = True,
) -> MotorTest:
    motor_test = MotorTest(
        code=code,
        name=name,
        unit=unit,
        result_direction=ResultDirection.HIGHER,
        result_type=result_type,
        aggregation_method=aggregation_method,
        default_attempts=min_attempts,
        min_attempts=min_attempts,
        max_attempts=max_attempts,
        is_active=is_active,
    )
    session.add(motor_test)
    session.flush()
    return motor_test


def test_save_test_results_creates_sequential_measurement_attempts(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(session)

    results = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=["120,5", 125.456],
        notes=["  primeira ", None],
    )

    assert [result.attempt_number for result in results] == [1, 2]
    assert [result.result_value for result in results] == [
        Decimal("120.50"),
        Decimal("125.46"),
    ]
    assert [result.notes for result in results] == ["primeira", None]
    assert all(result.is_active is True for result in results)


def test_binary_summary_preserves_successes_and_total_attempts(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(
        session,
        code="BALL_RECEPTION",
        name="Recepção de bola",
        unit="acertos",
        result_type=ResultType.BINARY,
        aggregation_method=AggregationMethod.SUM,
        min_attempts=3,
        max_attempts=10,
    )
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=["acerto", "erro", True, False, "acerto"],
    )

    summary = service.summarize_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    )

    assert summary.aggregate_value == Decimal("3.00")
    assert summary.attempt_count == 5
    assert summary.display_value == "3/5 acertos"


def test_save_test_results_updates_reactivates_and_deactivates_attempts(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(
        session,
        code="BALL_RECEPTION",
        result_type=ResultType.BINARY,
        aggregation_method=AggregationMethod.SUM,
        min_attempts=3,
        max_attempts=10,
    )
    original = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[True, True, False, False, True],
    )
    original_ids = [result.assessment_result_id for result in original]

    shortened = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[False, True, True],
    )
    all_results = service.get_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
        include_inactive=True,
    )

    assert [result.assessment_result_id for result in shortened] == original_ids[:3]
    assert [result.is_active for result in all_results] == [
        True,
        True,
        True,
        False,
        False,
    ]

    restored = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[True, True, True, True, False],
    )

    assert [result.assessment_result_id for result in restored] == original_ids
    assert all(result.is_active is True for result in restored)


def test_save_test_results_enforces_protocol_attempt_count(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(session)

    with pytest.raises(AssessmentResultValidationError):
        service.save_test_results(
            school_id=school.school_id,
            assessment_id=assessment.assessment_id,
            motor_test_id=motor_test.motor_test_id,
            values=[120],
        )

    assert service.get_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    ) == []


def test_save_test_results_requires_active_assessment_and_motor_test(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    inactive_test = create_motor_test(session, is_active=False)

    with pytest.raises(EntityNotFoundError):
        service.save_test_results(
            school_id=school.school_id,
            assessment_id=assessment.assessment_id,
            motor_test_id=inactive_test.motor_test_id,
            values=[120, 125],
        )

    active_test = create_motor_test(
        session,
        code="SECOND_TEST",
        name="Segundo teste",
    )
    assessment.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.save_test_results(
            school_id=school.school_id,
            assessment_id=assessment.assessment_id,
            motor_test_id=active_test.motor_test_id,
            values=[120, 125],
        )


def test_result_operations_are_scoped_by_school(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    other_school, _ = create_context(
        session,
        school_name="Escola Dois",
    )
    motor_test = create_motor_test(session)

    with pytest.raises(EntityNotFoundError):
        service.save_test_results(
            school_id=other_school.school_id,
            assessment_id=assessment.assessment_id,
            motor_test_id=motor_test.motor_test_id,
            values=[120, 125],
        )


@pytest.mark.parametrize(
    ("method", "expected"),
    [
        (AggregationMethod.MAXIMUM, Decimal("12.00")),
        (AggregationMethod.MINIMUM, Decimal("8.00")),
        (AggregationMethod.AVERAGE, Decimal("10.00")),
    ],
)
def test_summary_uses_configured_measurement_aggregation(
    service: AssessmentResultService,
    session: Session,
    method: AggregationMethod,
    expected: Decimal,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(
        session,
        aggregation_method=method,
        min_attempts=3,
        max_attempts=3,
    )
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[10, 12, 8],
    )

    summary = service.summarize_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    )

    assert summary.aggregate_value == expected
    assert summary.display_value == f"{int(expected)} cm"


def test_list_assessment_summaries_returns_each_recorded_test(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    jump = create_motor_test(session)
    balance = create_motor_test(
        session,
        code="SINGLE_LEG_BALANCE",
        name="Equilíbrio unipodal",
        unit="s",
    )
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=jump.motor_test_id,
        values=[120, 125],
    )
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=balance.motor_test_id,
        values=[20, 25],
    )

    summaries = service.list_assessment_summaries(
        school.school_id,
        assessment.assessment_id,
    )

    assert [summary.code for summary in summaries] == [
        "HORIZONTAL_JUMP",
        "SINGLE_LEG_BALANCE",
    ]


def test_deactivate_test_results_preserves_and_can_reactivate_attempts(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(session)
    original = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[120, 125],
    )

    deactivated = service.deactivate_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    )

    assert deactivated == original
    assert all(result.is_active is False for result in deactivated)

    with pytest.raises(EntityNotFoundError):
        service.summarize_test_results(
            school.school_id,
            assessment.assessment_id,
            motor_test.motor_test_id,
        )

    restored = service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[130, 135],
    )

    assert restored == original
    assert all(result.is_active is True for result in restored)


def test_result_history_survives_assessment_and_test_deactivation(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(session)
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[120, 125],
    )
    assessment.is_active = False
    motor_test.is_active = False
    session.flush()

    results = service.get_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    )
    summary = service.summarize_test_results(
        school.school_id,
        assessment.assessment_id,
        motor_test.motor_test_id,
    )

    assert len(results) == 2
    assert summary.aggregate_value == Decimal("125.00")


def test_result_queries_require_active_school(
    service: AssessmentResultService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    motor_test = create_motor_test(session)
    service.save_test_results(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        motor_test_id=motor_test.motor_test_id,
        values=[120, 125],
    )
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.get_test_results(
            school.school_id,
            assessment.assessment_id,
            motor_test.motor_test_id,
        )

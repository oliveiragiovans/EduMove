"""Integration tests for AssessmentService."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.business_rules.assessment_rules import AssessmentValidationError
from src.models.assessment import Assessment
from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher, TeacherRole
from src.services.assessment_service import AssessmentService
from src.services.exceptions import EntityNotFoundError


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)
    SchoolClass.__table__.create(engine)
    Student.__table__.create(engine)
    Assessment.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> AssessmentService:
    return AssessmentService(session)


def create_school(
    session: Session,
    *,
    name: str = "Escola Movimento",
    is_active: bool = True,
) -> School:
    school = School(
        name=name,
        city="São Paulo",
        state="SP",
        is_active=is_active,
    )
    session.add(school)
    session.flush()
    return school


def create_teacher(
    session: Session,
    school: School,
    *,
    email: str = "professora@exemplo.com",
    is_active: bool = True,
) -> Teacher:
    teacher = Teacher(
        school_id=school.school_id,
        name="Professora Avaliadora",
        email=email,
        password_hash="$argon2id$hash-de-teste",
        role=TeacherRole.TEACHER,
        is_active=is_active,
    )
    session.add(teacher)
    session.flush()
    return teacher


def create_school_class(
    session: Session,
    school: School,
    *,
    section: str = "A",
    is_active: bool = True,
) -> SchoolClass:
    school_class = SchoolClass(
        school_id=school.school_id,
        grade_number=5,
        education_level=EducationLevel.ELEMENTARY_I,
        section=section,
        academic_year=2026,
        shift=SchoolShift.MORNING,
        is_active=is_active,
    )
    session.add(school_class)
    session.flush()
    return school_class


def create_student(
    session: Session,
    school_class: SchoolClass,
    *,
    registration_number: str = "MAT-001",
    birth_date: date = date(2016, 5, 12),
    is_active: bool = True,
) -> Student:
    student = Student(
        class_id=school_class.class_id,
        registration_number=registration_number,
        name="Ana Beatriz",
        birth_date=birth_date,
        sex=StudentSex.FEMALE,
        is_active=is_active,
    )
    session.add(student)
    session.flush()
    return student


def create_assessment(
    service: AssessmentService,
    school: School,
    student: Student,
    teacher: Teacher,
    *,
    assessment_date: date = date(2026, 7, 20),
    weight_kg: object = "32,5",
    height_cm: object = "142,0",
    notes: object = "Avaliação inicial.",
) -> Assessment:
    return service.create_assessment(
        school_id=school.school_id,
        student_id=student.student_id,
        teacher_id=teacher.teacher_id,
        assessment_date=assessment_date,
        weight_kg=weight_kg,
        height_cm=height_cm,
        notes=notes,
    )


def create_complete_context(
    session: Session,
) -> tuple[School, SchoolClass, Student, Teacher]:
    school = create_school(session)
    school_class = create_school_class(session, school)
    student = create_student(session, school_class)
    teacher = create_teacher(session, school)
    return school, school_class, student, teacher


def test_create_assessment_uses_student_class_and_normalizes_data(
    service: AssessmentService,
    session: Session,
) -> None:
    school, school_class, student, teacher = create_complete_context(session)

    assessment = create_assessment(
        service,
        school,
        student,
        teacher,
        weight_kg=" 32,456 ",
        height_cm=142.345,
        notes="  Avaliação inicial.  ",
    )

    assert assessment.assessment_id is not None
    assert assessment.student_id == student.student_id
    assert assessment.teacher_id == teacher.teacher_id
    assert assessment.class_id == school_class.class_id
    assert assessment.weight_kg == Decimal("32.46")
    assert assessment.height_cm == Decimal("142.35")
    assert assessment.notes == "Avaliação inicial."
    assert assessment.bmi == Decimal("16.02")
    assert assessment.is_active is True


def test_create_assessment_allows_optional_measurements(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)

    assessment = create_assessment(
        service,
        school,
        student,
        teacher,
        weight_kg=None,
        height_cm=None,
        notes=None,
    )

    assert assessment.weight_kg is None
    assert assessment.height_cm is None
    assert assessment.notes is None
    assert assessment.bmi is None


def test_create_assessment_requires_active_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        create_assessment(service, school, student, teacher)


@pytest.mark.parametrize(
    ("student_is_active", "class_is_active"),
    [(False, True), (True, False)],
)
def test_create_assessment_requires_active_student_and_class(
    service: AssessmentService,
    session: Session,
    student_is_active: bool,
    class_is_active: bool,
) -> None:
    school = create_school(session)
    school_class = create_school_class(
        session,
        school,
        is_active=class_is_active,
    )
    student = create_student(
        session,
        school_class,
        is_active=student_is_active,
    )
    teacher = create_teacher(session, school)

    with pytest.raises(EntityNotFoundError):
        create_assessment(service, school, student, teacher)


def test_create_assessment_rejects_student_from_another_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school = create_school(session, name="Escola Um")
    teacher = create_teacher(session, school)
    other_school = create_school(session, name="Escola Dois")
    other_class = create_school_class(session, other_school)
    student = create_student(session, other_class)

    with pytest.raises(EntityNotFoundError):
        create_assessment(service, school, student, teacher)


@pytest.mark.parametrize("teacher_is_active", [True, False])
def test_create_assessment_rejects_teacher_outside_active_school_scope(
    service: AssessmentService,
    session: Session,
    teacher_is_active: bool,
) -> None:
    school = create_school(session, name="Escola Um")
    school_class = create_school_class(session, school)
    student = create_student(session, school_class)
    teacher_school = (
        create_school(session, name="Escola Dois")
        if teacher_is_active
        else school
    )
    teacher = create_teacher(
        session,
        teacher_school,
        is_active=teacher_is_active,
    )

    with pytest.raises(EntityNotFoundError):
        create_assessment(service, school, student, teacher)


def test_create_assessment_rejects_date_before_student_birth(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)

    with pytest.raises(AssessmentValidationError):
        create_assessment(
            service,
            school,
            student,
            teacher,
            assessment_date=date(2016, 5, 11),
        )


def test_get_assessment_is_scoped_by_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)
    other_school = create_school(session, name="Escola Dois")

    with pytest.raises(EntityNotFoundError):
        service.get_assessment(
            other_school.school_id,
            assessment.assessment_id,
        )

    assert service.get_assessment(
        school.school_id,
        assessment.assessment_id,
    ) is assessment


def test_list_assessments_orders_by_most_recent_and_hides_inactive(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    older = create_assessment(
        service,
        school,
        student,
        teacher,
        assessment_date=date(2026, 6, 10),
    )
    recent = create_assessment(
        service,
        school,
        student,
        teacher,
        assessment_date=date(2026, 7, 20),
    )
    older.is_active = False
    session.flush()

    assert service.list_assessments(school.school_id) == [recent]
    assert service.list_assessments(
        school.school_id,
        include_inactive=True,
    ) == [recent, older]


def test_list_assessments_applies_entity_and_date_filters(
    service: AssessmentService,
    session: Session,
) -> None:
    school, school_class, student, teacher = create_complete_context(session)
    expected = create_assessment(
        service,
        school,
        student,
        teacher,
        assessment_date=date(2026, 7, 20),
    )
    create_assessment(
        service,
        school,
        student,
        teacher,
        assessment_date=date(2026, 6, 10),
    )

    assert service.list_assessments(
        school.school_id,
        student_id=student.student_id,
        teacher_id=teacher.teacher_id,
        class_id=school_class.class_id,
        date_from=date(2026, 7, 1),
        date_to=date(2026, 7, 29),
    ) == [expected]


def test_list_assessments_rejects_entity_filter_from_another_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school = create_school(session, name="Escola Um")
    other_school = create_school(session, name="Escola Dois")
    other_teacher = create_teacher(
        session,
        other_school,
        email="outra.escola@exemplo.com",
    )

    with pytest.raises(EntityNotFoundError):
        service.list_assessments(
            school.school_id,
            teacher_id=other_teacher.teacher_id,
        )


def test_update_assessment_changes_editable_fields(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    second_teacher = create_teacher(
        session,
        school,
        email="segunda@exemplo.com",
    )
    assessment = create_assessment(service, school, student, teacher)

    updated = service.update_assessment(
        school.school_id,
        assessment.assessment_id,
        teacher_id=second_teacher.teacher_id,
        assessment_date=date(2026, 7, 21),
        weight_kg="33,25",
        height_cm=None,
        notes="  Medida revisada. ",
    )

    assert updated is assessment
    assert updated.teacher_id == second_teacher.teacher_id
    assert updated.assessment_date == date(2026, 7, 21)
    assert updated.weight_kg == Decimal("33.25")
    assert updated.height_cm is None
    assert updated.notes == "Medida revisada."


def test_update_assessment_rejects_teacher_from_another_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)
    other_school = create_school(session, name="Escola Dois")
    other_teacher = create_teacher(
        session,
        other_school,
        email="outra.escola@exemplo.com",
    )

    with pytest.raises(EntityNotFoundError):
        service.update_assessment(
            school.school_id,
            assessment.assessment_id,
            teacher_id=other_teacher.teacher_id,
        )


def test_update_assessment_rejects_date_before_student_birth(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)

    with pytest.raises(AssessmentValidationError):
        service.update_assessment(
            school.school_id,
            assessment.assessment_id,
            assessment_date=date(2016, 5, 11),
        )


def test_update_assessment_rejects_identity_changes(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)

    with pytest.raises(AssessmentValidationError):
        service.update_assessment(
            school.school_id,
            assessment.assessment_id,
            student_id=999,
        )


def test_deactivate_assessment_preserves_record(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)

    deactivated = service.deactivate_assessment(
        school.school_id,
        assessment.assessment_id,
    )

    assert deactivated.is_active is False

    with pytest.raises(EntityNotFoundError):
        service.get_assessment(
            school.school_id,
            assessment.assessment_id,
        )

    assert service.get_assessment(
        school.school_id,
        assessment.assessment_id,
        include_inactive=True,
    ) is assessment
    assert session.scalar(
        select(Assessment).where(
            Assessment.assessment_id == assessment.assessment_id
        )
    ) is assessment


def test_assessment_history_survives_related_record_deactivation(
    service: AssessmentService,
    session: Session,
) -> None:
    school, school_class, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)
    student.is_active = False
    teacher.is_active = False
    school_class.is_active = False
    session.flush()

    assert service.get_assessment(
        school.school_id,
        assessment.assessment_id,
    ) is assessment
    assert service.list_assessments(
        school.school_id,
        student_id=student.student_id,
    ) == [assessment]


def test_assessment_queries_require_active_school(
    service: AssessmentService,
    session: Session,
) -> None:
    school, _, student, teacher = create_complete_context(session)
    assessment = create_assessment(service, school, student, teacher)
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.get_assessment(
            school.school_id,
            assessment.assessment_id,
        )

    with pytest.raises(EntityNotFoundError):
        service.list_assessments(school.school_id)

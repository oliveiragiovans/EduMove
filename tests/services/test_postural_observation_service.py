"""Integration tests for PosturalObservationService."""

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models.assessment import Assessment
from src.models.postural_observation import (
    AssessmentPosturalObservation,
    PosturalObservationOption,
    PosturalRegion,
    PosturalView,
)
from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher, TeacherRole
from src.services.exceptions import EntityNotFoundError
from src.services.postural_observation_service import (
    PosturalObservationService,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)
    SchoolClass.__table__.create(engine)
    Student.__table__.create(engine)
    Assessment.__table__.create(engine)
    PosturalObservationOption.__table__.create(engine)
    AssessmentPosturalObservation.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> PosturalObservationService:
    return PosturalObservationService(session)


def create_context(
    session: Session,
    *,
    school_name: str = "Escola Movimento",
) -> tuple[School, Assessment]:
    school = School(name=school_name, city="São Paulo", state="SP")
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


def create_option(
    session: Session,
    *,
    code: str,
    region: PosturalRegion = PosturalRegion.SHOULDERS,
    view: PosturalView = PosturalView.FRONTAL,
    label: str = "Opção postural",
    image_path: str = "assets/posture/shoulders-reference.png",
    sort_order: int = 1,
    is_active: bool = True,
) -> PosturalObservationOption:
    option = PosturalObservationOption(
        code=code,
        region=region,
        view_position=view,
        label=label,
        reference_image_path=image_path,
        sort_order=sort_order,
        is_active=is_active,
    )
    session.add(option)
    session.flush()
    return option


def test_list_options_filters_catalog_and_omits_inactive(
    service: PosturalObservationService,
    session: Session,
) -> None:
    active = create_option(
        session,
        code="SHOULDERS_FRONTAL_SYMMETRICAL",
        sort_order=2,
    )
    first = create_option(
        session,
        code="SHOULDERS_FRONTAL_LEFT_ELEVATED",
        sort_order=1,
    )
    create_option(
        session,
        code="KNEES_FRONTAL_NEUTRAL",
        region=PosturalRegion.KNEES,
    )
    create_option(
        session,
        code="SHOULDERS_FRONTAL_INACTIVE",
        is_active=False,
    )

    options = service.list_options(region="shoulders", view_position="frontal")

    assert options == [first, active]


def test_save_observation_creates_choice_with_normalized_note(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    option = create_option(session, code="SHOULDERS_FRONTAL_SYMMETRICAL")

    observation = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=option.postural_option_id,
        notes="  acompanhar nas próximas avaliações  ",
    )

    assert observation.notes == "acompanhar nas próximas avaliações"
    assert observation.is_active is True


def test_new_choice_replaces_only_same_region_and_view(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    symmetrical = create_option(
        session,
        code="SHOULDERS_FRONTAL_SYMMETRICAL",
    )
    elevated = create_option(
        session,
        code="SHOULDERS_FRONTAL_LEFT_ELEVATED",
        sort_order=2,
    )
    lateral = create_option(
        session,
        code="SHOULDERS_LATERAL_NEUTRAL",
        view=PosturalView.LATERAL,
    )
    old_choice = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=symmetrical.postural_option_id,
    )
    lateral_choice = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=lateral.postural_option_id,
    )

    new_choice = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=elevated.postural_option_id,
    )

    assert old_choice.is_active is False
    assert new_choice.is_active is True
    assert lateral_choice.is_active is True
    assert service.get_assessment_observations(
        school.school_id,
        assessment.assessment_id,
    ) == [new_choice, lateral_choice]


def test_previous_choice_is_reactivated_instead_of_duplicated(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    first = create_option(session, code="FIRST")
    second = create_option(session, code="SECOND", sort_order=2)
    original = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=first.postural_option_id,
    )
    service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=second.postural_option_id,
    )

    restored = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=first.postural_option_id,
        notes="reavaliado",
    )

    assert restored.postural_observation_id == original.postural_observation_id
    assert restored.notes == "reavaliado"
    assert len(
        service.get_assessment_observations(
            school.school_id,
            assessment.assessment_id,
            include_inactive=True,
        )
    ) == 2


def test_summary_includes_approved_reference_image(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    option = create_option(
        session,
        code="FEET_REFERENCE_LOW_ARCH",
        region=PosturalRegion.FEET,
        view=PosturalView.REFERENCE,
        label="Pegada com arco rebaixado",
        image_path="assets/posture/feet-footprints-reference.png",
    )
    service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=option.postural_option_id,
    )

    summaries = service.list_observation_summaries(
        school.school_id,
        assessment.assessment_id,
    )

    assert len(summaries) == 1
    assert summaries[0].label == "Pegada com arco rebaixado"
    assert summaries[0].reference_image_path == (
        "assets/posture/feet-footprints-reference.png"
    )


def test_inactive_assessment_and_option_cannot_receive_choice(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    option = create_option(session, code="INACTIVE", is_active=False)

    with pytest.raises(EntityNotFoundError, match="Opção"):
        service.save_observation(
            school_id=school.school_id,
            assessment_id=assessment.assessment_id,
            postural_option_id=option.postural_option_id,
        )

    option.is_active = True
    assessment.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError, match="Avaliação"):
        service.save_observation(
            school_id=school.school_id,
            assessment_id=assessment.assessment_id,
            postural_option_id=option.postural_option_id,
        )


def test_historical_assessment_can_still_be_read(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    option = create_option(session, code="HISTORICAL")
    observation = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=option.postural_option_id,
    )
    assessment.is_active = False
    session.flush()

    assert service.get_assessment_observations(
        school.school_id,
        assessment.assessment_id,
    ) == [observation]


def test_assessment_cannot_be_accessed_from_another_school(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    other_school, _ = create_context(session, school_name="Outra escola")
    option = create_option(session, code="SCHOOL_SCOPE")

    with pytest.raises(EntityNotFoundError, match="Avaliação"):
        service.save_observation(
            school_id=other_school.school_id,
            assessment_id=assessment.assessment_id,
            postural_option_id=option.postural_option_id,
        )

    assert school.school_id != other_school.school_id


def test_deactivate_preserves_history_and_choice_can_be_restored(
    service: PosturalObservationService,
    session: Session,
) -> None:
    school, assessment = create_context(session)
    option = create_option(session, code="DEACTIVATE")
    observation = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=option.postural_option_id,
    )

    deactivated = service.deactivate_observation(
        school.school_id,
        assessment.assessment_id,
        observation.postural_observation_id,
    )

    assert deactivated.is_active is False
    assert service.get_assessment_observations(
        school.school_id,
        assessment.assessment_id,
    ) == []
    assert service.get_assessment_observations(
        school.school_id,
        assessment.assessment_id,
        include_inactive=True,
    ) == [observation]

    restored = service.save_observation(
        school_id=school.school_id,
        assessment_id=assessment.assessment_id,
        postural_option_id=option.postural_option_id,
    )
    assert restored.postural_observation_id == observation.postural_observation_id
    assert restored.is_active is True

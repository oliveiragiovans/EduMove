"""Integration tests for StudentService."""

from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher
from src.services.exceptions import ConflictError, EntityNotFoundError
from src.services.student_service import StudentService


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)
    SchoolClass.__table__.create(engine)
    Student.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> StudentService:
    return StudentService(session)


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
    service: StudentService,
    school: School,
    school_class: SchoolClass,
    *,
    registration_number: str | None = "MAT-001",
    name: str = "Ana Beatriz",
    birth_date: date = date(2016, 5, 12),
    sex: StudentSex | str = StudentSex.FEMALE,
) -> Student:
    return service.create_student(
        school_id=school.school_id,
        class_id=school_class.class_id,
        registration_number=registration_number,
        name=name,
        birth_date=birth_date,
        sex=sex,
    )


def test_create_student_normalizes_and_persists_data(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)

    student = service.create_student(
        school_id=school.school_id,
        class_id=school_class.class_id,
        registration_number=" ab 123 ",
        name="  Ana   Beatriz ",
        birth_date=date(2016, 5, 12),
        sex=" feminino ",
    )

    assert student.student_id is not None
    assert student.class_id == school_class.class_id
    assert student.registration_number == "AB 123"
    assert student.name == "Ana Beatriz"
    assert student.birth_date == date(2016, 5, 12)
    assert student.sex is StudentSex.FEMALE
    assert student.is_active is True


def test_create_student_allows_no_registration_number(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)

    student = create_student(
        service,
        school,
        school_class,
        registration_number=None,
    )

    assert student.registration_number is None


def test_create_student_requires_active_school(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session, is_active=False)
    school_class = create_school_class(session, school)

    with pytest.raises(EntityNotFoundError):
        create_student(service, school, school_class)


@pytest.mark.parametrize("class_is_active", [True, False])
def test_create_student_rejects_class_outside_active_school_scope(
    service: StudentService,
    session: Session,
    class_is_active: bool,
) -> None:
    school = create_school(session, name="Escola Um")
    class_school = (
        create_school(session, name="Escola Dois")
        if class_is_active
        else school
    )
    school_class = create_school_class(
        session,
        class_school,
        is_active=class_is_active,
    )

    with pytest.raises(EntityNotFoundError):
        create_student(service, school, school_class)


def test_create_student_rejects_duplicate_registration_number(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    create_student(service, school, school_class)
    session.commit()

    with pytest.raises(ConflictError):
        create_student(
            service,
            school,
            school_class,
            name="Outra Aluna",
        )


def test_get_student_is_scoped_by_school(
    service: StudentService,
    session: Session,
) -> None:
    first_school = create_school(session, name="Escola Um")
    second_school = create_school(session, name="Escola Dois")
    first_class = create_school_class(session, first_school)
    student = create_student(service, first_school, first_class)

    with pytest.raises(EntityNotFoundError):
        service.get_student(second_school.school_id, student.student_id)

    assert service.get_student(
        first_school.school_id,
        student.student_id,
    ) is student


def test_list_students_returns_active_records_ordered_by_name(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    second = create_student(
        service,
        school,
        school_class,
        registration_number="MAT-002",
        name="Bruno Lima",
        sex=StudentSex.MALE,
    )
    first = create_student(
        service,
        school,
        school_class,
        registration_number="MAT-001",
        name="Ana Beatriz",
    )
    second.is_active = False
    session.flush()

    assert service.list_students(school.school_id) == [first]
    assert service.list_students(
        school.school_id,
        include_inactive=True,
    ) == [first, second]


def test_list_students_filters_by_class_and_partial_name(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    first_class = create_school_class(session, school, section="A")
    second_class = create_school_class(session, school, section="B")
    ana = create_student(
        service,
        school,
        first_class,
        registration_number="MAT-001",
        name="Ana Beatriz",
    )
    create_student(
        service,
        school,
        first_class,
        registration_number="MAT-002",
        name="Bruno Lima",
        sex=StudentSex.MALE,
    )
    create_student(
        service,
        school,
        second_class,
        registration_number="MAT-003",
        name="Ana Clara",
    )

    assert service.list_students(
        school.school_id,
        class_id=first_class.class_id,
        name="Ana",
    ) == [ana]


def test_list_students_rejects_class_from_another_school(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session, name="Escola Um")
    other_school = create_school(session, name="Escola Dois")
    other_class = create_school_class(session, other_school)

    with pytest.raises(EntityNotFoundError):
        service.list_students(
            school.school_id,
            class_id=other_class.class_id,
        )


def test_update_student_changes_registration_data(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    student = create_student(service, school, school_class)

    updated = service.update_student(
        school.school_id,
        student.student_id,
        registration_number=" nova-10 ",
        name="  Ana   Clara ",
        birth_date=date(2015, 4, 20),
        sex="Masculino",
    )

    assert updated is student
    assert updated.registration_number == "NOVA-10"
    assert updated.name == "Ana Clara"
    assert updated.birth_date == date(2015, 4, 20)
    assert updated.sex is StudentSex.MALE


def test_update_student_transfers_to_active_class_in_same_school(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    first_class = create_school_class(session, school, section="A")
    second_class = create_school_class(session, school, section="B")
    student = create_student(service, school, first_class)

    service.update_student(
        school.school_id,
        student.student_id,
        class_id=second_class.class_id,
    )

    assert student.class_id == second_class.class_id


@pytest.mark.parametrize("class_is_active", [True, False])
def test_update_student_rejects_class_outside_active_school_scope(
    service: StudentService,
    session: Session,
    class_is_active: bool,
) -> None:
    school = create_school(session, name="Escola Um")
    first_class = create_school_class(session, school, section="A")
    student = create_student(service, school, first_class)
    target_school = (
        create_school(session, name="Escola Dois")
        if class_is_active
        else school
    )
    target_class = create_school_class(
        session,
        target_school,
        section="B",
        is_active=class_is_active,
    )

    with pytest.raises(EntityNotFoundError):
        service.update_student(
            school.school_id,
            student.student_id,
            class_id=target_class.class_id,
        )


def test_update_student_rejects_duplicate_registration_number(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    create_student(
        service,
        school,
        school_class,
        registration_number="MAT-001",
    )
    student = create_student(
        service,
        school,
        school_class,
        registration_number="MAT-002",
        name="Bruno Lima",
        sex=StudentSex.MALE,
    )
    session.commit()

    with pytest.raises(ConflictError):
        service.update_student(
            school.school_id,
            student.student_id,
            registration_number="MAT-001",
        )


def test_deactivate_student_preserves_record(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    student = create_student(service, school, school_class)

    deactivated = service.deactivate_student(
        school.school_id,
        student.student_id,
    )

    assert deactivated.is_active is False

    with pytest.raises(EntityNotFoundError):
        service.get_student(school.school_id, student.student_id)

    assert service.get_student(
        school.school_id,
        student.student_id,
        include_inactive=True,
    ) is student
    assert session.scalar(
        select(Student).where(Student.student_id == student.student_id)
    ) is student


def test_student_queries_preserve_access_when_class_is_inactive(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    student = create_student(service, school, school_class)
    school_class.is_active = False
    session.flush()

    assert service.get_student(
        school.school_id,
        student.student_id,
    ) is student
    assert service.list_students(
        school.school_id,
        class_id=school_class.class_id,
    ) == [student]


def test_student_queries_require_active_school(
    service: StudentService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(session, school)
    student = create_student(service, school, school_class)
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.get_student(school.school_id, student.student_id)

    with pytest.raises(EntityNotFoundError):
        service.list_students(school.school_id)

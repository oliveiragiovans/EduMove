"""Integration tests for SchoolClassService."""

from datetime import date

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher, TeacherRole
from src.services.exceptions import ConflictError, EntityNotFoundError
from src.services.school_class_service import SchoolClassService


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
def service(session: Session) -> SchoolClassService:
    return SchoolClassService(session)


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
        name="Professora Responsável",
        email=email,
        password_hash="$argon2id$hash-de-teste",
        role=TeacherRole.TEACHER,
        is_active=is_active,
    )
    session.add(teacher)
    session.flush()
    return teacher


def create_school_class(
    service: SchoolClassService,
    school: School,
    *,
    teacher_id: int | None = None,
    grade_number: int = 5,
    education_level: EducationLevel | str = EducationLevel.ELEMENTARY_I,
    section: str = "A",
    academic_year: int = 2026,
    shift: SchoolShift | str = SchoolShift.MORNING,
) -> SchoolClass:
    return service.create_school_class(
        school_id=school.school_id,
        teacher_id=teacher_id,
        grade_number=grade_number,
        education_level=education_level,
        section=section,
        academic_year=academic_year,
        shift=shift,
    )


def test_create_school_class_normalizes_and_persists_data(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(session, school)

    school_class = create_school_class(
        service,
        school,
        teacher_id=teacher.teacher_id,
        education_level=" ensino fundamental i ",
        section=" b ",
        shift=" manhã ",
    )

    assert school_class.class_id is not None
    assert school_class.school_id == school.school_id
    assert school_class.teacher_id == teacher.teacher_id
    assert school_class.education_level is EducationLevel.ELEMENTARY_I
    assert school_class.section == "B"
    assert school_class.shift is SchoolShift.MORNING
    assert school_class.is_active is True


def test_create_school_class_allows_no_responsible_teacher(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)

    school_class = create_school_class(service, school)

    assert school_class.teacher_id is None


def test_create_school_class_requires_active_school(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session, is_active=False)

    with pytest.raises(EntityNotFoundError):
        create_school_class(service, school)


@pytest.mark.parametrize("teacher_is_active", [True, False])
def test_create_school_class_rejects_teacher_outside_active_school_scope(
    service: SchoolClassService,
    session: Session,
    teacher_is_active: bool,
) -> None:
    school = create_school(session, name="Escola Um")
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
        create_school_class(
            service,
            school,
            teacher_id=teacher.teacher_id,
        )


def test_create_school_class_rejects_duplicate_identity(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    create_school_class(service, school)
    session.commit()

    with pytest.raises(ConflictError):
        create_school_class(service, school)


def test_get_school_class_is_scoped_by_school(
    service: SchoolClassService,
    session: Session,
) -> None:
    first_school = create_school(session, name="Escola Um")
    second_school = create_school(session, name="Escola Dois")
    school_class = create_school_class(service, first_school)

    with pytest.raises(EntityNotFoundError):
        service.get_school_class(
            second_school.school_id,
            school_class.class_id,
        )

    assert service.get_school_class(
        first_school.school_id,
        school_class.class_id,
    ) is school_class


def test_list_school_classes_returns_active_records_in_academic_order(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    older = create_school_class(
        service,
        school,
        section="B",
        academic_year=2025,
    )
    later_section = create_school_class(
        service,
        school,
        section="B",
    )
    first = create_school_class(
        service,
        school,
        section="A",
    )
    older.is_active = False
    session.flush()

    assert service.list_school_classes(school.school_id) == [
        first,
        later_section,
    ]
    assert service.list_school_classes(
        school.school_id,
        include_inactive=True,
    ) == [first, later_section, older]


def test_update_school_class_changes_fields_and_assigns_teacher(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(session, school)
    school_class = create_school_class(service, school)

    updated = service.update_school_class(
        school.school_id,
        school_class.class_id,
        teacher_id=teacher.teacher_id,
        grade_number=6,
        education_level="Ensino Fundamental II",
        section=" c ",
        academic_year=2027,
        shift="Tarde",
    )

    assert updated is school_class
    assert updated.teacher_id == teacher.teacher_id
    assert updated.grade_number == 6
    assert updated.education_level is EducationLevel.ELEMENTARY_II
    assert updated.section == "C"
    assert updated.academic_year == 2027
    assert updated.shift is SchoolShift.AFTERNOON


def test_update_school_class_can_remove_responsible_teacher(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(session, school)
    school_class = create_school_class(
        service,
        school,
        teacher_id=teacher.teacher_id,
    )

    service.update_school_class(
        school.school_id,
        school_class.class_id,
        teacher_id=None,
    )

    assert school_class.teacher_id is None


def test_update_school_class_rejects_duplicate_identity(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    create_school_class(service, school, section="A")
    school_class = create_school_class(service, school, section="B")
    session.commit()

    with pytest.raises(ConflictError):
        service.update_school_class(
            school.school_id,
            school_class.class_id,
            section="A",
        )


def test_deactivate_school_class_preserves_record(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(service, school)

    deactivated = service.deactivate_school_class(
        school.school_id,
        school_class.class_id,
    )

    assert deactivated.is_active is False

    with pytest.raises(EntityNotFoundError):
        service.get_school_class(
            school.school_id,
            school_class.class_id,
        )

    assert service.get_school_class(
        school.school_id,
        school_class.class_id,
        include_inactive=True,
    ) is school_class
    assert session.scalar(
        select(SchoolClass).where(
            SchoolClass.class_id == school_class.class_id
        )
    ) is school_class


def test_deactivate_school_class_rejects_active_students(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(service, school)
    student = Student(
        class_id=school_class.class_id,
        registration_number="MAT-001",
        name="Ana Beatriz",
        birth_date=date(2016, 5, 12),
        sex=StudentSex.FEMALE,
    )
    session.add(student)
    session.flush()

    with pytest.raises(ConflictError):
        service.deactivate_school_class(
            school.school_id,
            school_class.class_id,
        )

    assert school_class.is_active is True


def test_school_class_queries_require_active_school(
    service: SchoolClassService,
    session: Session,
) -> None:
    school = create_school(session)
    school_class = create_school_class(service, school)
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.get_school_class(
            school.school_id,
            school_class.class_id,
        )

    with pytest.raises(EntityNotFoundError):
        service.list_school_classes(school.school_id)

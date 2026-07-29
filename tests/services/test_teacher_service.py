"""Integration tests for TeacherService."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.business_rules.teacher_rules import TeacherValidationError
from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.security.passwords import verify_password
from src.services.exceptions import (
    AuthenticationError,
    ConflictError,
    EntityNotFoundError,
)
from src.services.teacher_service import TeacherService


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> TeacherService:
    return TeacherService(session)


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
    service: TeacherService,
    school: School,
    *,
    name: str = "Giovana Oliveira",
    email: str = "giovana@exemplo.com",
    role: TeacherRole | str = TeacherRole.TEACHER,
) -> Teacher:
    return service.create_teacher(
        school_id=school.school_id,
        name=name,
        email=email,
        password="senha pedagógica segura",
        role=role,
    )


def test_create_teacher_normalizes_and_persists_data(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)

    teacher = service.create_teacher(
        school_id=school.school_id,
        name="  Giovana   Oliveira ",
        email=" GIOVANA@EXEMPLO.COM ",
        password="minha senha pedagógica",
    )

    assert teacher.teacher_id is not None
    assert teacher.school_id == school.school_id
    assert teacher.name == "Giovana Oliveira"
    assert teacher.email == "giovana@exemplo.com"
    assert teacher.password_hash != "minha senha pedagógica"
    assert teacher.password_hash.startswith("$argon2id$")
    assert verify_password(
        teacher.password_hash,
        "minha senha pedagógica",
    )
    assert teacher.role is TeacherRole.TEACHER
    assert teacher.is_active is True


def test_create_teacher_requires_active_school(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session, is_active=False)

    with pytest.raises(EntityNotFoundError):
        create_teacher(service, school)


def test_create_teacher_rejects_duplicate_email(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    create_teacher(service, school)
    session.commit()

    with pytest.raises(ConflictError):
        create_teacher(
            service,
            school,
            name="Outra Professora",
        )


def test_school_allows_only_one_active_administrator(
    service: TeacherService,
    session: Session,
) -> None:
    first_school = create_school(session, name="Escola Um")
    second_school = create_school(session, name="Escola Dois")
    create_teacher(
        service,
        first_school,
        role=TeacherRole.ADMINISTRATOR,
    )

    with pytest.raises(ConflictError):
        create_teacher(
            service,
            first_school,
            name="Segunda Administradora",
            email="admin2@exemplo.com",
            role=TeacherRole.ADMINISTRATOR,
        )

    other_administrator = create_teacher(
        service,
        second_school,
        name="Administradora da Escola Dois",
        email="admin.escola2@exemplo.com",
        role=TeacherRole.ADMINISTRATOR,
    )

    assert other_administrator.school_id == second_school.school_id


def test_get_teacher_is_scoped_by_school(
    service: TeacherService,
    session: Session,
) -> None:
    first_school = create_school(session, name="Escola Um")
    second_school = create_school(session, name="Escola Dois")
    teacher = create_teacher(service, first_school)

    with pytest.raises(EntityNotFoundError):
        service.get_teacher(second_school.school_id, teacher.teacher_id)

    assert (
        service.get_teacher(first_school.school_id, teacher.teacher_id)
        is teacher
    )


def test_get_teacher_requires_active_school(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)
    school.is_active = False
    session.flush()

    with pytest.raises(EntityNotFoundError):
        service.get_teacher(school.school_id, teacher.teacher_id)


def test_list_teachers_returns_active_records_ordered_by_name(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    second = create_teacher(
        service,
        school,
        name="Professora Beta",
        email="beta@exemplo.com",
    )
    first = create_teacher(
        service,
        school,
        name="Professora Alfa",
        email="alfa@exemplo.com",
    )
    second.is_active = False
    session.flush()

    assert service.list_teachers(school.school_id) == [first]
    assert service.list_teachers(
        school.school_id,
        include_inactive=True,
    ) == [first, second]


def test_update_teacher_changes_only_editable_fields(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)

    updated = service.update_teacher(
        school.school_id,
        teacher.teacher_id,
        name="Giovana Luciano",
        email=" NOVO@EXEMPLO.COM ",
        role="Coordenador",
    )

    assert updated is teacher
    assert updated.name == "Giovana Luciano"
    assert updated.email == "novo@exemplo.com"
    assert updated.role is TeacherRole.COORDINATOR
    assert updated.school_id == school.school_id
    assert verify_password(
        updated.password_hash,
        "senha pedagógica segura",
    )


def test_update_teacher_cannot_create_second_administrator(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    create_teacher(
        service,
        school,
        email="admin@exemplo.com",
        role=TeacherRole.ADMINISTRATOR,
    )
    teacher = create_teacher(
        service,
        school,
        name="Professora",
        email="professora@exemplo.com",
    )

    with pytest.raises(ConflictError):
        service.update_teacher(
            school.school_id,
            teacher.teacher_id,
            role=TeacherRole.ADMINISTRATOR,
        )


def test_update_teacher_rejects_credential_changes(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)

    with pytest.raises(TeacherValidationError):
        service.update_teacher(
            school.school_id,
            teacher.teacher_id,
            password_hash="novo-hash",
        )


def test_change_password_requires_current_password_and_replaces_hash(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)
    original_hash = teacher.password_hash

    changed = service.change_password(
        school.school_id,
        teacher.teacher_id,
        current_password="senha pedagógica segura",
        new_password="uma nova senha pedagógica",
    )

    assert changed is teacher
    assert changed.password_hash != original_hash
    assert not verify_password(
        changed.password_hash,
        "senha pedagógica segura",
    )
    assert verify_password(
        changed.password_hash,
        "uma nova senha pedagógica",
    )


def test_change_password_rejects_wrong_current_password_without_mutation(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)
    original_hash = teacher.password_hash

    with pytest.raises(AuthenticationError, match="Senha atual incorreta"):
        service.change_password(
            school.school_id,
            teacher.teacher_id,
            current_password="senha atual errada",
            new_password="uma nova senha pedagógica",
        )

    assert teacher.password_hash == original_hash


def test_deactivate_teacher_preserves_record(
    service: TeacherService,
    session: Session,
) -> None:
    school = create_school(session)
    teacher = create_teacher(service, school)

    deactivated = service.deactivate_teacher(
        school.school_id,
        teacher.teacher_id,
    )

    assert deactivated.is_active is False

    with pytest.raises(EntityNotFoundError):
        service.get_teacher(school.school_id, teacher.teacher_id)

    assert service.get_teacher(
        school.school_id,
        teacher.teacher_id,
        include_inactive=True,
    ) is teacher
    assert session.scalar(
        select(Teacher).where(Teacher.teacher_id == teacher.teacher_id)
    ) is teacher

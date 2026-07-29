"""Integration tests for AuthenticationService."""

import pytest
from argon2 import PasswordHasher
from argon2.low_level import Type
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.security.passwords import verify_password
from src.services.authentication_service import AuthenticationService
from src.services.exceptions import AuthenticationError
from src.services.teacher_service import TeacherService


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


def create_account(
    session: Session,
    *,
    school_active: bool = True,
    teacher_active: bool = True,
) -> tuple[School, Teacher]:
    school = School(
        name="Escola Movimento",
        city="São Paulo",
        state="SP",
        is_active=True,
    )
    session.add(school)
    session.flush()
    teacher = TeacherService(session).create_teacher(
        school_id=school.school_id,
        name="Giovana Oliveira",
        email="giovana@exemplo.com",
        password="frase secreta pedagógica",
        role=TeacherRole.ADMINISTRATOR,
    )
    school.is_active = school_active
    teacher.is_active = teacher_active
    session.flush()
    return school, teacher


def test_authenticate_returns_minimal_identity_for_active_account(
    session: Session,
) -> None:
    school, teacher = create_account(session)

    identity = AuthenticationService(session).authenticate(
        email=" GIOVANA@EXEMPLO.COM ",
        password="frase secreta pedagógica",
    )

    assert identity.teacher_id == teacher.teacher_id
    assert identity.school_id == school.school_id
    assert identity.name == teacher.name
    assert identity.email == "giovana@exemplo.com"
    assert identity.role is TeacherRole.ADMINISTRATOR
    assert not hasattr(identity, "password_hash")


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("inexistente@exemplo.com", "frase secreta pedagógica"),
        ("giovana@exemplo.com", "uma frase secreta incorreta"),
        ("email-inválido", "frase secreta pedagógica"),
        ("giovana@exemplo.com", None),
        ("giovana@exemplo.com", "a" * 129),
    ],
)
def test_authenticate_uses_generic_error_for_invalid_credentials(
    session: Session,
    email: object,
    password: object,
) -> None:
    create_account(session)

    with pytest.raises(
        AuthenticationError,
        match="E-mail ou senha inválidos",
    ):
        AuthenticationService(session).authenticate(
            email=email,
            password=password,
        )


@pytest.mark.parametrize(
    ("school_active", "teacher_active"),
    [(False, True), (True, False)],
)
def test_inactive_school_or_teacher_cannot_authenticate(
    session: Session,
    school_active: bool,
    teacher_active: bool,
) -> None:
    create_account(
        session,
        school_active=school_active,
        teacher_active=teacher_active,
    )

    with pytest.raises(
        AuthenticationError,
        match="E-mail ou senha inválidos",
    ):
        AuthenticationService(session).authenticate(
            email="giovana@exemplo.com",
            password="frase secreta pedagógica",
        )


def test_successful_login_upgrades_legacy_argon2_parameters(
    session: Session,
) -> None:
    _, teacher = create_account(session)
    old_hasher = PasswordHasher(
        time_cost=1,
        memory_cost=8 * 1024,
        parallelism=1,
        hash_len=16,
        salt_len=16,
        type=Type.ID,
    )
    teacher.password_hash = old_hasher.hash("frase secreta pedagógica")
    old_hash = teacher.password_hash
    session.flush()

    AuthenticationService(session).authenticate(
        email=teacher.email,
        password="frase secreta pedagógica",
    )

    assert teacher.password_hash != old_hash
    assert verify_password(
        teacher.password_hash,
        "frase secreta pedagógica",
    )


def test_malformed_stored_hash_fails_as_generic_authentication_error(
    session: Session,
) -> None:
    _, teacher = create_account(session)
    teacher.password_hash = "hash-legado-inválido"
    session.flush()

    with pytest.raises(
        AuthenticationError,
        match="E-mail ou senha inválidos",
    ):
        AuthenticationService(session).authenticate(
            email=teacher.email,
            password="frase secreta pedagógica",
        )

"""Integration tests for the one-time provisioning workflow."""

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from src.business_rules.teacher_rules import TeacherValidationError
from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.security.passwords import verify_password
from src.services.exceptions import ConflictError
from src.services.initial_provisioning_service import (
    InitialProvisioningService,
)


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)
    Teacher.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


def provisioning_data() -> dict[str, str]:
    return {
        "school_name": " Escola Movimento ",
        "school_city": " São Paulo ",
        "school_state": "sp",
        "administrator_name": " Giovana Oliveira ",
        "administrator_email": " GIOVANA@EXEMPLO.COM ",
        "administrator_password": "senha pedagógica segura",
    }


def test_provision_creates_first_school_and_administrator(
    session: Session,
) -> None:
    access = InitialProvisioningService(session).provision(
        **provisioning_data()
    )

    school = session.get(School, access.school_id)
    administrator = session.get(Teacher, access.teacher_id)

    assert school is not None
    assert school.name == "Escola Movimento"
    assert school.city == "São Paulo"
    assert school.state == "SP"
    assert administrator is not None
    assert administrator.school_id == school.school_id
    assert administrator.name == "Giovana Oliveira"
    assert administrator.email == "giovana@exemplo.com"
    assert administrator.role is TeacherRole.ADMINISTRATOR
    assert administrator.password_hash.startswith("$argon2id$")
    assert verify_password(
        administrator.password_hash,
        "senha pedagógica segura",
    )
    assert access.administrator_email == "giovana@exemplo.com"


def test_provision_rejects_a_second_execution(session: Session) -> None:
    service = InitialProvisioningService(session)
    service.provision(**provisioning_data())
    session.commit()

    with pytest.raises(ConflictError, match="banco sem escolas"):
        service.provision(
            **{
                **provisioning_data(),
                "administrator_email": "outra@exemplo.com",
            }
        )

    assert session.scalar(select(func.count()).select_from(School)) == 1
    assert session.scalar(select(func.count()).select_from(Teacher)) == 1


def test_provision_administrator_for_sole_existing_school(
    session: Session,
) -> None:
    school = School(
        name="Escola já cadastrada",
        city="São Paulo",
        state="SP",
    )
    session.add(school)
    session.commit()

    access = InitialProvisioningService(
        session
    ).provision_administrator_for_existing_school(
        school_id=school.school_id,
        administrator_name="Giovana Oliveira",
        administrator_email="giovana@exemplo.com",
        administrator_password="senha pedagógica segura",
    )

    administrator = session.get(Teacher, access.teacher_id)
    assert access.school_id == school.school_id
    assert administrator is not None
    assert administrator.role is TeacherRole.ADMINISTRATOR
    assert verify_password(
        administrator.password_hash,
        "senha pedagógica segura",
    )


def test_existing_school_provision_rejects_ambiguous_school(
    session: Session,
) -> None:
    session.add_all(
        [
            School(name="Escola Um", city="São Paulo", state="SP"),
            School(name="Escola Dois", city="São Paulo", state="SP"),
        ]
    )
    session.commit()

    with pytest.raises(ConflictError, match="mais de uma escola"):
        InitialProvisioningService(session).find_existing_school_without_access()


def test_failed_provision_can_be_rolled_back_as_one_transaction(
    session: Session,
) -> None:
    data = provisioning_data()
    data["administrator_password"] = "curta"

    with pytest.raises(TeacherValidationError):
        InitialProvisioningService(session).provision(**data)

    session.rollback()

    assert session.scalar(select(func.count()).select_from(School)) == 0
    assert session.scalar(select(func.count()).select_from(Teacher)) == 0

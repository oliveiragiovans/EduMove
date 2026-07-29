"""Integration tests for SchoolService."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from src.business_rules.school_rules import SchoolValidationError
from src.models.school import School
from src.services.exceptions import ConflictError, EntityNotFoundError
from src.services.school_service import SchoolService


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    School.__table__.create(engine)

    with Session(engine) as database_session:
        yield database_session

    engine.dispose()


@pytest.fixture
def service(session: Session) -> SchoolService:
    return SchoolService(session)


def test_create_school_normalizes_and_persists_data(
    service: SchoolService,
) -> None:
    school = service.create_school(
        name="  Escola   Movimento ",
        cnpj="12.345.678/0001-99",
        email=" CONTATO@EXEMPLO.COM ",
        phone="(11) 99999-0000",
        city=" São  Paulo ",
        state="sp",
    )

    assert school.school_id is not None
    assert school.name == "Escola Movimento"
    assert school.cnpj == "12345678000199"
    assert school.email == "contato@exemplo.com"
    assert school.city == "São Paulo"
    assert school.state == "SP"
    assert school.is_active is True


def test_create_school_rejects_duplicate_cnpj(
    service: SchoolService,
    session: Session,
) -> None:
    service.create_school(
        name="Escola Um",
        cnpj="12.345.678/0001-99",
        city="São Paulo",
        state="SP",
    )
    session.commit()

    with pytest.raises(ConflictError):
        service.create_school(
            name="Escola Dois",
            cnpj="12.345.678/0001-99",
            city="Campinas",
            state="SP",
        )


def test_get_school_rejects_missing_school(service: SchoolService) -> None:
    with pytest.raises(EntityNotFoundError):
        service.get_school(999)


def test_list_schools_returns_active_records_ordered_by_name(
    service: SchoolService,
) -> None:
    second = service.create_school(
        name="Escola Beta",
        city="São Paulo",
        state="SP",
    )
    first = service.create_school(
        name="Escola Alfa",
        city="São Paulo",
        state="SP",
    )
    second.is_active = False
    service.session.flush()

    assert service.list_schools() == [first]
    assert service.list_schools(include_inactive=True) == [first, second]


def test_update_school_changes_only_informed_fields(
    service: SchoolService,
) -> None:
    school = service.create_school(
        name="Escola Antiga",
        email="antigo@exemplo.com",
        city="São Paulo",
        state="SP",
    )

    updated = service.update_school(
        school.school_id,
        name="Escola Atualizada",
        email=None,
        state="rj",
    )

    assert updated is school
    assert updated.name == "Escola Atualizada"
    assert updated.email is None
    assert updated.city == "São Paulo"
    assert updated.state == "RJ"


def test_update_school_rejects_empty_changes(
    service: SchoolService,
) -> None:
    school = service.create_school(
        name="Escola Movimento",
        city="São Paulo",
        state="SP",
    )

    with pytest.raises(SchoolValidationError):
        service.update_school(school.school_id)


def test_deactivate_school_preserves_record(
    service: SchoolService,
    session: Session,
) -> None:
    school = service.create_school(
        name="Escola Movimento",
        city="São Paulo",
        state="SP",
    )

    deactivated = service.deactivate_school(school.school_id)

    assert deactivated.is_active is False

    with pytest.raises(EntityNotFoundError):
        service.get_school(school.school_id)

    assert (
        service.get_school(
            school.school_id,
            include_inactive=True,
        )
        is school
    )
    assert session.scalar(
        select(School).where(School.school_id == school.school_id)
    ) is school

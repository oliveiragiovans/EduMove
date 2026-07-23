"""Tests for the School SQLAlchemy model."""

from sqlalchemy import CHAR, String

from src.models.school import School


def test_school_uses_expected_table_and_columns() -> None:
    assert School.__tablename__ == "schools"
    assert set(School.__table__.columns.keys()) == {
        "school_id",
        "name",
        "cnpj",
        "email",
        "phone",
        "city",
        "state",
        "created_at",
        "updated_at",
    }


def test_school_primary_key_is_generated_by_database() -> None:
    school_id = School.__table__.c.school_id

    assert school_id.primary_key is True
    assert school_id.autoincrement is True
    assert school_id.nullable is False


def test_school_required_and_optional_fields_match_schema() -> None:
    columns = School.__table__.c

    assert columns.name.nullable is False
    assert columns.city.nullable is False
    assert columns.state.nullable is False

    assert columns.cnpj.nullable is True
    assert columns.email.nullable is True
    assert columns.phone.nullable is True


def test_school_text_field_lengths_match_schema() -> None:
    columns = School.__table__.c

    assert isinstance(columns.name.type, String)
    assert columns.name.type.length == 150
    assert isinstance(columns.cnpj.type, CHAR)
    assert columns.cnpj.type.length == 14
    assert columns.email.type.length == 100
    assert columns.phone.type.length == 20
    assert columns.city.type.length == 100
    assert isinstance(columns.state.type, CHAR)
    assert columns.state.type.length == 2


def test_school_cnpj_is_unique() -> None:
    assert School.__table__.c.cnpj.unique is True


def test_school_timestamps_are_managed_by_database() -> None:
    columns = School.__table__.c

    assert columns.created_at.nullable is False
    assert columns.created_at.server_default is not None
    assert columns.updated_at.nullable is False
    assert columns.updated_at.server_default is not None
    assert columns.updated_at.server_onupdate is not None

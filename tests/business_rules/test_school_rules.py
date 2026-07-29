"""Tests for school validation and normalization rules."""

import pytest

from src.business_rules.school_rules import (
    SchoolValidationError,
    normalize_school_changes,
    normalize_school_data,
)


def test_normalize_school_data_cleans_supported_fields() -> None:
    data = normalize_school_data(
        name="  Escola   Movimento  ",
        cnpj="12.345.678/0001-99",
        email=" CONTATO@EXEMPLO.COM ",
        phone=" (11) 99999-0000 ",
        city="  São   Paulo ",
        state="sp",
    )

    assert data == {
        "name": "Escola Movimento",
        "cnpj": "12345678000199",
        "email": "contato@exemplo.com",
        "phone": "(11) 99999-0000",
        "city": "São Paulo",
        "state": "SP",
    }


def test_normalize_school_data_converts_blank_optional_fields_to_none() -> None:
    data = normalize_school_data(
        name="Escola Movimento",
        city="São Paulo",
        state="SP",
        cnpj=" ",
        email=" ",
        phone=" ",
    )

    assert data["cnpj"] is None
    assert data["email"] is None
    assert data["phone"] is None


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", ""),
        ("city", "   "),
        ("state", "S"),
        ("state", "123"),
        ("cnpj", "123"),
        ("cnpj", "12.345.678/0001-AB"),
        ("email", "email-invalido"),
    ],
)
def test_normalize_school_data_rejects_invalid_fields(
    field: str,
    value: str,
) -> None:
    data = {
        "name": "Escola Movimento",
        "city": "São Paulo",
        "state": "SP",
        "cnpj": None,
        "email": None,
        "phone": None,
    }
    data[field] = value

    with pytest.raises(SchoolValidationError) as error:
        normalize_school_data(**data)

    assert error.value.field == field


def test_normalize_school_changes_accepts_partial_updates() -> None:
    assert normalize_school_changes(
        {
            "email": " NOVO@EXEMPLO.COM ",
            "state": "rj",
        }
    ) == {
        "email": "novo@exemplo.com",
        "state": "RJ",
    }


def test_normalize_school_changes_rejects_empty_updates() -> None:
    with pytest.raises(SchoolValidationError) as error:
        normalize_school_changes({})

    assert error.value.field == "changes"


def test_normalize_school_changes_rejects_non_editable_fields() -> None:
    with pytest.raises(SchoolValidationError) as error:
        normalize_school_changes({"is_active": False})

    assert error.value.field == "changes"

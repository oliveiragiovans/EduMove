"""Tests for secure interactive provisioning input."""

from collections.abc import Iterator

import pytest

from src.business_rules.teacher_rules import TeacherValidationError
from src.cli.provision_first_administrator import collect_form


def input_reader(values: list[str]):
    answers: Iterator[str] = iter(values)

    def read(_prompt: str) -> str:
        return next(answers)

    return read


def test_collect_form_keeps_password_out_of_prompts_and_output(capsys) -> None:
    password = "senha pedagógica segura"
    password_prompts: list[str] = []

    def read_password(prompt: str) -> str:
        password_prompts.append(prompt)
        return password

    form = collect_form(
        input_fn=input_reader(
            [
                "Escola Movimento",
                "São Paulo",
                "SP",
                "",
                "",
                "",
                "Giovana Oliveira",
                "giovana@exemplo.com",
            ]
        ),
        password_fn=read_password,
    )

    captured = capsys.readouterr()
    assert form.administrator_password == password
    assert len(password_prompts) == 2
    assert password not in captured.out
    assert all(password not in prompt for prompt in password_prompts)


def test_collect_form_rejects_mismatched_passwords() -> None:
    passwords = iter(["senha pedagógica segura", "senha diferente e segura"])

    with pytest.raises(TeacherValidationError, match="não coincidem"):
        collect_form(
            input_fn=input_reader(
                [
                    "Escola Movimento",
                    "São Paulo",
                    "SP",
                    "",
                    "",
                    "",
                    "Giovana Oliveira",
                    "giovana@exemplo.com",
                ]
            ),
            password_fn=lambda _prompt: next(passwords),
        )

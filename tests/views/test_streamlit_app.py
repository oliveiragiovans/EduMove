"""Smoke tests for the Streamlit login and authenticated shell."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

from src.models.teacher import TeacherRole
from src.services.authentication_service import AuthenticatedTeacher
from src.views.auth_session import AUTHENTICATED_TEACHER_KEY


APP_PATH = Path(__file__).resolve().parents[2] / "app.py"


def test_public_app_renders_login_form_without_database_access() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=15)

    assert not app.exception
    assert [field.label for field in app.text_input] == ["E-mail", "Senha"]
    assert [button.label for button in app.button] == ["Entrar no EduMove"]
    assert any(
        "Bem-vinda de volta" in block.value
        for block in app.markdown
    )


def test_empty_login_submission_shows_friendly_validation() -> None:
    app = AppTest.from_file(str(APP_PATH)).run(timeout=15)

    app.button[0].click().run(timeout=15)

    assert not app.exception
    assert app.warning[0].value == (
        "Informe o e-mail e a senha para continuar."
    )


def test_authenticated_identity_renders_dashboard_and_logout() -> None:
    app = AppTest.from_file(str(APP_PATH))
    app.session_state[AUTHENTICATED_TEACHER_KEY] = AuthenticatedTeacher(
        teacher_id=7,
        school_id=3,
        name="Giovana Oliveira",
        email="giovana@exemplo.com",
        role=TeacherRole.TEACHER,
    )

    app.run(timeout=15)

    assert not app.exception
    assert app.title[0].value == "Olá, Giovana! 👋"
    assert any(button.label == "Sair" for button in app.button)
    assert len(app.text_input) == 0


def test_logout_clears_identity_and_returns_to_login() -> None:
    app = AppTest.from_file(str(APP_PATH))
    app.session_state[AUTHENTICATED_TEACHER_KEY] = AuthenticatedTeacher(
        teacher_id=7,
        school_id=3,
        name="Giovana Oliveira",
        email="giovana@exemplo.com",
        role=TeacherRole.TEACHER,
    )
    app.run(timeout=15)
    logout_button = next(
        button for button in app.button if button.label == "Sair"
    )

    logout_button.click().run(timeout=15)

    assert not app.exception
    assert app.session_state[AUTHENTICATED_TEACHER_KEY] is None
    assert [field.label for field in app.text_input] == ["E-mail", "Senha"]

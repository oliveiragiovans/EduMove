"""Tests for Streamlit authentication-state helpers."""

from src.models.teacher import TeacherRole
from src.services.authentication_service import AuthenticatedTeacher
from src.views.auth_session import (
    AUTHENTICATED_TEACHER_KEY,
    clear_authenticated_teacher,
    get_authenticated_teacher,
    initialize_authentication_state,
    set_authenticated_teacher,
)


def create_identity() -> AuthenticatedTeacher:
    return AuthenticatedTeacher(
        teacher_id=7,
        school_id=3,
        name="Giovana Oliveira",
        email="giovana@exemplo.com",
        role=TeacherRole.TEACHER,
    )


def test_authentication_state_starts_without_identity() -> None:
    state: dict[str, object] = {}

    initialize_authentication_state(state)

    assert state == {AUTHENTICATED_TEACHER_KEY: None}
    assert get_authenticated_teacher(state) is None


def test_identity_can_be_stored_and_removed_without_credentials() -> None:
    state: dict[str, object] = {}
    identity = create_identity()

    set_authenticated_teacher(state, identity)

    assert get_authenticated_teacher(state) is identity
    assert set(state[AUTHENTICATED_TEACHER_KEY].__dict__) == {
        "teacher_id",
        "school_id",
        "name",
        "email",
        "role",
    }

    clear_authenticated_teacher(state)

    assert get_authenticated_teacher(state) is None


def test_malformed_identity_is_treated_as_logged_out() -> None:
    state = {
        AUTHENTICATED_TEACHER_KEY: {
            "teacher_id": 7,
            "password": "não deve ser aceito",
        }
    }

    assert get_authenticated_teacher(state) is None

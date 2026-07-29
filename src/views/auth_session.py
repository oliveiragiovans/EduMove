"""Authentication state helpers for the Streamlit interface."""

from collections.abc import MutableMapping
from typing import Any

from src.services.authentication_service import AuthenticatedTeacher


AUTHENTICATED_TEACHER_KEY = "authenticated_teacher"


def initialize_authentication_state(
    state: MutableMapping[str, Any],
) -> None:
    """Ensure the authentication key exists for a new browser session."""

    state.setdefault(AUTHENTICATED_TEACHER_KEY, None)


def get_authenticated_teacher(
    state: MutableMapping[str, Any],
) -> AuthenticatedTeacher | None:
    """Return the current safe identity, ignoring malformed state."""

    identity = state.get(AUTHENTICATED_TEACHER_KEY)

    if isinstance(identity, AuthenticatedTeacher):
        return identity

    return None


def set_authenticated_teacher(
    state: MutableMapping[str, Any],
    identity: AuthenticatedTeacher,
) -> None:
    """Store only the minimal authenticated identity in the browser session."""

    state[AUTHENTICATED_TEACHER_KEY] = identity


def clear_authenticated_teacher(
    state: MutableMapping[str, Any],
) -> None:
    """Remove the identity when the teacher logs out."""

    state[AUTHENTICATED_TEACHER_KEY] = None

"""EduMove Streamlit entry point."""

import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from src.config.database import session_scope
from src.services.authentication_service import (
    AuthenticatedTeacher,
    AuthenticationService,
)
from src.services.exceptions import AuthenticationError
from src.views.auth_session import (
    get_authenticated_teacher,
    initialize_authentication_state,
)
from src.views.dashboard import render_dashboard
from src.views.login import render_login
from src.views.styles import apply_global_styles


def authenticate_teacher(email: str, password: str) -> AuthenticatedTeacher:
    """Authenticate one teacher in a committed database transaction."""

    try:
        with session_scope() as session:
            return AuthenticationService(session).authenticate(
                email=email,
                password=password,
            )
    except AuthenticationError:
        raise
    except SQLAlchemyError as error:
        raise AuthenticationError(
            "Não foi possível acessar o EduMove agora. Tente novamente."
        ) from error


def main() -> None:
    """Render the login page or the authenticated application shell."""

    st.set_page_config(
        page_title="EduMove",
        page_icon="🏃",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_global_styles()
    initialize_authentication_state(st.session_state)
    identity = get_authenticated_teacher(st.session_state)

    if identity is None:
        render_login(authenticate_teacher, st.session_state)
        return

    render_dashboard(identity, st.session_state)


if __name__ == "__main__":
    main()

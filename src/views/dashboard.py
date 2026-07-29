"""Authenticated Streamlit application shell."""

from collections.abc import MutableMapping
from html import escape
from typing import Any

import streamlit as st

from src.services.authentication_service import AuthenticatedTeacher
from src.views.auth_session import clear_authenticated_teacher


def render_dashboard(
    identity: AuthenticatedTeacher,
    state: MutableMapping[str, Any],
) -> None:
    """Render the first authenticated EduMove workspace."""

    safe_name = escape(identity.name)
    safe_initial = escape(identity.name[:1].upper())
    safe_role = escape(identity.role.value)

    with st.sidebar:
        st.markdown(
            """
            <div class="edumove-sidebar-brand">
                <span class="edumove-logo-mark">EM</span>
                <strong>EduMove</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="edumove-profile">
                <span class="edumove-avatar">
                    {safe_initial}
                </span>
                <div>
                    <strong>{safe_name}</strong>
                    <small>{safe_role}</small>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    selected_page = st.navigation(
        [
            st.Page(
                _render_home,
                title="Início",
                icon=":material/home:",
                default=True,
            ),
            st.Page(
                _render_assessments_placeholder,
                title="Avaliações",
                icon=":material/assignment:",
            ),
        ],
        position="sidebar",
    )

    with st.sidebar:
        st.divider()

        if st.button(
            "Sair",
            icon=":material/logout:",
            use_container_width=True,
            key="logout_button",
        ):
            clear_authenticated_teacher(state)
            st.rerun()

    selected_page.run()


def _render_home() -> None:
    """Render a concise landing dashboard for the authenticated teacher."""

    identity = st.session_state.get("authenticated_teacher")
    first_name = identity.name.split()[0] if identity else "professora"
    st.markdown('<p class="edumove-eyebrow">VISÃO GERAL</p>', unsafe_allow_html=True)
    st.title(f"Olá, {first_name}! 👋")
    st.write(
        "A base do EduMove está pronta. A partir daqui, vamos conectar "
        "os cadastros e as avaliações à interface."
    )

    first, second, third = st.columns(3)

    with first:
        _status_card(
            "Alunos",
            "Cadastros e histórico individual",
            "Próxima etapa",
            "🧒",
        )

    with second:
        _status_card(
            "Avaliações",
            "Medidas, testes motores e postura",
            "Backend pronto",
            "📋",
        )

    with third:
        _status_card(
            "Segurança",
            "Acesso protegido por Argon2id",
            "Concluído",
            "🔐",
        )

    st.info(
        "Esta é a primeira área autenticada. Os indicadores reais aparecerão "
        "quando conectarmos os módulos de turmas, alunos e avaliações."
    )


def _render_assessments_placeholder() -> None:
    """Preview the next interface module without exposing unfinished actions."""

    st.markdown('<p class="edumove-eyebrow">AVALIAÇÕES</p>', unsafe_allow_html=True)
    st.title("Avaliações dos alunos")
    st.write(
        "Aqui entraremos com o fluxo guiado de medidas, testes motores "
        "e observações posturais."
    )
    st.warning("Módulo visual em construção. O backend já está preparado.")


def _status_card(
    title: str,
    description: str,
    status: str,
    icon: str,
) -> None:
    st.markdown(
        f"""
        <div class="edumove-status-card">
            <span class="edumove-card-icon">{icon}</span>
            <h3>{title}</h3>
            <p>{description}</p>
            <small>{status}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

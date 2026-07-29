"""Streamlit login page."""

from collections.abc import Callable, MutableMapping
from typing import Any

import streamlit as st

from src.services.authentication_service import AuthenticatedTeacher
from src.services.exceptions import AuthenticationError
from src.views.auth_session import set_authenticated_teacher


AuthenticationCallback = Callable[[str, str], AuthenticatedTeacher]


def render_login(
    authenticate: AuthenticationCallback,
    state: MutableMapping[str, Any],
) -> None:
    """Render the public login page and establish an authenticated session."""

    brand_column, form_column = st.columns([1.15, 0.85], gap="large")

    with brand_column:
        st.markdown(
            """
            <div class="edumove-hero">
                <span class="edumove-kicker">MOVIMENTO QUE ENSINA</span>
                <h1>EduMove</h1>
                <p class="edumove-hero-copy">
                    Avaliações escolares organizadas para acompanhar cada aluno
                    com clareza, cuidado e propósito pedagógico.
                </p>
                <div class="edumove-feature">
                    <span>✓</span>
                    <p>Histórico individual preservado ao longo do tempo</p>
                </div>
                <div class="edumove-feature">
                    <span>✓</span>
                    <p>Avaliações antropométricas, motoras e posturais</p>
                </div>
                <div class="edumove-feature">
                    <span>✓</span>
                    <p>Dados organizados para apoiar o planejamento docente</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_column:
        st.markdown(
            """
            <div class="edumove-login-heading">
                <span class="edumove-logo-mark">EM</span>
                <div>
                    <p class="edumove-eyebrow">ÁREA DO PROFESSOR</p>
                    <h2>Bem-vinda de volta</h2>
                </div>
            </div>
            <p class="edumove-login-copy">
                Entre com seu e-mail institucional para acessar o EduMove.
            </p>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            email = st.text_input(
                "E-mail",
                placeholder="professora@escola.com.br",
            )
            password = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha",
            )
            submitted = st.form_submit_button(
                "Entrar no EduMove",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if not email or not password:
                st.warning("Informe o e-mail e a senha para continuar.")
            else:
                try:
                    identity = authenticate(email, password)
                except AuthenticationError as error:
                    st.error(str(error))
                else:
                    set_authenticated_teacher(state, identity)
                    st.rerun()

        st.caption(
            "O EduMove armazena somente a versão protegida da sua senha."
        )

"""Shared visual language for the EduMove Streamlit interface."""

import streamlit as st


_GLOBAL_STYLES = """
<style>
    :root {
        --edumove-ink: #18352f;
        --edumove-muted: #667b75;
        --edumove-green: #16836f;
        --edumove-green-dark: #0d6657;
        --edumove-mint: #def4e9;
        --edumove-cream: #f8f6ef;
        --edumove-coral: #ef8b72;
        --edumove-white: #ffffff;
        --edumove-border: #dce7e2;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 15%, rgba(210, 239, 224, .72), transparent 28rem),
            linear-gradient(135deg, #fbfaf5 0%, #f5f9f6 55%, #eef7f3 100%);
        color: var(--edumove-ink);
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1180px;
        padding-top: 5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, p, label {
        color: var(--edumove-ink);
    }

    .edumove-hero {
        padding: 2.4rem 2.8rem 2.4rem 0;
    }

    .edumove-kicker,
    .edumove-eyebrow {
        color: var(--edumove-green);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .14em;
        margin: 0 0 .65rem;
    }

    .edumove-hero h1 {
        font-size: clamp(4rem, 8vw, 6.5rem);
        letter-spacing: -.07em;
        line-height: .95;
        margin: .2rem 0 1.4rem;
    }

    .edumove-hero-copy {
        color: var(--edumove-muted);
        font-size: 1.2rem;
        line-height: 1.65;
        max-width: 37rem;
        margin-bottom: 2rem;
    }

    .edumove-feature {
        align-items: center;
        display: flex;
        gap: .8rem;
        margin: .8rem 0;
    }

    .edumove-feature span {
        align-items: center;
        background: var(--edumove-mint);
        border-radius: 999px;
        color: var(--edumove-green-dark);
        display: inline-flex;
        font-weight: 800;
        height: 1.8rem;
        justify-content: center;
        width: 1.8rem;
    }

    .edumove-feature p {
        font-size: .97rem;
        margin: 0;
    }

    [data-testid="stForm"] {
        background: rgba(255, 255, 255, .9);
        border: 1px solid var(--edumove-border);
        border-radius: 1.4rem;
        box-shadow: 0 24px 70px rgba(32, 77, 67, .11);
        padding: 1.7rem;
    }

    .edumove-login-heading {
        align-items: center;
        display: flex;
        gap: 1rem;
        margin-top: 1.2rem;
    }

    .edumove-login-heading h2 {
        font-size: 2rem;
        letter-spacing: -.03em;
        margin: 0;
    }

    .edumove-login-copy {
        color: var(--edumove-muted);
        margin: 1rem 0 1.4rem;
    }

    .edumove-logo-mark {
        align-items: center;
        background: var(--edumove-green);
        border-radius: .9rem;
        color: white;
        display: inline-flex;
        font-size: .82rem;
        font-weight: 900;
        height: 3.2rem;
        justify-content: center;
        letter-spacing: -.04em;
        transform: rotate(-4deg);
        width: 3.2rem;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        border-radius: .8rem;
        font-weight: 750;
        min-height: 2.9rem;
    }

    .stFormSubmitButton > button[kind="primary"],
    .stButton > button[kind="primary"] {
        background: var(--edumove-green);
        border-color: var(--edumove-green);
    }

    .stFormSubmitButton > button[kind="primary"]:hover,
    .stButton > button[kind="primary"]:hover {
        background: var(--edumove-green-dark);
        border-color: var(--edumove-green-dark);
    }

    [data-testid="stSidebar"] {
        background: #f4f8f5;
        border-right: 1px solid var(--edumove-border);
    }

    .edumove-sidebar-brand {
        align-items: center;
        display: flex;
        font-size: 1.25rem;
        gap: .8rem;
        margin: .5rem 0 2rem;
    }

    .edumove-sidebar-brand .edumove-logo-mark {
        border-radius: .65rem;
        height: 2.5rem;
        width: 2.5rem;
    }

    .edumove-profile {
        align-items: center;
        background: white;
        border: 1px solid var(--edumove-border);
        border-radius: 1rem;
        display: flex;
        gap: .75rem;
        margin-bottom: 1.5rem;
        padding: .85rem;
    }

    .edumove-profile div {
        display: flex;
        flex-direction: column;
        min-width: 0;
    }

    .edumove-profile strong {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .edumove-profile small {
        color: var(--edumove-muted);
    }

    .edumove-avatar {
        align-items: center;
        background: var(--edumove-mint);
        border-radius: 999px;
        color: var(--edumove-green-dark);
        display: inline-flex;
        flex: 0 0 auto;
        font-weight: 900;
        height: 2.6rem;
        justify-content: center;
        width: 2.6rem;
    }

    .edumove-status-card {
        background: rgba(255, 255, 255, .88);
        border: 1px solid var(--edumove-border);
        border-radius: 1.2rem;
        min-height: 12rem;
        padding: 1.35rem;
    }

    .edumove-status-card h3 {
        margin: .8rem 0 .4rem;
    }

    .edumove-status-card p {
        color: var(--edumove-muted);
        min-height: 3rem;
    }

    .edumove-status-card small {
        background: var(--edumove-mint);
        border-radius: 999px;
        color: var(--edumove-green-dark);
        font-weight: 750;
        padding: .35rem .65rem;
    }

    .edumove-card-icon {
        font-size: 1.7rem;
    }

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem;
        }

        .edumove-hero {
            padding: 1rem 0;
        }

        .edumove-hero h1 {
            font-size: 4rem;
        }
    }
</style>
"""


def apply_global_styles() -> None:
    """Inject the shared EduMove theme into the current Streamlit page."""

    st.markdown(_GLOBAL_STYLES, unsafe_allow_html=True)

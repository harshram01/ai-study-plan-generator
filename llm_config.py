"""
Central place that builds the LangChain chat model.

Every provider below exposes the same LangChain chat model interface,
so the rest of the app (extractor.py, explainer.py) never needs to
know or care which one is active. Switch providers by changing
LLM_PROVIDER in your .env file.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def get_api_key(provider: str, explicit_key: str = None) -> str:
    """
    Resolve the API key in order of precedence:
      1. Explicit key passed directly (e.g. from Streamlit sidebar input)
      2. Environment variable (from .env or host environment)
      3. Streamlit Cloud secrets (st.secrets)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    key_var = "GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"

    # 1. Check environment variable (.env / OS)
    env_val = os.getenv(key_var)
    if env_val and env_val.strip():
        return env_val.strip()

    # 2. Check Streamlit secrets (Streamlit Community Cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key_var in st.secrets:
            sec_val = st.secrets[key_var]
            if sec_val and str(sec_val).strip():
                return str(sec_val).strip()
    except Exception:
        pass

    return ""


def get_llm(
    temperature: float = 0.2,
    provider: str = None,
    api_key: str = None,
    model: str = None,
):
    """Return a LangChain chat model based on provider and resolved API key."""
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "groq")
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "LLM_PROVIDER" in st.secrets:
                provider = st.secrets["LLM_PROVIDER"]
        except Exception:
            pass

    provider = str(provider).strip().lower()
    resolved_key = get_api_key(provider, explicit_key=api_key)

    if not resolved_key:
        key_var = "GROQ_API_KEY" if provider == "groq" else "OPENAI_API_KEY"
        raise ValueError(
            f"No API key found for {provider.upper()}. Please add {key_var} to your .env file, "
            f"configure it in Streamlit Cloud Secrets, or enter it in the sidebar."
        )

    if provider == "groq":
        from langchain_groq import ChatGroq

        selected_model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
        try:
            import streamlit as st
            if not model and hasattr(st, "secrets") and "GROQ_MODEL" in st.secrets:
                selected_model = st.secrets["GROQ_MODEL"]
        except Exception:
            pass

        return ChatGroq(
            model=selected_model,
            temperature=temperature,
            api_key=resolved_key,
        )

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        try:
            import streamlit as st
            if not model and hasattr(st, "secrets") and "OPENAI_MODEL" in st.secrets:
                selected_model = st.secrets["OPENAI_MODEL"]
        except Exception:
            pass

        return ChatOpenAI(
            model=selected_model,
            temperature=temperature,
            api_key=resolved_key,
        )

    raise ValueError(
        f"Unsupported LLM_PROVIDER '{provider}'. Use 'groq' or 'openai'."
    )

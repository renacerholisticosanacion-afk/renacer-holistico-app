"""Acceso seguro a st.secrets: si no existe ningún secrets.toml, Streamlit
lanza StreamlitSecretNotFoundError en vez de comportarse como vacío."""


def to_dict(st_secrets):
    try:
        return dict(st_secrets)
    except Exception:
        return {}

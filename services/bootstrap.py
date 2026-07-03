"""Elige backends reales (Google) o locales (demo) según lo configurado en st.secrets."""
from collections import namedtuple

from services.calendar_backend import LocalCalendarBackend, GoogleCalendarBackend
from services.storage_backend import LocalJSONStorage, GoogleSheetsStorage
from services.config_backend import LocalJSONConfigStorage, GoogleSheetsConfigStorage
from services.notifications import LocalNotifier, GmailNotifier

Backends = namedtuple("Backends", ["calendar", "storage", "config", "notifier", "demo_mode"])

_cache = {}


def get_backends(secrets):
    if _cache:
        return _cache["backends"]

    tiene_google = "gcp_service_account" in secrets and "google_calendar_id" in secrets and "google_sheet_key" in secrets

    if tiene_google:
        calendar, storage, config = _build_google_backends(secrets)
    else:
        calendar, storage, config = LocalCalendarBackend(), LocalJSONStorage(), LocalJSONConfigStorage()

    if "gmail_remitente" in secrets and "gmail_app_password" in secrets:
        notifier = GmailNotifier(secrets["gmail_remitente"], secrets["gmail_app_password"])
    else:
        notifier = LocalNotifier()

    backends = Backends(calendar=calendar, storage=storage, config=config, notifier=notifier, demo_mode=not tiene_google)
    _cache["backends"] = backends
    return backends


def _build_google_backends(secrets):
    import google.auth
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    import gspread

    scopes = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    creds = Credentials.from_service_account_info(dict(secrets["gcp_service_account"]), scopes=scopes)

    calendar_service = build("calendar", "v3", credentials=creds)
    calendar = GoogleCalendarBackend(calendar_service, secrets["google_calendar_id"])

    gc = gspread.authorize(creds)
    storage = GoogleSheetsStorage(gc, secrets["google_sheet_key"])
    config = GoogleSheetsConfigStorage(gc, secrets["google_sheet_key"])

    return calendar, storage, config

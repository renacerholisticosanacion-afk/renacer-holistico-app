"""Backends de calendario: local (demo) y Google Calendar (producción)."""
import json
import os
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

TZ_ARGENTINA = ZoneInfo("America/Argentina/Buenos_Aires")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EVENTS_FILE = os.path.join(DATA_DIR, "calendar_events.json")


class LocalCalendarBackend:
    """Simula un calendario guardando eventos en un archivo JSON local."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _leer(self):
        try:
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _escribir(self, eventos):
        with open(EVENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(eventos, f, ensure_ascii=False, indent=2)

    def get_busy_intervals(self, desde, hasta):
        eventos = self._leer()
        intervalos = []
        for e in eventos:
            if e.get("cancelado"):
                continue
            inicio = datetime.fromisoformat(e["inicio"])
            fin = datetime.fromisoformat(e["fin"])
            if inicio < hasta and fin > desde:
                intervalos.append((inicio, fin))
        return intervalos

    def create_event(self, summary, inicio, fin, description=""):
        eventos = self._leer()
        event_id = str(uuid.uuid4())
        eventos.append({
            "id": event_id,
            "summary": summary,
            "description": description,
            "inicio": inicio.isoformat(),
            "fin": fin.isoformat(),
            "cancelado": False,
        })
        self._escribir(eventos)
        return event_id

    def delete_event(self, event_id):
        eventos = self._leer()
        for e in eventos:
            if e["id"] == event_id:
                e["cancelado"] = True
                break
        self._escribir(eventos)


class GoogleCalendarBackend:
    """Backend real usando la Google Calendar API con una cuenta de servicio."""

    def __init__(self, service, calendar_id):
        self.service = service
        self.calendar_id = calendar_id

    def get_busy_intervals(self, desde, hasta):
        desde_tz = desde if desde.tzinfo else desde.replace(tzinfo=TZ_ARGENTINA)
        hasta_tz = hasta if hasta.tzinfo else hasta.replace(tzinfo=TZ_ARGENTINA)
        body = {
            "timeMin": desde_tz.isoformat(),
            "timeMax": hasta_tz.isoformat(),
            "items": [{"id": self.calendar_id}],
        }
        resp = self.service.freebusy().query(body=body).execute()
        busy = resp["calendars"][self.calendar_id]["busy"]
        intervalos = []
        for b in busy:
            inicio = datetime.fromisoformat(b["start"]).astimezone(TZ_ARGENTINA).replace(tzinfo=None)
            fin = datetime.fromisoformat(b["end"]).astimezone(TZ_ARGENTINA).replace(tzinfo=None)
            intervalos.append((inicio, fin))
        return intervalos

    def create_event(self, summary, inicio, fin, description=""):
        evento = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": inicio.isoformat(), "timeZone": "America/Argentina/Buenos_Aires"},
            "end": {"dateTime": fin.isoformat(), "timeZone": "America/Argentina/Buenos_Aires"},
        }
        creado = self.service.events().insert(calendarId=self.calendar_id, body=evento).execute()
        return creado["id"]

    def delete_event(self, event_id):
        try:
            self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
        except Exception:
            pass

"""Backends de almacenamiento de reservas: local (demo) y Google Sheets (producción)."""
import json
import os
import uuid

CAMPOS = [
    "id", "tipo", "terapia_key", "terapia_nombre", "inicio", "fin",
    "nombre", "telefono", "email", "precio", "sena", "estado",
    "calendar_event_id", "notas", "creado",
]

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
BOOKINGS_FILE = os.path.join(DATA_DIR, "bookings.json")


class LocalJSONStorage:
    """Guarda las reservas en un archivo JSON local. Solo para desarrollo/demo."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _leer(self):
        try:
            with open(BOOKINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _escribir(self, registros):
        with open(BOOKINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(registros, f, ensure_ascii=False, indent=2)

    def add_booking(self, record):
        registros = self._leer()
        record = dict(record)
        record["id"] = record.get("id") or str(uuid.uuid4())
        registros.append(record)
        self._escribir(registros)
        return record["id"]

    def list_bookings(self):
        return self._leer()

    def update_booking(self, booking_id, fields):
        registros = self._leer()
        for r in registros:
            if r["id"] == booking_id:
                r.update(fields)
                break
        self._escribir(registros)


class GoogleSheetsStorage:
    """Guarda las reservas en una Google Sheet compartida."""

    def __init__(self, gspread_client, sheet_key, worksheet_name="Reservas"):
        sheet = gspread_client.open_by_key(sheet_key)
        try:
            self.ws = sheet.worksheet(worksheet_name)
        except Exception:
            self.ws = sheet.add_worksheet(title=worksheet_name, rows=1000, cols=len(CAMPOS))
            self.ws.append_row(CAMPOS)

    def add_booking(self, record):
        record = dict(record)
        record["id"] = record.get("id") or str(uuid.uuid4())
        fila = [str(record.get(campo, "")) for campo in CAMPOS]
        self.ws.append_row(fila)
        return record["id"]

    def list_bookings(self):
        return self.ws.get_all_records()

    def update_booking(self, booking_id, fields):
        celdas = self.ws.findall(booking_id)
        for celda in celdas:
            fila = celda.row
            encabezados = self.ws.row_values(1)
            if encabezados[celda.col - 1] != "id":
                continue
            for campo, valor in fields.items():
                if campo in encabezados:
                    col = encabezados.index(campo) + 1
                    self.ws.update_cell(fila, col, str(valor))
            break

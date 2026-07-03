"""Backend de configuración editable (precios, datos de pago): local (demo) y Google Sheets (producción)."""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config_override.json")


class LocalJSONConfigStorage:
    """Guarda los overrides de configuración en un archivo JSON local. Solo para desarrollo/demo."""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _leer(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_all(self):
        return self._leer()

    def set(self, key, value):
        datos = self._leer()
        datos[key] = value
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)


class GoogleSheetsConfigStorage:
    """Guarda los overrides de configuración en una hoja 'Config' (clave, valor JSON) de la Sheet compartida."""

    def __init__(self, gspread_client, sheet_key, worksheet_name="Config"):
        sheet = gspread_client.open_by_key(sheet_key)
        try:
            self.ws = sheet.worksheet(worksheet_name)
        except Exception:
            self.ws = sheet.add_worksheet(title=worksheet_name, rows=100, cols=2)
            self.ws.append_row(["key", "value"])

    def get_all(self):
        registros = self.ws.get_all_records()
        return {r["key"]: json.loads(r["value"]) for r in registros if r.get("key") and r.get("value")}

    def set(self, key, value):
        valor_str = json.dumps(value, ensure_ascii=False)
        celdas = self.ws.findall(key)
        for celda in celdas:
            if celda.col == 1:
                self.ws.update_cell(celda.row, 2, valor_str)
                return
        self.ws.append_row([key, valor_str])

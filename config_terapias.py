"""Configuración de terapias, horarios de atención, pagos y mensajes."""

GRUPO_MEET = "meet"
GRUPO_DISTANCIA = "distancia"
GRUPO_ENTREGA = "entrega"

TERAPIAS = {
    "biodecodificacion": {
        "nombre": "Biodescodificación",
        "grupo": GRUPO_MEET,
        "duracion_min": 90,
        "precio": 40000,
        "min_dias": 7,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a contactar para enviarte el link de Meet. "
            "Antes de la sesión vas a recibir un formulario para completar."
        ),
    },
    "reiki": {
        "nombre": "Reiki",
        "grupo": GRUPO_DISTANCIA,
        "duracion_min": 60,
        "precio": 30000,
        "min_dias": 2,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a escribir para avisarte que comienzo. "
            "Dentro de las 24 hs siguientes vas a recibir un informe escrito."
        ),
    },
    "radiestesia": {
        "nombre": "Radiestesia",
        "grupo": GRUPO_DISTANCIA,
        "duracion_min": 60,
        "precio": 30000,
        "min_dias": 2,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a escribir para avisarte que comienzo. "
            "Dentro de las 24 hs siguientes vas a recibir un informe escrito."
        ),
    },
    "tarot": {
        "nombre": "Tarot Evolutivo",
        "grupo": GRUPO_ENTREGA,
        "duracion_min": 30,
        "precio": 20000,
        "min_dias": 1,
        "mensaje_confirmacion": (
            "Vas a recibir tu tirada con la explicación por WhatsApp en la fecha y horario indicado."
        ),
    },
    "habitarme": {
        "nombre": "Programa Habitarme",
        "grupo": GRUPO_MEET,
        "duracion_min": 60,
        "precio": 40000,
        "min_dias": 7,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a contactar para enviarte el link de Meet. "
            "Antes de la sesión vas a recibir un formulario para completar."
        ),
    },
    "carta_numerologica": {
        "nombre": "Carta Numerológica",
        "grupo": GRUPO_ENTREGA,
        "duracion_min": 30,
        "precio": 40000,
        "min_dias": 10,
        "mensaje_confirmacion": (
            "Vas a recibir tu informe por WhatsApp en la fecha y horario indicado. "
            "Luego podés coordinar una videollamada de 30 minutos por si te quedan dudas."
        ),
    },
    "rito_corazon": {
        "nombre": "Rito del Corazón",
        "grupo": GRUPO_MEET,
        "duracion_min": 90,
        "precio": 30000,
        "min_dias": 7,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a contactar para enviarte el link de Meet. "
            "Antes de la sesión vas a recibir un ebook para leer."
        ),
    },
    "rito_utero": {
        "nombre": "Rito del Útero",
        "grupo": GRUPO_MEET,
        "duracion_min": 90,
        "precio": 30000,
        "min_dias": 7,
        "mensaje_confirmacion": (
            "Unos minutos antes de tu sesión te voy a contactar para enviarte el link de Meet. "
            "Antes de la sesión vas a recibir un ebook para leer."
        ),
    },
}

# Ventanas de atención por grupo. Claves de día: 0=Lunes ... 6=Domingo (datetime.weekday()).
HORARIOS_ATENCION = {
    GRUPO_MEET: {
        0: [("08:30", "12:30")],
        1: [("08:30", "12:30")],
        2: [("08:30", "12:30")],
        3: [("08:30", "12:30")],
        4: [("08:30", "12:30")],
    },
    GRUPO_DISTANCIA: {
        0: [("08:30", "12:30"), ("14:00", "17:00")],
        1: [("08:30", "12:30"), ("14:00", "17:00")],
        2: [("08:30", "12:30"), ("14:00", "17:00")],
        3: [("08:30", "12:30"), ("14:00", "17:00")],
        4: [("08:30", "12:30"), ("14:00", "17:00")],
        6: [("10:00", "13:00")],
    },
    GRUPO_ENTREGA: {
        0: [("08:00", "12:00"), ("14:00", "17:00")],
        1: [("08:00", "12:00"), ("14:00", "17:00")],
        2: [("08:00", "12:00"), ("14:00", "17:00")],
        3: [("08:00", "12:00"), ("14:00", "17:00")],
        4: [("08:00", "12:00"), ("14:00", "17:00")],
        6: [("10:00", "13:00")],
    },
}

DATOS_PAGO = {
    "alias": "ANTOPRATO",
    "banco": "Santander Río",
    "nota_exterior": "Para pagos desde el exterior, consultar cuentas alternativas escribiendo por WhatsApp.",
}

POLITICA_CANCELACION = (
    "Podés cancelar o reprogramar tu turno hasta 24 hs antes de la sesión sin costo. "
    "Pasado ese plazo, la seña no es reembolsable."
)

HORIZONTE_DIAS = 45  # cuántos días hacia adelante se muestran turnos disponibles

NOTIFICACION_EMAIL = "renacer.holistico.sanacion@gmail.com"

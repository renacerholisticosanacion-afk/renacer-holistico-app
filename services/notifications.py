"""Notificación por email de nuevas reservas."""
import smtplib
from email.mime.text import MIMEText


class LocalNotifier:
    """No envía nada de verdad; solo guarda el último mensaje para poder mostrarlo en demo."""

    def __init__(self):
        self.ultimo_enviado = None

    def enviar(self, destinatario, asunto, cuerpo):
        self.ultimo_enviado = {"destinatario": destinatario, "asunto": asunto, "cuerpo": cuerpo}
        return True


class GmailNotifier:
    """Envía el aviso por email real usando una cuenta de Gmail + contraseña de aplicación."""

    def __init__(self, remitente, password_app):
        self.remitente = remitente
        self.password_app = password_app

    def enviar(self, destinatario, asunto, cuerpo):
        msg = MIMEText(cuerpo, "plain", "utf-8")
        msg["Subject"] = asunto
        msg["From"] = self.remitente
        msg["To"] = destinatario
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.remitente, self.password_app)
            server.sendmail(self.remitente, [destinatario], msg.as_string())
        return True

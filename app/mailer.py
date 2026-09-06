"""
Envio de correo transaccional via Gmail SMTP (mirrorlaboral@gmail.com +
App Password de Google, configurados como variables de entorno).
Si las credenciales no estan configuradas (ej. en desarrollo local), el
envio se omite silenciosamente y queda registrado en consola -- para no
bloquear el resto del flujo mientras se prueba.
"""
import smtplib
from email.message import EmailMessage

from app.config import GMAIL_USER, GMAIL_APP_PASSWORD, INTERNAL_ALERT_EMAIL


def enviar_correo(destinatario: str, asunto: str, cuerpo_html: str, adjuntos=None) -> bool:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        print(f"[mailer] Credenciales de Gmail no configuradas -- correo omitido: "
              f"'{asunto}' -> {destinatario}")
        return False

    msg = EmailMessage()
    msg["From"] = f"Mirror Laboral <{GMAIL_USER}>"
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.set_content("Tu cliente de correo no muestra HTML. Escríbenos a mirrorlaboral@gmail.com "
                     "si necesitas este mensaje en otro formato.")
    msg.add_alternative(cuerpo_html, subtype="html")

    for nombre_archivo, contenido in (adjuntos or []):
        msg.add_attachment(
            contenido,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=nombre_archivo,
        )

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as exc:  # nunca tumbar el flujo de pago/documento por un error de correo
        print(f"[mailer] Error enviando correo a {destinatario}: {exc}")
        return False


def alertar_riesgo_interno(contexto: str, email_persona: str, nombre: str = "—") -> None:
    """Alerta interna al equipo cuando se detecta riesgo -- nunca contacta a la persona
    ni a su contacto de confianza de forma automática; solo avisa al equipo para que
    decida los siguientes pasos (protocolo de riesgo, Sistema_Mirror_3_Niveles.md)."""
    destino = INTERNAL_ALERT_EMAIL or GMAIL_USER
    if not destino:
        print(f"[mailer] Riesgo detectado pero no hay correo interno configurado. "
              f"Contexto: {contexto} / persona: {nombre} <{email_persona}>")
        return
    cuerpo = f"""
    <p><strong>Se detectó una señal de riesgo en {contexto}.</strong></p>
    <p>Persona: {nombre} — {email_persona}</p>
    <p>Revisar el caso y decidir los siguientes pasos según el protocolo de riesgo.
    No contactar de forma automática ni al contacto de confianza sin evaluación previa.</p>
    """
    enviar_correo(destino, f"[Alerta de riesgo] {contexto}", cuerpo)

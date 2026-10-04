import os
import smtplib
from email.message import EmailMessage
from html import escape


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "innovaideia2023@gmail.com").strip()
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD", "").replace(" ", "").strip()
LEAD_EMAIL = "innovaideia2023@gmail.com"


def email_config_status():
    """Retorna apenas metadados seguros da configuração de e-mail."""
    return {
        "provider": "gmail_smtp",
        "config_version": "2026-10-04-gmail-v1",
        "smtp_host": SMTP_HOST,
        "smtp_port": SMTP_PORT,
        "smtp_email": SMTP_EMAIL,
        "app_password_configured": bool(SMTP_APP_PASSWORD),
        "lead_email": LEAD_EMAIL,
        "production_sender_ready": bool(SMTP_EMAIL and SMTP_APP_PASSWORD),
    }


def _email_html(nome, email, empresa, telefone, interesse, mensagem, newsletter):
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:680px;margin:auto;color:#222">
      <div style="background:#111827;color:#fff;padding:24px;border-radius:12px 12px 0 0">
        <h2 style="margin:0">🚀 Novo Lead — InNovaIdeia</h2>
        <p style="margin:8px 0 0;color:#cbd5e1">Novo contato recebido pelo site institucional.</p>
      </div>
      <div style="padding:24px;border:1px solid #e5e7eb;border-top:0;border-radius:0 0 12px 12px">
        <p><strong>Nome:</strong> {escape(nome)}</p>
        <p><strong>Empresa:</strong> {escape(empresa) or 'Não informado'}</p>
        <p><strong>E-mail:</strong> {escape(email)}</p>
        <p><strong>Telefone:</strong> {escape(telefone) or 'Não informado'}</p>
        <p><strong>Interesse:</strong> {escape(interesse)}</p>
        <p><strong>Newsletter:</strong> {'Sim' if newsletter else 'Não'}</p>
        <hr>
        <p><strong>Mensagem:</strong></p>
        <p style="white-space:pre-line">{escape(mensagem)}</p>
      </div>
    </div>
    """


def _confirmation_html(nome):
    return f"""
    <div style="font-family:Arial,sans-serif;max-width:680px;margin:auto;color:#222">
      <h2>Olá, {escape(nome)}!</h2>
      <p>Recebemos sua mensagem e agradecemos o contato com a <strong>InNovaIdeia</strong>.</p>
      <p>Nossa equipe avaliará sua solicitação e retornará em até 24 horas úteis.</p>
      <p>Atenciosamente,<br><strong>InNovaIdeia Assessoria em Tecnologia</strong></p>
    </div>
    """


def _send_email(to_email, subject, html, reply_to=None):
    if not SMTP_EMAIL:
        raise RuntimeError("SMTP_EMAIL não configurado.")
    if not SMTP_APP_PASSWORD:
        raise RuntimeError("SMTP_APP_PASSWORD não configurado.")

    msg = EmailMessage()
    msg["From"] = f"InNovaIdeia <{SMTP_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    if reply_to:
        msg["Reply-To"] = reply_to

    msg.set_content("Este e-mail contém conteúdo HTML. Abra em um cliente compatível.")
    msg.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
        smtp.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        smtp.send_message(msg)

    return {"status": "sent", "to": to_email}


def enviar_lead(nome, email, empresa, telefone, interesse, mensagem, newsletter=False):
    """Envia o lead ao Gmail da InNovaIdeia e tenta confirmar ao visitante."""
    lead = _send_email(
        to_email=LEAD_EMAIL,
        subject=f"Novo lead — {interesse} — {nome}",
        html=_email_html(
            nome, email, empresa, telefone, interesse, mensagem, newsletter
        ),
        reply_to=email,
    )

    confirmation = None
    confirmation_error = None

    try:
        confirmation = _send_email(
            to_email=email,
            subject="Recebemos seu contato — InNovaIdeia",
            html=_confirmation_html(nome),
        )
    except Exception as exc:
        confirmation_error = str(exc)

    return {
        "lead": lead,
        "confirmation": confirmation,
        "confirmation_error": confirmation_error,
    }

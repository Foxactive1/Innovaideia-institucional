import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage
from html import escape


GMAIL_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID", "").strip()
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET", "").strip()
GMAIL_REFRESH_TOKEN = os.getenv("GMAIL_REFRESH_TOKEN", "").strip()
GMAIL_SENDER = os.getenv(
    "GMAIL_SENDER", "innovaideia2023@gmail.com"
).strip()
LEAD_EMAIL = "innovaideia2023@gmail.com"

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_SEND_URL = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"


def email_config_status():
    """Retorna apenas metadados seguros da configuração de e-mail."""
    ready = bool(
        GMAIL_CLIENT_ID
        and GMAIL_CLIENT_SECRET
        and GMAIL_REFRESH_TOKEN
        and GMAIL_SENDER
    )
    return {
        "provider": "gmail_api_oauth2",
        "config_version": "2026-10-04-gmail-api-v1",
        "client_id_configured": bool(GMAIL_CLIENT_ID),
        "client_secret_configured": bool(GMAIL_CLIENT_SECRET),
        "refresh_token_configured": bool(GMAIL_REFRESH_TOKEN),
        "gmail_sender": GMAIL_SENDER,
        "lead_email": LEAD_EMAIL,
        "production_sender_ready": ready,
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


def _require_config():
    missing = []
    if not GMAIL_CLIENT_ID:
        missing.append("GMAIL_CLIENT_ID")
    if not GMAIL_CLIENT_SECRET:
        missing.append("GMAIL_CLIENT_SECRET")
    if not GMAIL_REFRESH_TOKEN:
        missing.append("GMAIL_REFRESH_TOKEN")
    if not GMAIL_SENDER:
        missing.append("GMAIL_SENDER")

    if missing:
        raise RuntimeError(
            "Configuração Gmail OAuth ausente: " + ", ".join(missing)
        )


def _get_access_token():
    _require_config()

    payload = urllib.parse.urlencode({
        "client_id": GMAIL_CLIENT_ID,
        "client_secret": GMAIL_CLIENT_SECRET,
        "refresh_token": GMAIL_REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode("utf-8")

    request = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Falha ao renovar token OAuth ({exc.code}): {detail}"
        ) from exc

    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError("Google OAuth não retornou access_token.")

    return access_token


def _build_raw_message(to_email, subject, html, reply_to=None):
    message = EmailMessage()
    message["From"] = f"InNovaIdeia <{GMAIL_SENDER}>"
    message["To"] = to_email
    message["Subject"] = subject
    if reply_to:
        message["Reply-To"] = reply_to

    message.set_content(
        "Este e-mail contém conteúdo HTML. Abra em um cliente compatível."
    )
    message.add_alternative(html, subtype="html")

    return base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")


def _send_email(to_email, subject, html, reply_to=None):
    token = _get_access_token()
    raw_message = _build_raw_message(
        to_email=to_email,
        subject=subject,
        html=html,
        reply_to=reply_to,
    )

    body = json.dumps({"raw": raw_message}).encode("utf-8")
    request = urllib.request.Request(
        GMAIL_SEND_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"Gmail API recusou o envio ({exc.code}): {detail}"
        ) from exc

    return {
        "status": "sent",
        "to": to_email,
        "message_id": result.get("id"),
        "thread_id": result.get("threadId"),
    }


def enviar_lead(nome, email, empresa, telefone, interesse, mensagem, newsletter=False):
    """Envia o lead via Gmail API e tenta confirmar o recebimento ao visitante."""
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

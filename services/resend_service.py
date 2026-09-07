import os
from html import escape

import resend


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "InNovaIdeia <onboarding@resend.dev>")
EMAIL_TO = os.getenv("EMAIL_TO", "innovaideia2023@gmail.com")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY


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


def enviar_lead(nome, email, empresa, telefone, interesse, mensagem, newsletter=False):
    """Envia o lead para a InNovaIdeia e uma confirmação para o visitante."""
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY não configurada.")

    lead = resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [EMAIL_TO],
        "reply_to": email,
        "subject": f"Novo lead — {interesse} — {nome}",
        "html": _email_html(nome, email, empresa, telefone, interesse, mensagem, newsletter),
    })

    confirmation = resend.Emails.send({
        "from": EMAIL_FROM,
        "to": [email],
        "subject": "Recebemos seu contato — InNovaIdeia",
        "html": _confirmation_html(nome),
    })

    return {"lead": lead, "confirmation": confirmation}

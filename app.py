import json
import os
import re
import secrets
import logging

from flask import Flask, render_template, abort, jsonify, request, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from services.email_service import enviar_lead, email_config_status


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

_secret = os.environ.get("SECRET_KEY")
if not _secret:
    _secret = secrets.token_hex(32)
    logger.warning("SECRET_KEY não definida — gerada aleatoriamente.")
app.config["SECRET_KEY"] = _secret
app.config["MAX_CONTENT_LENGTH"] = 64 * 1024  # 64 KB por requisição

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    default_limits=[],
)

DATA_DIR = os.path.join(app.static_folder, "data")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    data = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data


def load_data_or_404(filename, is_jsonl=False):
    data = load_jsonl(filename) if is_jsonl else load_json(filename)
    if data is None or (isinstance(data, list) and len(data) == 0):
        abort(404)
    return data


INDICADORES = load_json("indicadores.json") or []
SERVICOS = load_json("servicos.json") or []
TECNOLOGIAS = load_json("tecnologias.json") or []
PROJETOS = load_json("projetos.json") or []
DEPOIMENTOS = load_json("depoimentos.json") or []
FAQ = load_json("faq.json") or []
EMPRESA = load_json("empresa.json") or {}


def validar_email(email: str) -> bool:
    return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email) is not None


def _email_error_hint(exc: Exception) -> str:
    """Classifica erros comuns do provedor sem expor credenciais."""
    msg = str(exc).lower()

    if "smtp_app_password" in msg or "password not configured" in msg:
        return "smtp_app_password_missing"
    if "smtp_email" in msg:
        return "smtp_email_missing"
    if "username and password not accepted" in msg or "authentication failed" in msg:
        return "smtp_authentication_failed"
    if "application-specific password required" in msg or "app password" in msg:
        return "smtp_app_password_required"
    if "timed out" in msg or "timeout" in msg:
        return "smtp_timeout"
    if "connection refused" in msg:
        return "smtp_connection_refused"
    if "network is unreachable" in msg:
        return "smtp_network_unreachable"
    if "name or service not known" in msg or "getaddrinfo failed" in msg:
        return "smtp_dns_error"
    if "ssl" in exc.__class__.__name__.lower() or "ssl" in msg:
        return "smtp_ssl_error"
    if isinstance(exc, OSError):
        return "smtp_network_error"

    return "smtp_error"


@app.route("/")
def index():
    return render_template(
        "index.html",
        indicadores=INDICADORES,
        servicos=SERVICOS,
        tecnologias=TECNOLOGIAS,
        projetos=PROJETOS,
        depoimentos=DEPOIMENTOS,
        faq=FAQ,
        empresa=EMPRESA,
    )


@app.route("/sobre")
def sobre():
    return render_template("sobre.html", empresa=EMPRESA)


@app.route("/servicos")
def servicos():
    return render_template("servicos.html", servicos=SERVICOS)


@app.route("/projetos")
def projetos():
    return render_template("projetos.html", projetos=PROJETOS)


@app.route("/tecnologias")
def tecnologias():
    return render_template("tecnologias.html", tecnologias=TECNOLOGIAS)


@app.route("/contato")
def contato():
    return render_template("contato.html")


@app.route("/api/indicadores")
def api_indicadores():
    return jsonify(INDICADORES)


@app.route("/api/servicos")
def api_servicos():
    return jsonify(SERVICOS)


@app.route("/api/tecnologias")
def api_tecnologias():
    return jsonify(TECNOLOGIAS)


@app.route("/api/projetos")
def api_projetos():
    return jsonify(PROJETOS)


@app.route("/api/depoimentos")
def api_depoimentos():
    return jsonify(DEPOIMENTOS)


@app.route("/api/faq")
def api_faq():
    return jsonify(FAQ)


@app.route("/api/health")
@limiter.exempt
def api_health():
    return jsonify({
        "status": "ok",
        "service": "innovaideia-institucional",
    }), 200


@app.route("/api/email-health")
@limiter.exempt
def api_email_health():
    return jsonify(email_config_status()), 200


@app.route("/api/contato", methods=["POST"])
@limiter.limit("5 per minute")
def api_contato():
    """Recebe um lead e envia as notificações usando a API do Resend."""
    if not request.is_json:
        return jsonify({"erro": "Content-Type deve ser application/json"}), 415

    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Requisição deve conter JSON válido"}), 400

    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()
    mensagem = str(dados.get("mensagem", "")).strip()
    interesse = str(dados.get("interesse", "Consultoria")).strip() or "Consultoria"
    telefone = str(dados.get("telefone", "")).strip()
    empresa = str(dados.get("empresa", "")).strip()
    newsletter = bool(dados.get("newsletter", False))
    website = str(dados.get("website", "")).strip()

    # Limites defensivos para evitar payloads excessivos e abuso do serviço de e-mail.
    nome = nome[:120]
    email = email[:254]
    telefone = telefone[:40]
    empresa = empresa[:160]
    interesse = interesse[:120]
    mensagem = mensagem[:5000]
    website = website[:255]

    # Honeypot anti-bot: usuários reais não veem nem preenchem este campo.
    # Retornamos sucesso genérico para não revelar a regra de proteção.
    if website:
        logger.warning("Submissão bloqueada pelo honeypot no formulário de contato.")
        return jsonify({
            "mensagem": "Contato registrado e enviado com sucesso!",
            "status": "sent",
        }), 201

    erros = []
    if len(nome) < 2:
        erros.append("Nome deve ter pelo menos 2 caracteres.")
    if not validar_email(email):
        erros.append("E-mail inválido.")
    if len(mensagem) < 20:
        erros.append("Mensagem deve ter pelo menos 20 caracteres.")

    if erros:
        return jsonify({"erro": "; ".join(erros)}), 400

    try:
        resultado = enviar_lead(
            nome=nome,
            email=email,
            empresa=empresa,
            telefone=telefone,
            interesse=interesse,
            mensagem=mensagem,
            newsletter=newsletter,
        )
        logger.info("Lead enviado por e-mail: %s", resultado.get("lead"))
        if resultado.get("confirmation_error"):
            logger.warning("Lead recebido, mas confirmação ao visitante falhou: %s", resultado.get("confirmation_error"))
        return jsonify({
            "mensagem": "Contato registrado e enviado com sucesso!",
            "status": "sent",
        }), 201
    except Exception as exc:
        error_hint = _email_error_hint(exc)
        logger.exception(
            "Falha ao enviar lead por e-mail [%s]: %s",
            error_hint,
            exc,
        )
        safe_detail = str(exc)
        if len(safe_detail) > 180:
            safe_detail = safe_detail[:180] + "..."

        return jsonify({
            "erro": "Não foi possível enviar sua mensagem agora. Tente novamente em instantes.",
            "codigo": error_hint,
            "tipo": exc.__class__.__name__,
            "detalhe": safe_detail,
        }), 502


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(
        app.static_folder,
        "sitemap.xml",
        mimetype="application/xml",
    )


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({
        "erro": "Muitas tentativas em pouco tempo. Aguarde um momento e tente novamente."
    }), 429


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(debug=debug, host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))

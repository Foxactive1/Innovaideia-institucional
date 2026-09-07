import json
import os
import re
import secrets
import logging

from flask import Flask, render_template, abort, jsonify, request, send_from_directory

from services.resend_service import enviar_lead


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


@app.route("/api/contato", methods=["POST"])
def api_contato():
    """Recebe um lead e envia as notificações usando a API do Resend."""
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({"erro": "Requisição deve conter JSON válido"}), 400

    nome = str(dados.get("nome", "")).strip()
    email = str(dados.get("email", "")).strip()
    mensagem = str(dados.get("mensagem", "")).strip()
    interesse = str(dados.get("interesse", "Consultoria")).strip() or "Consultoria"
    telefone = str(dados.get("telefone", "")).strip()
    empresa = str(dados.get("empresa", "")).strip()
    newsletter = bool(dados.get("newsletter", False))

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
        logger.info("Lead enviado pelo Resend: %s", resultado.get("lead"))
        return jsonify({
            "mensagem": "Contato registrado e enviado com sucesso!",
            "status": "sent",
        }), 201
    except Exception as exc:
        logger.exception("Falha ao enviar lead pelo Resend")
        return jsonify({
            "erro": "Não foi possível enviar sua mensagem agora. Tente novamente em instantes."
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


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

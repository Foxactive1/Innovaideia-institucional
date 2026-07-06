import json
import os
import re
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from html import escape

from flask import Flask, render_template, abort, jsonify, request, send_from_directory

# ── Configurações de e-mail (via variáveis de ambiente) ─
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")          # obrigatório para enviar e-mail
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # obrigatório para enviar e-mail
EMAIL_TO = os.getenv("EMAIL_TO", "innovaideia2023@gmail.com")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializa a aplicação
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Caminho da pasta de dados
DATA_DIR = os.path.join(app.static_folder, 'data')

# ── Funções auxiliares para carregar dados ──────────────

def load_json(filename):
    """Carrega um arquivo JSON."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_jsonl(filename):
    """Carrega um arquivo JSONL (cada linha um JSON) e retorna uma lista."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append(json.loads(line))
    return data

def load_data_or_404(filename, is_jsonl=False):
    """Carrega dados ou retorna 404 se o arquivo não existir."""
    if is_jsonl:
        data = load_jsonl(filename)
    else:
        data = load_json(filename)
    if data is None or (isinstance(data, list) and len(data) == 0):
        abort(404)
    return data

# ── Carrega todos os dados ao iniciar (cache) ──────────

INDICADORES = load_json('indicadores.json') or []
SERVICOS = load_json('servicos.json') or []
TECNOLOGIAS = load_json('tecnologias.json') or []
PROJETOS = load_json('projetos.json') or []
DEPOIMENTOS = load_json('depoimentos.json') or []
FAQ = load_json('faq.json') or []
EMPRESA = load_json('empresa.json') or {}

# ── Funções auxiliares de e-mail (formulário de contato) ─

def validar_email(email: str) -> bool:
    """Valida o formato básico de um endereço de e-mail."""
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email) is not None

def _enviar_email_smtp(nome: str, email: str, telefone: str,
                        interesse: str, mensagem: str, newsletter: bool) -> bool:
    """Conecta ao servidor SMTP e envia o e-mail de contato."""
    corpo = f"""
    <h2>Novo contato via site</h2>
    <p><strong>Nome:</strong> {escape(nome)}</p>
    <p><strong>E-mail:</strong> {escape(email)}</p>
    <p><strong>Telefone:</strong> {escape(telefone) or 'Não informado'}</p>
    <p><strong>Interesse:</strong> {escape(interesse)}</p>
    <p><strong>Newsletter:</strong> {'Sim' if newsletter else 'Não'}</p>
    <p><strong>Mensagem:</strong><br>{escape(mensagem)}</p>
    """

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = f"Novo contato - {interesse}"
    msg.attach(MIMEText(corpo, 'html'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
    return True

def enviar_email_async(app_obj, nome, email, telefone, interesse, mensagem, newsletter):
    """Dispara o envio de e-mail em uma thread separada, com contexto da app."""
    with app_obj.app_context():
        try:
            _enviar_email_smtp(nome, email, telefone, interesse, mensagem, newsletter)
            logger.info(f"E-mail de contato enviado para {EMAIL_TO}")
        except Exception as e:
            logger.error(f"Falha no envio do e-mail: {str(e)}")

# ── Rotas da aplicação ──────────────────────────────────

@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html',
                           indicadores=INDICADORES,
                           servicos=SERVICOS,
                           tecnologias=TECNOLOGIAS,
                           projetos=PROJETOS,
                           depoimentos=DEPOIMENTOS,
                           faq=FAQ,
                           empresa=EMPRESA)

@app.route('/sobre')
def sobre():
    """Página 'Sobre'."""
    return render_template('sobre.html', empresa=EMPRESA)

@app.route('/servicos')
def servicos():
    """Página de serviços."""
    return render_template('servicos.html', servicos=SERVICOS)

@app.route('/projetos')
def projetos():
    """Página de projetos."""
    return render_template('projetos.html', projetos=PROJETOS)

@app.route('/tecnologias')
def tecnologias():
    """Página de tecnologias."""
    return render_template('tecnologias.html', tecnologias=TECNOLOGIAS)

@app.route('/contato')
def contato():
    """Página de contato."""
    return render_template('contato.html')

# ── Rotas para API (opcional) ──────────────────────────

@app.route('/api/indicadores')
def api_indicadores():
    return jsonify(INDICADORES)

@app.route('/api/servicos')
def api_servicos():
    return jsonify(SERVICOS)

@app.route('/api/tecnologias')
def api_tecnologias():
    return jsonify(TECNOLOGIAS)

@app.route('/api/projetos')
def api_projetos():
    return jsonify(PROJETOS)

@app.route('/api/depoimentos')
def api_depoimentos():
    return jsonify(DEPOIMENTOS)

@app.route('/api/faq')
def api_faq():
    return jsonify(FAQ)

@app.route('/api/contato', methods=['POST'])
def api_contato():
    """Recebe os dados do formulário de contato, valida e envia por e-mail."""
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'Requisição deve conter JSON válido'}), 400

    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip()
    mensagem = dados.get('mensagem', '').strip()
    interesse = dados.get('interesse', 'Consultoria').strip()
    telefone = dados.get('telefone', '').strip()
    newsletter = bool(dados.get('newsletter', False))

    erros = []
    if len(nome) < 2:
        erros.append('Nome deve ter pelo menos 2 caracteres.')
    if not validar_email(email):
        erros.append('E-mail inválido.')
    if len(mensagem) < 20:
        erros.append('Mensagem deve ter pelo menos 20 caracteres.')

    if erros:
        return jsonify({'erro': '; '.join(erros)}), 400

    if SMTP_USER and SMTP_PASSWORD:
        Thread(
            target=enviar_email_async,
            args=(app, nome, email, telefone, interesse, mensagem, newsletter)
        ).start()
    else:
        logger.warning("Credenciais SMTP não configuradas – e-mail não enviado.")

    return jsonify({'mensagem': 'Contato registrado com sucesso!'}), 201

# ── Tratamento de erros ──────────────────────────────────

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ── Inicialização ────────────────────────────────────────

if __name__ == '__main__':
    # Em desenvolvimento, ativa o debug e recarrega automático
    app.run(debug=True, host='0.0.0.0', port=5000)

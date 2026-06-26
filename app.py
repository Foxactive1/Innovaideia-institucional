import os
import re
import sqlite3
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread
from html import escape

from flask import Flask, request, jsonify
from flask_cors import CORS

# ================= CONFIGURAÇÕES (via variáveis de ambiente) =================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")          # obrigatório
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # obrigatório
EMAIL_TO = os.getenv("EMAIL_TO", "innovaideia2023@gmail.com")
DB_PATH = os.getenv("DB_PATH", "contatos.db")
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================= INICIALIZAÇÃO DO APP =================
app = Flask(__name__)
CORS(app)  # Permite requisições do frontend (ajuste origins em produção)

# ================= BANCO DE DADOS =================
def init_db():
    """Cria a tabela se não existir (thread‑safe para SQLite em modo WAL)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                telefone TEXT,
                interesse TEXT,
                mensagem TEXT NOT NULL,
                newsletter INTEGER DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    finally:
        conn.close()

init_db()

# ================= FUNÇÕES AUXILIARES =================
def validar_email(email: str) -> bool:
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email) is not None

def _enviar_email_smtp(nome: str, email: str, telefone: str,
                       interesse: str, mensagem: str, newsletter: bool) -> bool:
    """Função interna síncrona que realmente conecta ao SMTP."""
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
    """Dispara o envio de e‑mail em uma thread separada, com contexto da app."""
    with app_obj.app_context():
        try:
            _enviar_email_smtp(nome, email, telefone, interesse, mensagem, newsletter)
            logger.info(f"E‑mail de contato enviado para {EMAIL_TO}")
        except Exception as e:
            logger.error(f"Falha no envio do e‑mail: {str(e)}")

def salvar_contato(dados: dict):
    """Persiste os dados do formulário no SQLite."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('''
            INSERT INTO contatos (nome, email, telefone, interesse, mensagem, newsletter)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            dados['nome'],
            dados['email'],
            dados.get('telefone', ''),
            dados['interesse'],
            dados['mensagem'],
            1 if dados.get('newsletter') else 0
        ))
        conn.commit()
    finally:
        conn.close()

# ================= ROTAS =================
@app.route('/api/contact', methods=['POST'])
def contact():
    """Recebe os dados do formulário, valida, salva e notifica por e‑mail."""
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'Requisição deve conter JSON válido'}), 400

    # Extração e limpeza
    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip()
    mensagem = dados.get('mensagem', '').strip()
    interesse = dados.get('interesse', 'Consultoria').strip()
    telefone = dados.get('telefone', '').strip()
    newsletter = bool(dados.get('newsletter', False))

    # Validações
    erros = []
    if len(nome) < 2:
        erros.append('Nome deve ter pelo menos 2 caracteres.')
    if not validar_email(email):
        erros.append('E‑mail inválido.')
    if len(mensagem) < 20:
        erros.append('Mensagem deve ter pelo menos 20 caracteres.')

    if erros:
        return jsonify({'erro': '; '.join(erros)}), 400

    # Persistência (síncrona para garantir integridade)
    try:
        salvar_contato({
            'nome': nome,
            'email': email,
            'telefone': telefone,
            'interesse': interesse,
            'mensagem': mensagem,
            'newsletter': newsletter
        })
    except Exception as e:
        logger.error(f"Erro ao salvar contato: {str(e)}")
        return jsonify({'erro': 'Erro interno ao salvar os dados.'}), 500

    # Envio de e‑mail em background (não bloqueante)
    if SMTP_USER and SMTP_PASSWORD:
        Thread(
            target=enviar_email_async,
            args=(app, nome, email, telefone, interesse, mensagem, newsletter)
        ).start()
    else:
        logger.warning("Credenciais SMTP não configuradas – e‑mail não enviado.")

    return jsonify({'mensagem': 'Contato registrado com sucesso!'}), 201

@app.route('/')
def index():
    return "API da InNovaIdeia funcionando!"

# ================= EXECUÇÃO =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)

import os
import re
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend

# ================= CONFIGURAÇÕES =================
# Substitua pelos seus dados:
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu-email@gmail.com"
SMTP_PASSWORD = "sua-senha-ou-app-password"
EMAIL_TO = "innovaideia2023@gmail.com"

DB_PATH = "contatos.db"

# ================= BANCO DE DADOS =================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
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
    conn.close()

init_db()

# ================= FUNÇÕES AUXILIARES =================
def validar_email(email):
    return re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email) is not None

def enviar_email(nome, email, telefone, interesse, mensagem, newsletter):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = f"Novo contato - {interesse}"

        corpo = f"""
        <h2>Novo contato via site</h2>
        <p><strong>Nome:</strong> {nome}</p>
        <p><strong>E-mail:</strong> {email}</p>
        <p><strong>Telefone:</strong> {telefone or 'Não informado'}</p>
        <p><strong>Interesse:</strong> {interesse}</p>
        <p><strong>Newsletter:</strong> {'Sim' if newsletter else 'Não'}</p>
        <p><strong>Mensagem:</strong><br>{mensagem}</p>
        """

        msg.attach(MIMEText(corpo, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def salvar_contato(dados):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
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
    conn.close()

# ================= ROTA PRINCIPAL =================
@app.route('/api/contact', methods=['POST'])
def contact():
    dados = request.get_json()

    # Validações básicas
    if not dados:
        return jsonify({'erro': 'Dados não enviados'}), 400

    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip()
    mensagem = dados.get('mensagem', '').strip()
    interesse = dados.get('interesse', 'Consultoria')
    telefone = dados.get('telefone', '').strip()
    newsletter = dados.get('newsletter', False)

    if len(nome) < 2:
        return jsonify({'erro': 'Nome deve ter pelo menos 2 caracteres'}), 400
    if not validar_email(email):
        return jsonify({'erro': 'E-mail inválido'}), 400
    if len(mensagem) < 20:
        return jsonify({'erro': 'Mensagem deve ter pelo menos 20 caracteres'}), 400

    # Salvar no banco
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
        return jsonify({'erro': f'Erro ao salvar: {str(e)}'}), 500

    # Enviar e-mail (opcional, pode falhar mas não impede o cadastro)
    enviar_email(nome, email, telefone, interesse, mensagem, newsletter)

    return jsonify({'mensagem': 'Contato registrado com sucesso!'}), 201

# ================= ROTA DE TESTE =================
@app.route('/')
def index():
    return "API da InNovaIdeia funcionando!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

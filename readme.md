# InNovaIdeia — Site Institucional ®

Site institucional da **InNovaIdeia Assessoria em Tecnologia**, desenvolvido com **Flask** e arquitetura baseada em dados JSON para fácil manutenção e escalabilidade.

---

## 🚀 Tecnologias

- **Backend:** Flask 3.x (Python 3.9+)
- **Frontend:** Bootstrap 5, CSS customizado (variáveis, grid, animações), JavaScript nativo
- **Dados:** JSON (arquivos estáticos em `static/data/`)
- **E-mail:** Resend API (`resend` SDK), com envio do lead e confirmação automática ao visitante
- **Proteção anti-abuso:** Flask-Limiter no endpoint de contato + honeypot anti-bot invisível
- **Deploy:** Vercel (runtime Python serverless)

---

## 📁 Estrutura do Projeto

```
innovaideia-institucional/
├── app.py                      # Servidor Flask (rotas, API, envio de e-mail)
├── requirements.txt            # Dependências Python
├── vercel.json                 # Configuração de deploy na Vercel
├── services/
│   └── resend_service.py       # Integração com Resend para leads e confirmações
├── readme.md                   # Documentação do projeto
│
├── templates/                  # Páginas Jinja2 (nome em minúsculas — obrigatório no Linux)
│   ├── base.html
│   ├── index.html
│   ├── sobre.html
│   ├── servicos.html
│   ├── projetos.html
│   ├── tecnologias.html
│   ├── contato.html
│   ├── 404.html
│   ├── 500.html
│   └── components/              # Componentes reutilizáveis (includes)
│       ├── navbar.html
│       ├── hero.html
│       ├── indicadores.html
│       ├── empresa.html
│       ├── servicos_cards.html
│       ├── solucoes.html
│       ├── tecnologias_grid.html
│       ├── projetos_cards.html
│       ├── processo.html
│       ├── diferenciais.html
│       ├── depoimentos.html
│       ├── faq.html
│       ├── cta.html
│       ├── contato_form.html
│       ├── page_header.html
│       ├── timeline.html
│       └── footer.html
│
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   ├── app.js               # Navbar, scroll, animações
    │   └── contact.js           # Validação e envio do formulário
    └── data/                    # Conteúdo editável do site (sem tocar em código)
        ├── empresa.json
        ├── indicadores.json
        ├── servicos.json
        ├── projetos.json
        ├── tecnologias.json
        ├── depoimentos.json
        └── faq.json
```

> ⚠️ **Importante:** a pasta de templates deve se chamar `templates` (minúsculo). O Flask procura por esse nome exato via `render_template()`, e em qualquer host Linux (Vercel, Fly.io, Railway) o filesystem é case-sensitive — uma pasta `Templates` com T maiúsculo quebra o carregamento das páginas em produção, mesmo que funcione localmente no Windows/Termux.

---

## 🔧 Pré-requisitos

- Python 3.9 ou superior
- pip
- Git (opcional, para clonar)

---

## 📦 Instalação e Execução Local

1. Clone o repositório:
   ```bash
   git clone https://github.com/Foxactive1/Innovaideia-institucional.git
   cd Innovaideia-institucional
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac/Termux
   venv\Scripts\activate         # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente (formulário de contato):
   ```bash
   export SECRET_KEY="chave-secreta-aleatoria"
   export RESEND_API_KEY="re_xxxxxxxxx"
   export EMAIL_FROM="InNovaIdeia <contato@seudominio.com>"
   export EMAIL_TO="innovaideia2023@gmail.com"
   ```
   `RESEND_API_KEY` é obrigatória para o envio. `EMAIL_FROM` é opcional e deve usar um remetente/domínio autorizado no Resend. `EMAIL_TO` é opcional e, se omitida, usa `innovaideia2023@gmail.com`.

5. Execute o servidor:
   ```bash
   python app.py
   ```

6. Acesse `http://localhost:5000`.

---

## 🌐 Deploy na Vercel (recomendado)

Este projeto atualmente é stateless para persistência de negócio (sem banco de dados). O formulário envia os contatos pela API do Resend, e a Vercel com runtime Python serverless continua sendo uma opção simples para o deploy:

1. Garanta que `requirements.txt` e `vercel.json` estão na raiz (ambos incluídos neste repositório).
2. No painel da Vercel, importe o repositório do GitHub.
3. Em **Settings → Environment Variables**, adicione:
   - `SECRET_KEY`
   - `RESEND_API_KEY`
   - `EMAIL_FROM` (opcional; use um remetente autorizado no Resend)
   - `EMAIL_TO` (opcional; padrão: `innovaideia2023@gmail.com`)
   - `RATELIMIT_STORAGE_URI` (opcional; padrão: `memory://`)
4. Deploy automático a cada push na branch `main`.

O endpoint `POST /api/contato` aceita no máximo **5 requisições por minuto por origem**, reduzindo abuso e spam. O formulário também possui um **honeypot anti-bot**: visitantes reais não veem o campo, enquanto submissões automatizadas que o preenchem são descartadas sem disparar e-mails. Sem `RATELIMIT_STORAGE_URI`, o controle usa memória local da instância; em ambientes serverless isso funciona como uma primeira camada de proteção, mas não é um contador global entre todas as instâncias.

> O `vercel.json` deste repositório usa `@vercel/python` apontando para `app.py` — a versão anterior usava `@vercel/static` apontando para um `index.html` na raiz que não existe (o arquivo real fica em `templates/index.html`), o que fazia o build falhar antes mesmo de rodar o Flask.

### Alternativa: Fly.io

Só faz sentido se o projeto passar a persistir dados (ex: salvar contatos em SQLite/Postgres). Nesse caso é necessário:
- Criar o `Dockerfile` referenciado em `fly.toml` (ainda não existe no repositório).
- Ajustar o `app.py` para de fato gravar em `DB_PATH`, hoje configurado no `fly.toml` mas não utilizado no código.

---

## 🛠 Personalização

**Conteúdo:** edite os arquivos em `static/data/*.json` e reinicie o servidor (ou aguarde o redeploy). Não requer alteração de código:
- `empresa.json` – missão, visão, valores
- `indicadores.json` – números (projetos, clientes, etc.)
- `servicos.json` – lista de serviços
- `projetos.json` – portfólio
- `tecnologias.json` – stack técnica
- `depoimentos.json` – depoimentos de clientes
- `faq.json` – perguntas frequentes

**Estilos:** `static/css/style.css`, organizado com variáveis CSS (`:root`) para cores, fontes e espaçamentos.

**JavaScript:** `static/js/app.js` (navbar, scroll, animações) e `static/js/contact.js` (validação do formulário).

---

## 📞 Contato

- E-mail: innovaideia2023@gmail.com
- GitHub: [github.com/Foxactive1](https://github.com/Foxactive1)
- LinkedIn: Dione Castro Alves

---

## 📄 Licença

© 2026 InNovaIdeia Assessoria em Tecnologia. Todos os direitos reservados. Uso interno da empresa — não reproduzir ou distribuir sem autorização prévia.

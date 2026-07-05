# InNovaIdeia — Site Institucional

Site institucional da InNovaIdeia Assessoria em Tecnologia, desenvolvido com **Flask** e arquitetura baseada em dados JSON/JSONL para fácil manutenção e escalabilidade.

---

## 🚀 Tecnologias

- **Backend:** Flask (Python 3.9+)
- **Frontend:** Bootstrap 5, CSS customizado (variáveis, grid, animações), JavaScript nativo
- **Dados:** JSON e JSONL (armazenamento em arquivos)
- **Fontes:** IBM Plex Mono + IBM Plex Sans (Google Fonts)
- **Ícones:** Font Awesome 6
- **Ambiente:** Python-dotenv (gerenciamento de variáveis)

---

## 📁 Estrutura do Projeto

```

innovaideia-site/
├── app.py                      # Servidor Flask (rotas, carregamento de dados)
├── requirements.txt            # Dependências Python
├── .env                        # Variáveis de ambiente (não versionado)
├── README.md                   # Este arquivo
│
├── templates/                  # Páginas Jinja2
│   ├── base.html               # Layout base
│   ├── index.html              # Página inicial (agrega todos os componentes)
│   ├── sobre.html
│   ├── servicos.html
│   ├── projetos.html
│   ├── tecnologias.html
│   ├── contato.html
│   └── components/             # Componentes reutilizáveis
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
│       └── footer.html
│
├── static/
│   ├── css/
│   │   ├── style.css           # Estilos principais (consolidado)
│   │   └── (outros arquivos .css)
│   ├── js/
│   │   ├── app.js              # Inicialização, scroll, navbar, animações
│   │   ├── contact.js          # Validação e envio do formulário
│   │   └── (demais scripts)
│   ├── data/                   # Dados em JSON/JSONL (editáveis)
│   │   ├── empresa.json
│   │   ├── indicadores.json
│   │   ├── servicos.json
│   │   ├── projetos.json
│   │   ├── tecnologias.json
│   │   ├── depoimentos.json
│   │   ├── faq.json
│   │   └── ... (outros .jsonl)
│   ├── img/                    # Imagens e logos
│   └── fonts/                  # Fontes locais (se houver)
│
├── assets/                     # Arquivos de design (mockups, banners, etc.)
├── docs/                       # Documentação técnica
└── scripts/                    # Scripts auxiliares (validação, otimização)

```

---

## 🔧 Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes)
- Git (opcional, para clonar)

---

## 📦 Instalação e Execução

1. **Clone o repositório** (ou baixe os arquivos):
   ```bash
   git clone https://github.com/seu-usuario/innovaideia-site.git
   cd innovaideia-site
```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure as variáveis de ambiente:
   · Copie o arquivo .env.example para .env (se existir) ou crie um manualmente:
     ```bash
     echo "SECRET_KEY=chave-secreta-aleatoria" > .env
     echo "DEBUG=True" >> .env
     ```
   · Ajuste a SECRET_KEY para um valor único em produção.
5. Execute o servidor:
   ```bash
   python app.py
   ```
6. Acesse http://localhost:5000 no navegador.

---

🛠 Personalização

Conteúdo (textos, serviços, projetos, etc.)

Todos os dados estão em arquivos JSON (ou JSONL) dentro de static/data/. Basta editar qualquer um deles e reiniciar o servidor (ou recarregar a página) para ver as alterações.

· empresa.json – missão, visão, valores
· indicadores.json – números (projetos, clientes, etc.)
· servicos.json – lista de serviços (título, descrição, ícone)
· projetos.json – portfólio com tags
· tecnologias.json – stack técnica (nome, ícone)
· depoimentos.json – depoimentos de clientes
· faq.json – perguntas frequentes

Dica: Para listas de objetos, use o formato JSONL (cada linha um objeto). O Flask carrega ambos os formatos.

Estilos (CSS)

Edite static/css/style.css. O arquivo está organizado com variáveis CSS (:root) para cores, fontes e espaçamentos. Altere as variáveis para modificar a identidade visual globalmente.

JavaScript

Os scripts estão em static/js/. O arquivo app.js contém a lógica de inicialização (navbar, scroll, animações). contact.js gerencia o envio do formulário de contato (com validação básica).

---

🌐 Deploy (Produção)

Para colocar o site no ar, recomenda-se:

1. Desativar o modo DEBUG – no .env, defina DEBUG=False.
2. Usar um servidor WSGI (ex: Gunicorn) em vez do servidor embutido do Flask.
3. Configurar um proxy reverso (Nginx, Apache) para servir arquivos estáticos e rotear requisições.
4. Definir uma SECRET_KEY forte e única (nunca versionada).
5. Servir os dados a partir de um local fora de static/ (por segurança).

Exemplo de comando com Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

🤝 Contribuição

Contribuições são bem-vindas! Para sugerir melhorias:

1. Faça um fork do projeto.
2. Crie uma branch para sua feature (git checkout -b feature/nova-feature).
3. Commit suas alterações (git commit -m 'Adiciona nova feature').
4. Push para a branch (git push origin feature/nova-feature).
5. Abra um Pull Request.

---

📄 Licença

© 2026 InNovaIdeia Assessoria em Tecnologia. Todos os direitos reservados.

Este projeto é de uso interno da empresa e não pode ser reproduzido ou distribuído sem autorização prévia.

---

📞 Contato

· Site: innovaideia.com.br
· E-mail: innovaideia2023@gmail.com
· WhatsApp: (16) 99311-7529
· GitHub: github.com/Foxactive1

---

🧪 Scripts Úteis

· Validar arquivos JSONL:
    python scripts/validate_jsonl.py static/data/
· Otimizar imagens:
    python scripts/optimize_images.py assets/img/
· Build de assets:
    python scripts/build_assets.py

```

---

## Principais melhorias

| Seção                 | Antes             | Depois                                                                 |
|-----------------------|-------------------|------------------------------------------------------------------------|
| **Tecnologias**       | Não listado       | Lista completa com versões                                             |
| **Estrutura**         | Apenas 3 linhas   | Árvore detalhada com todos os diretórios                               |
| **Instalação**        | Apenas 2 comandos | Passos com ambiente virtual, variáveis de ambiente, dicas de segurança |
| **Personalização**    | "Edite os JSONs"  | Explicação de cada arquivo e formato (JSON vs JSONL)                   |
| **Deploy**            | Ausente           | Orientações claras para produção                                       |
| **Scripts auxiliares**| Não mencionados   | Listados na seção final                                                |
| **Contato**           | Não existia       | Adicionado com todos os canais                                         |
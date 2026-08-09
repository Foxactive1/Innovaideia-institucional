"""
Testes básicos do site institucional InNovaIdeia.
Cobre rotas HTML, endpoints de API e validação do formulário de contato.
"""
import json
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    """Cliente de teste com modo de teste ativado."""
    flask_app.config['TESTING'] = True
    flask_app.config['SECRET_KEY'] = 'test-secret-key'
    with flask_app.test_client() as c:
        yield c


# ── Rotas HTML ─────────────────────────────────────────

def test_index_ok(client):
    r = client.get('/')
    assert r.status_code == 200
    assert b'InNovaIdeia' in r.data


def test_sobre_ok(client):
    r = client.get('/sobre')
    assert r.status_code == 200


def test_servicos_ok(client):
    r = client.get('/servicos')
    assert r.status_code == 200


def test_projetos_ok(client):
    r = client.get('/projetos')
    assert r.status_code == 200


def test_tecnologias_ok(client):
    r = client.get('/tecnologias')
    assert r.status_code == 200


def test_contato_ok(client):
    r = client.get('/contato')
    assert r.status_code == 200


def test_404_page(client):
    r = client.get('/pagina-que-nao-existe')
    assert r.status_code == 404


# ── SEO / arquivos estáticos ───────────────────────────

def test_robots_txt(client):
    r = client.get('/robots.txt')
    assert r.status_code == 200
    assert b'User-agent' in r.data


def test_sitemap_xml(client):
    r = client.get('/sitemap.xml')
    assert r.status_code == 200
    assert b'urlset' in r.data


# ── APIs GET ───────────────────────────────────────────

@pytest.mark.parametrize('endpoint', [
    '/api/indicadores',
    '/api/servicos',
    '/api/tecnologias',
    '/api/projetos',
    '/api/depoimentos',
    '/api/faq',
])
def test_api_get_ok(client, endpoint):
    r = client.get(endpoint)
    assert r.status_code == 200
    data = json.loads(r.data)
    assert isinstance(data, list)
    assert len(data) > 0


# ── API /api/contato (POST) ────────────────────────────

def _payload(**kwargs):
    base = {
        'nome': 'Dione Castro Alves',
        'email': 'innovaideia2023@gmail.com',
        'telefone': '(16) 99311-7529',
        'mensagem': 'Mensagem de teste com mais de vinte caracteres.',
        'interesse': 'Consultoria',
        'empresa': 'InNovaIdeia',
        'newsletter': False,
    }
    base.update(kwargs)
    return base


def test_contato_payload_valido(client):
    r = client.post(
        '/api/contato',
        data=json.dumps(_payload()),
        content_type='application/json'
    )
    assert r.status_code == 201
    data = json.loads(r.data)
    assert 'mensagem' in data


def test_contato_sem_body(client):
    r = client.post('/api/contato')
    assert r.status_code == 400


def test_contato_email_invalido(client):
    r = client.post(
        '/api/contato',
        data=json.dumps(_payload(email='nao-e-um-email')),
        content_type='application/json'
    )
    assert r.status_code == 400
    assert 'erro' in json.loads(r.data)


def test_contato_nome_curto(client):
    r = client.post(
        '/api/contato',
        data=json.dumps(_payload(nome='X')),
        content_type='application/json'
    )
    assert r.status_code == 400


def test_contato_mensagem_curta(client):
    r = client.post(
        '/api/contato',
        data=json.dumps(_payload(mensagem='Curta')),
        content_type='application/json'
    )
    assert r.status_code == 400

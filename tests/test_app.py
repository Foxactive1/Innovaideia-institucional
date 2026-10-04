import pytest

import app as app_module


@pytest.fixture
def client(monkeypatch):
    app_module.app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
    )

    def fake_enviar_lead(**kwargs):
        return {
            "lead": {"id": "test-lead"},
            "confirmation": {"id": "test-confirmation"},
            "confirmation_error": None,
        }

    monkeypatch.setattr(app_module, "enviar_lead", fake_enviar_lead)

    with app_module.app.test_client() as client:
        yield client


def payload(**overrides):
    data = {
        "nome": "Cliente Teste",
        "email": "cliente@example.com",
        "telefone": "(16) 99999-9999",
        "empresa": "Empresa Teste",
        "interesse": "Consultoria",
        "mensagem": "Mensagem valida para testar o formulario de contato.",
        "newsletter": False,
        "website": "",
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize("route", [
    "/",
    "/sobre",
    "/servicos",
    "/projetos",
    "/tecnologias",
    "/contato",
])
def test_paginas_publicas(client, route):
    assert client.get(route).status_code == 200


@pytest.mark.parametrize("route", [
    "/api/indicadores",
    "/api/servicos",
    "/api/tecnologias",
    "/api/projetos",
    "/api/depoimentos",
    "/api/faq",
])
def test_apis_publicas(client, route):
    response = client.get(route)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_healthcheck(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_contato_valido(client):
    response = client.post("/api/contato", json=payload())
    assert response.status_code == 201
    assert response.get_json()["status"] == "sent"


def test_contato_email_invalido(client):
    response = client.post("/api/contato", json=payload(email="invalido"))
    assert response.status_code == 400


def test_contato_mensagem_curta(client):
    response = client.post("/api/contato", json=payload(mensagem="curta"))
    assert response.status_code == 400


def test_contato_content_type_invalido(client):
    response = client.post("/api/contato", data="texto")
    assert response.status_code == 415


def test_honeypot_descarta_sem_email(client, monkeypatch):
    chamado = False

    def nao_deveria_enviar(**kwargs):
        nonlocal chamado
        chamado = True
        return {}

    monkeypatch.setattr(app_module, "enviar_lead", nao_deveria_enviar)
    response = client.post("/api/contato", json=payload(website="https://spam.example"))

    assert response.status_code == 201
    assert chamado is False

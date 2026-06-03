"""Tests for the stateless CardForge proxy."""


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert "client_id_configured" in body
    assert "client_secret_configured" in body


def test_exchange_requires_code(client):
    resp = client.post("/auth/github/exchange", json={})
    assert resp.status_code == 400


def test_render_pdf_requires_project(client):
    resp = client.post("/render/pdf", json={})
    assert resp.status_code == 400

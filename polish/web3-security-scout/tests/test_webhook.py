"""Tests for PR reviewer webhook (HMAC + rate limiting)."""

import os
import hashlib
import hmac
import pytest
from fastapi.testclient import TestClient
from webhook import app

client = TestClient(app)

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_invalid_signature():
    payload = b'{"test":"data"}'
    headers = {"X-Hub-Signature-256": "sha256=invalid", "X-GitHub-Event": "pull_request"}
    resp = client.post("/hooks/github", content=payload, headers=headers)
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid signature"

def test_valid_signature():
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "testsecret")
    payload = b'{"pull_request":{"number":1,"html_url":"https://github.com/example/repo/pull/1"}}'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": f"sha256={signature}", "X-GitHub-Event": "pull_request"}
    resp = client.post("/hooks/github", content=payload, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "received"

def test_rate_limiting():
    # Send many requests to exceed limit
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "testsecret")
    payload = b'{"pull_request":{"number":1}}'
    signature = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    headers = {"X-Hub-Signature-256": f"sha256={signature}", "X-GitHub-Event": "pull_request"}
    for _ in range(15):
        resp = client.post("/hooks/github", content=payload, headers=headers)
    # After enough, should be 429
    resp = client.post("/hooks/github", content=payload, headers=headers)
    assert resp.status_code == 429

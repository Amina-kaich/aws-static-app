"""
Tests unitaires pour la Lambda handler.
Lancer avec : python -m pytest test_handler.py -v
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/lambda_functions")

from lambda_functions.handler import lambda_handler


def _make_event(method="GET", path="/health", body=None):
    return {
        "httpMethod": method,
        "path": path,
        "body": json.dumps(body) if body else None
    }


def test_health_check():
    event = _make_event("GET", "/health")
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "ok"


def test_contact_success():
    event = _make_event("POST", "/contact", {
        "name": "Test User",
        "email": "test@example.com",
        "message": "Bonjour"
    })
    response = lambda_handler(event, {})
    assert response["statusCode"] == 201


def test_contact_missing_fields():
    event = _make_event("POST", "/contact", {"name": "Test"})
    response = lambda_handler(event, {})
    assert response["statusCode"] == 400


def test_unknown_route():
    event = _make_event("GET", "/unknown")
    response = lambda_handler(event, {})
    assert response["statusCode"] == 404


def test_cors_preflight():
    event = _make_event("OPTIONS", "/contact")
    response = lambda_handler(event, {})
    assert response["statusCode"] == 200
    assert "Access-Control-Allow-Origin" in response["headers"]


if __name__ == "__main__":
    test_health_check()
    test_contact_success()
    test_contact_missing_fields()
    test_unknown_route()
    test_cors_preflight()
    print("✅ Tous les tests sont passés !")

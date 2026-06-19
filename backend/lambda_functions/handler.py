"""
Lambda Function — API Handler
Architecture: API Gateway → Lambda → (DynamoDB / external services)

Cette fonction gère les requêtes REST envoyées via API Gateway.
Exemple d'usage : endpoint de contact, compteur de visites, ou
proxy vers un service externe.

Déploiement :
    aws lambda create-function \
        --function-name visitorHandler \
        --runtime python3.12 \
        --role arn:aws:iam::<ACCOUNT_ID>:role/lambda-execution-role \
        --handler handler.lambda_handler \
        --zip-file fileb://function.zip
"""

import json
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Headers CORS — nécessaires car le front est servi depuis un domaine
# CloudFront différent de l'API Gateway
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
}


def lambda_handler(event, context):
    """
    Point d'entrée principal de la Lambda.

    `event` contient les détails de la requête HTTP transmise par API Gateway
    (méthode, path, query params, body, headers...).
    """
    logger.info("Event reçu : %s", json.dumps(event))

    http_method = event.get("httpMethod", "GET")
    path = event.get("path", "/")

    # Gestion de la requête préliminaire CORS (preflight)
    if http_method == "OPTIONS":
        return _response(200, {"message": "CORS preflight OK"})

    try:
        if path == "/health":
            return _response(200, {
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "static-app-backend"
            })

        if path == "/contact" and http_method == "POST":
            body = json.loads(event.get("body") or "{}")
            return _handle_contact(body)

        return _response(404, {"error": "Route non trouvée", "path": path})

    except json.JSONDecodeError:
        return _response(400, {"error": "Corps de requête JSON invalide"})

    except Exception as exc:  # noqa: BLE001
        logger.exception("Erreur interne")
        return _response(500, {"error": "Erreur interne du serveur"})


def _handle_contact(body: dict):
    """Valide et traite un message de contact."""
    name = body.get("name", "").strip()
    email = body.get("email", "").strip()
    message = body.get("message", "").strip()

    if not name or not email or not message:
        return _response(400, {"error": "Champs name, email et message requis"})

    # Ici on pourrait écrire dans DynamoDB, envoyer un email via SES, etc.
    logger.info("Nouveau message de contact reçu de %s", email)

    return _response(201, {
        "message": "Message reçu avec succès",
        "received_at": datetime.now(timezone.utc).isoformat()
    })


def _response(status_code: int, body: dict):
    """Construit une réponse HTTP compatible avec API Gateway."""
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body)
    }

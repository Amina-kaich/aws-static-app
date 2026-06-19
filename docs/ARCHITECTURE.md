# Architecture — Déploiement Serverless AWS

## Vue d'ensemble

Ce projet déploie une application web statique sur AWS en utilisant une architecture **100% serverless**, c'est-à-dire sans serveur à provisionner ni à maintenir manuellement.

```
                            ┌─────────────────┐
        Utilisateur  ────► │   CloudFront     │  (CDN — edge locations)
                            │   (HTTPS)        │
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   S3 Bucket      │  (fichiers statiques :
                            │   (static site)  │   HTML / CSS / JS)
                            └─────────────────┘


                            ┌─────────────────┐
        Client API  ────►   │  API Gateway     │  (REST endpoint)
                            └────────┬─────────┘
                                     │
                                     ▼
                            ┌─────────────────┐       ┌──────────────┐
                            │  AWS Lambda      │ ◄──── │  IAM Role    │
                            │  (Python 3.12)   │       │ (permissions │
                            └─────────────────┘        │  minimales)  │
                                                        └──────────────┘


                            ┌─────────────────┐
        Administrateur ──►  │  EC2 (Ubuntu)    │  (accès SSH, IAM role
                            │                  │   dédié, opérations
                            └─────────────────┘   d'administration)
```

---

## Détail des composants

### 1. S3 — Hébergement statique
Le bucket S3 est configuré en mode **Static Website Hosting**. Il contient les fichiers `index.html`, CSS et JS du frontend. Une politique de bucket (`BucketPolicy`) autorise la lecture publique (`GetObject`) sans exposer d'autres permissions.

### 2. CloudFront — CDN
CloudFront sert de couche de distribution devant S3 :
- Réduit la latence en servant le contenu depuis l'edge location la plus proche de l'utilisateur
- Force le HTTPS (`redirect-to-https`)
- Cache les assets statiques pour réduire la charge sur S3
- `PriceClass_100` est utilisé pour limiter la distribution aux régions US/Europe et réduire les coûts

### 3. API Gateway + Lambda — Backend serverless
- **API Gateway** expose un endpoint REST (`/health`, `/contact`)
- **Lambda** (Python 3.12) exécute la logique métier uniquement à la demande — aucun serveur ne tourne en permanence
- Le coût est quasi nul en Free Tier : 1 million de requêtes Lambda gratuites par mois

### 4. IAM — Sécurité et permissions
Chaque service a un rôle IAM dédié avec le **principe du moindre privilège** :
- Le rôle Lambda n'a accès qu'à CloudWatch Logs (pour le debugging) — rien d'autre
- Aucune credential n'est codée en dur dans le code source

### 5. EC2 — Administration (optionnel)
Une instance EC2 Ubuntu peut être utilisée pour des tâches d'administration ou de build, avec accès SSH via key pair et un IAM role limité.

---

## Flux d'une requête

**Affichage du site :**
1. L'utilisateur tape l'URL → requête HTTPS vers CloudFront
2. CloudFront vérifie son cache ; si absent, il va chercher le fichier sur S3
3. Le fichier est retourné et mis en cache pour les prochaines requêtes

**Appel API (ex: formulaire de contact) :**
1. Le frontend envoie une requête `POST /contact` vers API Gateway
2. API Gateway déclenche la fonction Lambda (`AWS_PROXY` integration)
3. Lambda traite la requête et retourne une réponse JSON
4. API Gateway renvoie la réponse au client avec les headers CORS appropriés

---

## Coûts — Free Tier AWS

| Service | Limite Free Tier (12 mois) | Usage estimé du projet |
|---|---|---|
| S3 | 5 GB stockage, 20 000 GET/mois | < 1 GB, usage personnel |
| CloudFront | 1 TB de transfert sortant/mois | Largement suffisant |
| Lambda | 1M requêtes + 400 000 GB-secondes/mois | Quelques centaines de requêtes |
| EC2 | 750h/mois d'instance t2.micro | Usage ponctuel uniquement |
| API Gateway | 1M appels/mois (12 premiers mois) | Largement suffisant |

> ⚠️ Toujours exécuter `scripts/cleanup.sh` après les tests pour éviter des frais résiduels (notamment CloudFront qui n'est pas inclus dans le Free Tier au-delà de 1TB).

---

## Pourquoi cette architecture ?

**Serverless plutôt que EC2 pour le backend** — Lambda élimine la gestion de serveur, scale automatiquement, et le coût suit l'usage réel plutôt qu'un forfait fixe.

**CloudFront devant S3** — sans CDN, chaque utilisateur récupère les fichiers directement depuis la région S3, ce qui ajoute de la latence pour les utilisateurs éloignés. CloudFront résout ça avec ses edge locations.

**IAM avec permissions minimales** — limite la surface d'attaque : si une fonction Lambda est compromise, elle ne peut accéder qu'à ce qui lui est strictement nécessaire.

# Cloud Deployment on AWS — Static Web Application

Architecture serverless complète pour déployer une application web statique sur AWS, avec un backend RESTful basé sur API Gateway et Lambda.

---

##  Stack technique

`AWS S3` `CloudFront` `EC2` `Lambda` `API Gateway` `IAM` `CloudFormation` `Python 3.12`

---

##  Structure du projet

```
aws_static_app/
├── frontend/
│   └── index.html              # Page statique hébergée sur S3
├── backend/
│   ├── lambda_functions/
│   │   └── handler.py          # Fonction Lambda (API REST)
│   └── test_handler.py         # Tests unitaires
├── infrastructure/
│   └── template.yaml           # Infrastructure as Code (CloudFormation)
├── scripts/
│   ├── deploy.sh                # Script de déploiement automatisé
│   └── cleanup.sh               # Script de nettoyage des ressources
├── docs/
│   └── ARCHITECTURE.md          # Documentation détaillée de l'architecture
└── README.md
```

---

##  Ce que fait ce projet

- Héberge un site statique sur **S3** avec distribution via **CloudFront** (CDN)
- Expose une API REST via **API Gateway** connectée à une fonction **Lambda** (Python)
- Applique le principe du moindre privilège avec des rôles **IAM** dédiés
- Définit toute l'infrastructure en **Infrastructure as Code** (CloudFormation) — reproductible et versionnée
- Reste entièrement dans les limites du **Free Tier AWS**

 Documentation complète de l'architecture : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

##  Déploiement

### Prérequis

```bash
# AWS CLI installé et configuré
aws configure
```

### Déployer toute l'infrastructure

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

Ce script :
1. Déploie la stack CloudFormation (S3, CloudFront, Lambda, API Gateway, IAM)
2. Upload les fichiers frontend vers S3
3. Package et met à jour le code de la fonction Lambda
4. Affiche l'URL finale du site

### Supprimer toutes les ressources (éviter les frais)

```bash
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

---

##  Tests

```bash
cd backend
python -m pytest test_handler.py -v

# ou sans pytest :
python test_handler.py
```

Tests couvrant :
-  Health check endpoint
-  Création de message de contact (succès)
-  Validation des champs requis (erreur 400)
-  Route inconnue (erreur 404)
-  Préflight CORS

---

##  Sécurité

- Aucune credential AWS n'est codée en dur — tout passe par les rôles IAM et la configuration locale d'AWS CLI
- Le rôle Lambda suit le principe du moindre privilège (accès CloudWatch Logs uniquement)
- CORS configuré explicitement sur l'API Gateway
- HTTPS forcé via CloudFront (`redirect-to-https`)

---

##  Points clés techniques

- **Infrastructure as Code** — toute l'infra est versionnée dans `template.yaml`, reproductible en une commande
- **Serverless-first** — pas de serveur à patcher ou à monitorer pour le backend
- **Cost-optimisé** — dimensionné pour rester dans le Free Tier (mémoire Lambda à 128MB, CloudFront PriceClass_100)
- **Testé** — la logique métier de la Lambda est couverte par des tests unitaires indépendants d'AWS

---

##  Statut

 Architecture et code finalisés — déploiement sur compte AWS personnel en cours dans le cadre du Free Tier.

---


#!/bin/bash
# ─────────────────────────────────────────────────────
# Script de déploiement — Application Web Statique AWS
# Usage : ./deploy.sh
# Prérequis : AWS CLI configuré (aws configure)
# ─────────────────────────────────────────────────────

set -e

PROJECT_NAME="amina-portfolio"
REGION="eu-west-1"
STACK_NAME="${PROJECT_NAME}-stack"

echo "🚀 Déploiement de l'infrastructure CloudFormation..."
aws cloudformation deploy \
  --template-file infrastructure/template.yaml \
  --stack-name "$STACK_NAME" \
  --parameter-overrides ProjectName="$PROJECT_NAME" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "$REGION"

echo "📦 Récupération du nom du bucket S3..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" \
  --output text \
  --region "$REGION")

echo "📤 Upload des fichiers frontend vers S3 ($BUCKET_NAME)..."
aws s3 sync frontend/ "s3://${BUCKET_NAME}/" \
  --delete \
  --cache-control "max-age=3600" \
  --region "$REGION"

echo "⚡ Packaging et mise à jour de la fonction Lambda..."
cd backend/lambda_functions
zip -r ../../function.zip handler.py
cd ../..

aws lambda update-function-code \
  --function-name "${PROJECT_NAME}-api-handler" \
  --zip-file fileb://function.zip \
  --region "$REGION"

rm function.zip

echo ""
echo "✅ Déploiement terminé !"
echo "🌐 URL du site :"
aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='WebsiteURL'].OutputValue" \
  --output text \
  --region "$REGION"

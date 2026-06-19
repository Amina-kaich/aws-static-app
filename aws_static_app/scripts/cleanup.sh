#!/bin/bash
# ─────────────────────────────────────────────────────
# Script de nettoyage — Supprime toutes les ressources AWS
# Important pour rester dans le Free Tier et éviter des frais
# Usage : ./cleanup.sh
# ─────────────────────────────────────────────────────

set -e

PROJECT_NAME="amina-portfolio"
REGION="eu-west-1"
STACK_NAME="${PROJECT_NAME}-stack"

echo "🗑️  Vidage du bucket S3 (requis avant suppression)..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='S3BucketName'].OutputValue" \
  --output text \
  --region "$REGION" 2>/dev/null || echo "")

if [ -n "$BUCKET_NAME" ]; then
  aws s3 rm "s3://${BUCKET_NAME}" --recursive --region "$REGION"
fi

echo "🗑️  Suppression de la stack CloudFormation..."
aws cloudformation delete-stack --stack-name "$STACK_NAME" --region "$REGION"

echo "⏳ En attente de la suppression complète..."
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region "$REGION"

echo "✅ Toutes les ressources ont été supprimées."

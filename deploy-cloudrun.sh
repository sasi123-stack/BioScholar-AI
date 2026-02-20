#!/bin/bash

# Quick deployment script for Google Cloud Run
# This script automates the deployment process

set -e  # Exit on error

echo "========================================="
echo "🚀 Google Cloud Run Deployment Script"
echo "========================================="

# Configuration
PROJECT_ID="biomed-scholar"
SERVICE_NAME="biomed-scholar-api"
REGION="us-central1"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="10"
TIMEOUT="300"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI is not installed"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo ""
echo "📋 Deployment Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo "  Memory: $MEMORY"
echo "  CPU: $CPU"
echo ""

# Prompt for confirmation
read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "🔐 Step 1: Authenticating..."
gcloud auth login

echo ""
echo "📦 Step 2: Setting project..."
gcloud config set project $PROJECT_ID

echo ""
echo "🔧 Step 3: Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

echo ""
echo "🏗️  Step 4: Building and deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory $MEMORY \
  --cpu $CPU \
  --timeout $TIMEOUT \
  --max-instances $MAX_INSTANCES

echo ""
echo "✅ Deployment complete!"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')

echo "========================================="
echo "🎉 Your API is now live!"
echo "========================================="
echo "URL: $SERVICE_URL"
echo ""
echo "Next steps:"
echo "1. Set environment variables:"
echo "   gcloud run services update $SERVICE_NAME --update-env-vars KEY=VALUE"
echo ""
echo "2. Update your frontend to use this URL"
echo ""
echo "3. View logs:"
echo "   gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "========================================="

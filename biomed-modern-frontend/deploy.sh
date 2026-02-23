#!/bin/bash

# ============================================================================
# BioMedScholar AI - Firebase Hosting Setup Script
# ============================================================================
# This script initializes and deploys the frontend to Firebase Hosting

echo "🔥 BioMedScholar AI - Firebase Hosting Setup"
echo "=============================================="
echo ""

# Step 1: Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

echo "✅ Firebase CLI installed (version $(firebase --version))"
echo ""

# Step 2: Login to Firebase
echo "📝 Step 1: Login to Firebase"
echo "You need to authenticate with your Google account."
echo "Run this command:"
echo ""
echo "  firebase login"
echo ""
echo "This will open a browser window where you can sign in with your Google account."
echo ""
read -p "Press Enter after you've logged in..."
echo ""

# Step 3: Initialize Firebase project
echo "🚀 Step 2: Initializing Firebase project..."
cd /workspaces/BioScholar-AI/biomed-modern-frontend

firebase init hosting \
  --public="." \
  --single-page-app \
  --skip-analytics \
  --project=biomed-scholar

echo ""
echo "✅ Firebase project initialized!"
echo ""

# Step 4: Deploy to Firebase Hosting
echo "⚡ Step 3: Deploying to Firebase Hosting..."
firebase deploy --project=biomed-scholar

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📱 Your site is now live at:"
firebase hosting:list --project=biomed-scholar

echo ""
echo "✨ All done! Your BioMedScholar AI frontend is now hosted on Firebase!"

#!/bin/bash

# CodePilot Deployment Helper Script

echo "🚀 CodePilot Cloud Deployment Helper"
echo "====================================="
echo ""

# Check if git repo is clean
if [[ -n $(git status -s) ]]; then
    echo "⚠️  You have uncommitted changes. Commit them first:"
    echo "   git add ."
    echo "   git commit -m 'Prepare for deployment'"
    echo "   git push origin main"
    exit 1
fi

echo "✅ Git repository is clean"
echo ""

# Instructions
echo "📋 Deployment Steps:"
echo ""
echo "1️⃣  BACKEND (Render):"
echo "   • Go to: https://dashboard.render.com/create?type=web"
echo "   • Connect your GitHub repo"
echo "   • Build: pip install -r requirements.txt"
echo "   • Start: python -m uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
echo "   • Environment: PYTHONPATH=/opt/render/project/src"
echo "   • Copy your API URL"
echo ""

echo "2️⃣  FRONTEND (Vercel):"
echo "   • Option A - CLI:"
echo "     cd web && vercel"
echo ""
echo "   • Option B - Dashboard:"
echo "     https://vercel.com/new"
echo "     Root Directory: web"
echo "     Environment: NEXT_PUBLIC_API_URL=<your-render-url>"
echo ""

echo "3️⃣  TEST:"
echo "   • Visit your Vercel URL"
echo "   • Index a GitHub repo"
echo "   • Search!"
echo ""

echo "📖 Full guide: See DEPLOYMENT.md"
echo ""

read -p "Press Enter to open DEPLOYMENT.md or Ctrl+C to exit..."
open DEPLOYMENT.md || cat DEPLOYMENT.md


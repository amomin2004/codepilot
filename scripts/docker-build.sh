#!/bin/bash

# CodePilot Docker Build Script
set -e

echo "🐳 Building CodePilot Docker containers..."

# Build API container
echo "📦 Building API container..."
docker build -f Dockerfile.api -t codepilot-api:latest .

# Build Web container
echo "📦 Building Web container..."
docker build -f Dockerfile.web -t codepilot-web:latest .

echo "✅ Docker containers built successfully!"
echo ""
echo "🚀 To start CodePilot:"
echo "   docker-compose up -d"
echo ""
echo "🚀 To start in development mode:"
echo "   docker-compose -f docker-compose.dev.yml up -d"
echo ""
echo "🚀 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🚀 To stop:"
echo "   docker-compose down"

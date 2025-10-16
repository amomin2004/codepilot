#!/bin/bash

# CodePilot Docker Start Script
set -e

echo "🚀 Starting CodePilot..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p output

# Start services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 10

# Check API health
echo "🔍 Checking API health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start properly"
        docker-compose logs api
        exit 1
    fi
    sleep 2
done

# Check Web health
echo "🔍 Checking Web health..."
for i in {1..30}; do
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Web interface is healthy"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Web interface failed to start properly"
        docker-compose logs web
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎉 CodePilot is running!"
echo ""
echo "📱 Web Interface: http://localhost:3000"
echo "🔌 API Endpoint:  http://localhost:8000"
echo "📊 API Docs:      http://localhost:8000/docs"
echo ""
echo "🔧 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose down"
echo ""
echo "📁 To index a repository:"
echo "   1. Go to http://localhost:3000"
echo "   2. Click 'Ingest'"
echo "   3. Enter repository path"
echo "   4. Click 'Start Indexing'"

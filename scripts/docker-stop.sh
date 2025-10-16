#!/bin/bash

# CodePilot Docker Stop Script
set -e

echo "🛑 Stopping CodePilot..."

# Stop and remove containers
docker-compose down

echo "✅ CodePilot stopped successfully!"
echo ""
echo "🗑️  To remove all data (including indexed repositories):"
echo "   docker-compose down -v"
echo ""
echo "🧹 To clean up Docker images:"
echo "   docker system prune -a"

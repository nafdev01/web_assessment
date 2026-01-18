#!/bin/bash

# Quick start script for Docker setup
set -e

echo "================================"
echo "Web Assessment Docker Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and update the following:"
    echo "   - POSTGRES_PASSWORD"
    echo "   - DJANGO_SECRET_KEY"
    echo "   - DJANGO_SUPERUSER credentials"
    echo "   - Email configuration (if needed)"
    echo ""
    read -p "Press Enter to continue after updating .env file..."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🏗️  Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Services are starting up!"
echo ""
echo "================================"
echo "Access your application at:"
echo "  Web: http://localhost:8000"
echo "  Admin: http://localhost:8000/admin"
echo "================================"
echo ""
echo "Useful commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  Or use:           make help"
echo ""
echo "Check DOCKER.md for more information!"

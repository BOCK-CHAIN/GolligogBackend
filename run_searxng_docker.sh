#!/bin/bash
# SearXNG Docker Run Script for Golligog

echo "Starting SearXNG with Docker for Golligog..."
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "Error: docker-compose is not installed."
    exit 1
fi

echo "Using $COMPOSE_CMD"

# Start SearXNG
echo "Starting SearXNG and Redis services..."
$COMPOSE_CMD up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 10

# Check if SearXNG is running
if curl -f http://localhost:8080/healthz > /dev/null 2>&1; then
    echo "✅ SearXNG is running successfully!"
    echo "🌐 SearXNG URL: http://localhost:8080"
    echo "🔍 Search API: http://localhost:8080/search"
    echo ""
    echo "To view logs: $COMPOSE_CMD logs -f searxng"
    echo "To stop: $COMPOSE_CMD down"
else
    echo "❌ SearXNG failed to start. Checking logs..."
    $COMPOSE_CMD logs searxng
fi
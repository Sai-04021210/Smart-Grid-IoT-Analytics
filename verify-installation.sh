#!/bin/bash

# Smart Grid IoT Analytics - Installation Verification Script
# This script checks if all services are running correctly

echo "🔍 Smart Grid IoT Analytics - Installation Verification"
echo "======================================================="

# Check if Docker is installed
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed: $(docker --version)"
else
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
echo "2. Checking Docker Compose installation..."
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    echo "✅ Docker Compose is available"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if services are running
echo "3. Checking if services are running..."
if docker compose ps | grep -q "Up"; then
    echo "✅ Docker Compose services are running"
    docker compose ps
else
    echo "❌ Services are not running. Starting services..."
    docker compose up -d
    echo "⏳ Waiting 30 seconds for services to start..."
    sleep 30
fi

# Check individual service health
echo "4. Checking service health..."

# Check Frontend
echo "   - Frontend (React)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "     ✅ Frontend is accessible at http://localhost:3000"
else
    echo "     ❌ Frontend is not accessible"
fi

# Check Backend
echo "   - Backend (FastAPI)..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo "     ✅ Backend is accessible at http://localhost:8000"
else
    echo "     ❌ Backend is not accessible"
fi

# Check Node-RED
echo "   - Node-RED..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:1880 | grep -q "200"; then
    echo "     ✅ Node-RED is accessible at http://localhost:1880"
else
    echo "     ❌ Node-RED is not accessible"
fi

# Check MQTT Broker
echo "   - MQTT Broker..."
if nc -z localhost 1883 2>/dev/null; then
    echo "     ✅ MQTT Broker is accessible at localhost:1883"
else
    echo "     ❌ MQTT Broker is not accessible"
fi

# Check PostgreSQL
echo "   - PostgreSQL Database..."
if nc -z localhost 5432 2>/dev/null; then
    echo "     ✅ PostgreSQL is accessible at localhost:5432"
else
    echo "     ❌ PostgreSQL is not accessible"
fi

# Check Redis
echo "   - Redis Cache..."
if nc -z localhost 6379 2>/dev/null; then
    echo "     ✅ Redis is accessible at localhost:6379"
else
    echo "     ❌ Redis is not accessible"
fi

echo ""
echo "🎯 Installation Summary:"
echo "========================"
echo "✅ Web Dashboard: http://localhost:3000"
echo "✅ API Documentation: http://localhost:8000/docs"
echo "✅ Node-RED Dashboard: http://localhost:1880"
echo ""
echo "If any services show ❌, check the logs with:"
echo "   docker compose logs [service-name]"
echo ""
echo "For troubleshooting, see README.md"

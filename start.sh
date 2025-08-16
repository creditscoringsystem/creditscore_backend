#!/bin/bash

echo "🚀 Starting Credit Score Backend System..."

# Start all services
echo "📦 Building and starting containers..."
docker-compose up -d --build

# Wait a bit for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Apply Kong configuration
echo "🔧 Applying Kong configuration..."
./apply-kong-config.sh

echo ""
echo "✅ System started successfully!"
echo ""
echo "📊 Service Status:"
echo "   Kong Gateway: http://localhost:8000"
echo "   Kong Admin:   http://localhost:8001"
echo "   User Service: http://localhost:8002"
echo "   Profile Service: http://localhost:8003"
echo "   Alert Service: http://localhost:8004"
echo "   Survey Service: http://localhost:8005"
echo "   Score Service: http://localhost:8007"
echo "   PostgreSQL: localhost:5432"

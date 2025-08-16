#!/bin/bash

echo "🚀 Applying Kong Declarative Config..."

# Wait for Kong to be ready
until curl -f http://localhost:8001/ > /dev/null 2>&1; do
    echo "Waiting for Kong Admin API..."
    sleep 2
done

# Apply the YAML config
echo "📄 Loading kong-config.yml..."
curl -X POST http://localhost:8001/config \
    -F config=@kong-config.yml

echo ""
echo "✅ Kong configuration applied!"
echo ""
echo "🧪 Test endpoints:"
echo "   curl http://localhost:8000/api/v1/user-ping"
echo "   curl http://localhost:8000/api/v1/profile-health"
echo "   curl http://localhost:8000/api/v1/alert-health"
echo "   curl http://localhost:8000/api/v1/survey-health"
echo "   curl http://localhost:8000/api/v1/score-health"

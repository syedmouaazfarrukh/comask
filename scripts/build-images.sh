#!/bin/bash

# Build Docker images for Colorado Energy Compliance Assistant
# Usage: ./scripts/build-images.sh [tag]

set -e

# Configuration
TAG=${1:-latest}
REGISTRY=${DOCKER_REGISTRY:-""}

echo "Building Docker images with tag: $TAG"

# Build backend
echo "Building backend image..."
docker build \
  -t comask-backend:$TAG \
  -f backend/Dockerfile \
  ./backend

# Build frontend
echo "Building frontend image..."
docker build \
  -t comask-frontend:$TAG \
  -f frontend/Dockerfile \
  ./frontend

echo "Build complete!"
echo ""
echo "Images built:"
docker images | grep comask

# If registry is specified, tag and push
if [ -n "$REGISTRY" ]; then
  echo ""
  echo "Tagging and pushing to registry: $REGISTRY"

  docker tag comask-backend:$TAG $REGISTRY/comask-backend:$TAG
  docker tag comask-frontend:$TAG $REGISTRY/comask-frontend:$TAG

  docker push $REGISTRY/comask-backend:$TAG
  docker push $REGISTRY/comask-frontend:$TAG

  echo "Push complete!"
fi

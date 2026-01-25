#!/bin/bash

# =============================================================================
# Comask Docker Image Build Script
# =============================================================================
# Builds production Docker images for frontend and backend
#
# Usage:
#   ./scripts/build-images.sh <version>
#   ./scripts/build-images.sh v1.0.0
#   ./scripts/build-images.sh latest
#
# Options:
#   --push    Also push images to registry after building
#   --acr     Push to Azure Container Registry (requires az login)
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
ACR_NAME="${ACR_NAME:-comaskacr}"
IMAGE_PREFIX="${IMAGE_PREFIX:-comask}"

# Parse arguments
VERSION=""
PUSH=false
USE_ACR=false

for arg in "$@"; do
    case $arg in
        --push)
            PUSH=true
            shift
            ;;
        --acr)
            USE_ACR=true
            PUSH=true
            shift
            ;;
        -*)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION="$arg"
            fi
            ;;
    esac
done

# Validate version
if [ -z "$VERSION" ]; then
    echo -e "${RED}Error: Version tag required${NC}"
    echo ""
    echo "Usage: ./scripts/build-images.sh <version> [--push] [--acr]"
    echo ""
    echo "Examples:"
    echo "  ./scripts/build-images.sh v1.0.0"
    echo "  ./scripts/build-images.sh v1.0.0 --push"
    echo "  ./scripts/build-images.sh v1.0.0 --acr"
    exit 1
fi

# Set registry prefix
if [ "$USE_ACR" = true ]; then
    REGISTRY="${ACR_NAME}.azurecr.io"
else
    REGISTRY="docker.io"
fi

echo ""
echo -e "${BLUE}=============================================="
echo "  Comask Production Image Builder"
echo "==============================================${NC}"
echo ""
echo -e "Version:  ${GREEN}$VERSION${NC}"
echo -e "Registry: ${GREEN}$REGISTRY${NC}"
echo -e "Push:     ${GREEN}$PUSH${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo -e "${BLUE}[INFO]${NC} Project root: $PROJECT_ROOT"
echo ""

# -----------------------------------------------------------------------------
# Build Backend Image
# -----------------------------------------------------------------------------
echo -e "${BLUE}[1/4]${NC} Building backend image..."

BACKEND_IMAGE="${IMAGE_PREFIX}-backend"
BACKEND_FULL="${REGISTRY}/${BACKEND_IMAGE}"

docker build \
    -t "${BACKEND_IMAGE}:${VERSION}" \
    -t "${BACKEND_IMAGE}:latest" \
    -t "${BACKEND_FULL}:${VERSION}" \
    -t "${BACKEND_FULL}:latest" \
    --label "org.opencontainers.image.version=${VERSION}" \
    --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -f ./backend/Dockerfile \
    ./backend

echo -e "${GREEN}[SUCCESS]${NC} Backend image built: ${BACKEND_IMAGE}:${VERSION}"
echo ""

# -----------------------------------------------------------------------------
# Build Frontend Image
# -----------------------------------------------------------------------------
echo -e "${BLUE}[2/4]${NC} Building frontend image..."

FRONTEND_IMAGE="${IMAGE_PREFIX}-frontend"
FRONTEND_FULL="${REGISTRY}/${FRONTEND_IMAGE}"

docker build \
    -t "${FRONTEND_IMAGE}:${VERSION}" \
    -t "${FRONTEND_IMAGE}:latest" \
    -t "${FRONTEND_FULL}:${VERSION}" \
    -t "${FRONTEND_FULL}:latest" \
    --label "org.opencontainers.image.version=${VERSION}" \
    --label "org.opencontainers.image.created=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    -f ./frontend/Dockerfile \
    ./frontend

echo -e "${GREEN}[SUCCESS]${NC} Frontend image built: ${FRONTEND_IMAGE}:${VERSION}"
echo ""

# -----------------------------------------------------------------------------
# Push Images (if requested)
# -----------------------------------------------------------------------------
if [ "$PUSH" = true ]; then
    echo -e "${BLUE}[3/4]${NC} Pushing images to registry..."
    
    if [ "$USE_ACR" = true ]; then
        echo -e "${BLUE}[INFO]${NC} Logging into Azure Container Registry..."
        az acr login --name "$ACR_NAME"
    fi
    
    echo -e "${BLUE}[INFO]${NC} Pushing backend image..."
    docker push "${BACKEND_FULL}:${VERSION}"
    docker push "${BACKEND_FULL}:latest"
    echo -e "${GREEN}[SUCCESS]${NC} Backend pushed to ${BACKEND_FULL}:${VERSION}"
    
    echo -e "${BLUE}[INFO]${NC} Pushing frontend image..."
    docker push "${FRONTEND_FULL}:${VERSION}"
    docker push "${FRONTEND_FULL}:latest"
    echo -e "${GREEN}[SUCCESS]${NC} Frontend pushed to ${FRONTEND_FULL}:${VERSION}"
else
    echo -e "${YELLOW}[3/4]${NC} Skipping push (use --push or --acr to push)"
fi

echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "${BLUE}[4/4]${NC} Build Summary"
echo ""
echo -e "${GREEN}=============================================="
echo "  Build Complete!"
echo "==============================================${NC}"
echo ""
echo "Images created:"
echo -e "  ${GREEN}Backend:${NC}  ${BACKEND_IMAGE}:${VERSION}"
echo -e "  ${GREEN}Frontend:${NC} ${FRONTEND_IMAGE}:${VERSION}"
echo ""

if [ "$PUSH" = true ]; then
    echo "Pushed to registry:"
    echo -e "  ${GREEN}Backend:${NC}  ${BACKEND_FULL}:${VERSION}"
    echo -e "  ${GREEN}Frontend:${NC} ${FRONTEND_FULL}:${VERSION}"
    echo ""
fi

echo "To run locally with these images:"
echo "  docker run -p 8000:8000 ${BACKEND_IMAGE}:${VERSION}"
echo "  docker run -p 3000:3000 ${FRONTEND_IMAGE}:${VERSION}"
echo ""

if [ "$PUSH" = false ]; then
    echo "To push to Azure Container Registry:"
    echo "  ./scripts/build-images.sh ${VERSION} --acr"
    echo ""
fi

# Show image sizes
echo "Image sizes:"
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep "${IMAGE_PREFIX}"
echo ""

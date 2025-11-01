#!/bin/bash
set -euo pipefail

KUBECONFIG_FILE="$1"
NAMESPACE="${2:-youtube-app}"
DEPLOYMENT="${3:-youtube-api}"
IMAGE="$4"

export KUBECONFIG="$KUBECONFIG_FILE"

echo "Deploying to Kubernetes..."
echo "Namespace: $NAMESPACE"
echo "Deployment: $DEPLOYMENT"
echo "Image: $IMAGE"

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Apply RBAC
kubectl -n "$NAMESPACE" apply -f k8s/rbac.yaml || true

# Check if deployment exists and update or create
if kubectl -n "$NAMESPACE" get deploy "$DEPLOYMENT" >/dev/null 2>&1; then
  echo "Updating existing deployment..."
  kubectl -n "$NAMESPACE" set image deployment/"$DEPLOYMENT" "$DEPLOYMENT"="${IMAGE}"
else
  echo "Creating new deployment..."
  sed "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${IMAGE}#g" k8s/deploy.yaml | kubectl -n "$NAMESPACE" apply -f -
fi

# Wait for rollout
kubectl -n "$NAMESPACE" rollout status deployment/"$DEPLOYMENT" --timeout=120s

echo "Deployment successful!"
kubectl -n "$NAMESPACE" get pods

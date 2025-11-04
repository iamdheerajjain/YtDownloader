#!/bin/bash

# Script to diagnose Kubernetes connectivity issues
# Usage: ./scripts/diagnose-k8s-connectivity.sh [kubeconfig_path]

set -e

KUBECONFIG_PATH=${1:-"./kubeconfig-jenkins.yaml"}

echo "=== Kubernetes Connectivity Diagnosis ==="
echo "Using kubeconfig: $KUBECONFIG_PATH"
echo ""

# Check if kubeconfig file exists
if [ ! -f "$KUBECONFIG_PATH" ]; then
    echo "ERROR: Kubeconfig file not found at $KUBECONFIG_PATH"
    exit 1
fi

echo "Kubeconfig file exists: YES"
echo "Kubeconfig file size: $(stat -c%s "$KUBECONFIG_PATH") bytes"
echo ""

# Export kubeconfig
export KUBECONFIG="$KUBECONFIG_PATH"

echo "=== Kubectl Version ==="
kubectl version --client --output=yaml 2>/dev/null || echo "kubectl version check failed"
echo ""

echo "=== Current Context ==="
kubectl config current-context 2>/dev/null || echo "No current context found"
echo ""

echo "=== Available Contexts ==="
kubectl config get-contexts 2>/dev/null || echo "Failed to get contexts"
echo ""

echo "=== Cluster Information ==="
kubectl cluster-info 2>/dev/null || echo "Cannot reach cluster - this is expected if using placeholder config"
echo ""

echo "=== Server Endpoint ==="
SERVER=$(kubectl config view -o jsonpath='{.clusters[0].cluster.server}' 2>/dev/null || echo "Not found")
echo "Server endpoint: $SERVER"
echo ""

if [[ "$SERVER" == *"127.0.0.1"* ]] || [[ "$SERVER" == *"localhost"* ]]; then
    echo "WARNING: Server is pointing to localhost. This will not work in Jenkins environment."
    echo "Please update the kubeconfig with actual cluster endpoint information."
    echo ""
fi

echo "=== User Authentication ==="
USER_NAME=$(kubectl config view -o jsonpath='{.users[0].name}' 2>/dev/null || echo "Not found")
echo "User: $USER_NAME"

TOKEN_LENGTH=$(kubectl config view -o jsonpath='{.users[0].user.token}' 2>/dev/null | wc -c || echo "0")
if [ "$TOKEN_LENGTH" -gt "10" ]; then
    echo "Token: [REDACTED - ${TOKEN_LENGTH} characters]"
else
    echo "Token: [NOT FOUND or TOO SHORT]"
fi
echo ""

echo "=== Diagnosis Complete ==="
echo "If deploying to a real cluster, ensure:"
echo "1. Server endpoint points to actual cluster API"
echo "2. Authentication token is valid and not expired"
echo "3. Jenkins server can reach the cluster endpoint"
echo "4. RBAC permissions are properly configured"
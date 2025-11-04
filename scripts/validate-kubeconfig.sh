#!/bin/bash
set -euo pipefail

KUBECONFIG_FILE="${1:-kubeconfig-jenkins.yaml}"

echo "Validating kubeconfig file: $KUBECONFIG_FILE"

if [[ ! -f "$KUBECONFIG_FILE" ]]; then
    echo "Error: Kubeconfig file not found: $KUBECONFIG_FILE"
    exit 1
fi

export KUBECONFIG="$KUBECONFIG_FILE"

echo "Checking kubeconfig structure..."
if ! kubectl config view >/dev/null 2>&1; then
    echo "Error: Invalid kubeconfig structure"
    exit 1
fi

echo "Checking current context..."
CURRENT_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
if [[ -z "$CURRENT_CONTEXT" ]]; then
    echo "Warning: No current context set"
else
    echo "Current context: $CURRENT_CONTEXT"
fi

echo "Checking clusters..."
CLUSTERS=$(kubectl config get-clusters 2>/dev/null || echo "")
if [[ -z "$CLUSTERS" ]]; then
    echo "Warning: No clusters found"
else
    echo "Clusters found:"
    echo "$CLUSTERS" | sed 's/^/  - /'
fi

echo "Checking users..."
USERS=$(kubectl config view -o jsonpath='{.users[*].name}' 2>/dev/null || echo "")
if [[ -z "$USERS" ]]; then
    echo "Warning: No users found"
else
    echo "Users found:"
    for user in $USERS; do
        echo "  - $user"
    done
fi

echo "Testing cluster connectivity..."
if kubectl cluster-info >/dev/null 2>&1; then
    echo "Success: Cluster is reachable"
else
    echo "Warning: Cannot reach cluster (this is expected if running outside the cluster network)"
fi

echo "Testing authentication..."
NAMESPACE=$(kubectl config view -o jsonpath='{.contexts[?(@.name=="jenkins-context")].context.namespace}' 2>/dev/null || echo "default")
if [[ -z "$NAMESPACE" ]]; then
    NAMESPACE="default"
fi

if kubectl auth can-i get pods --namespace="$NAMESPACE" >/dev/null 2>&1; then
    echo "Success: Authentication is working"
else
    echo "Warning: Authentication failed - you may need to update your token"
fi

echo "Kubeconfig validation completed."
echo "Remember to replace the placeholder values with your real cluster information before deployment."
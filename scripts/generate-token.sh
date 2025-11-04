set -euo pipefail

NAMESPACE="${1:-youtube-app}"
SERVICE_ACCOUNT="${2:-jenkins-sa}"

echo "Generating new token for service account: $SERVICE_ACCOUNT in namespace: $NAMESPACE"

if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed or not in PATH"
    exit 1
fi

if ! kubectl -n "$NAMESPACE" get serviceaccount "$SERVICE_ACCOUNT" >/dev/null 2>&1; then
    echo "Error: Service account $SERVICE_ACCOUNT not found in namespace $NAMESPACE"
    echo "Please create it first with: kubectl -n $NAMESPACE apply -f k8s/rbac.yaml"
    exit 1
fi

SECRET_NAME="${SERVICE_ACCOUNT}-token-$(date +%s)"
cat <<EOF | kubectl -n "$NAMESPACE" apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: $SECRET_NAME
  annotations:
    kubernetes.io/service-account.name: $SERVICE_ACCOUNT
type: kubernetes.io/service-account-token
EOF

echo "Waiting for token to be generated..."
TOKEN=""
for i in {1..30}; do
    TOKEN=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o jsonpath='{.data.token}' 2>/dev/null | base64 -d 2>/dev/null || echo "")
    if [[ -n "$TOKEN" ]]; then
        break
    fi
    sleep 2
done

if [[ -z "$TOKEN" ]]; then
    echo "Error: Failed to generate token after 60 seconds"
    kubectl -n "$NAMESPACE" delete secret "$SECRET_NAME" >/dev/null 2>&1 || true
    exit 1
fi

echo "New token generated successfully!"
echo ""
echo "----------------------------------------"
echo "New token for $SERVICE_ACCOUNT:"
echo "$TOKEN"
echo "----------------------------------------"
echo ""

echo "To update your kubeconfig, replace the token in kubeconfig-jenkins.yaml with the token above."
echo "The token is located under users[0].user.token"

BACKUP_FILE="kubeconfig-jenkins.yaml.backup.$(date +%s)"
echo ""
echo "Creating backup of current kubeconfig as $BACKUP_FILE"
cp kubeconfig-jenkins.yaml "$BACKUP_FILE"

echo ""
echo "Next steps:"
echo "1. Update your kubeconfig file with the new token"
echo "2. Run './scripts/validate-kubeconfig.sh kubeconfig-jenkins.yaml' to verify"
echo "3. Test with 'kubectl --kubeconfig=kubeconfig-jenkins.yaml get pods -n youtube-app'"
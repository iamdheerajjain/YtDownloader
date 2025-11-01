set -euo pipefail

KUBECONFIG_FILE="$1"
NAMESPACE="${2:-youtube-app}"
DEPLOYMENT="${3:-youtube-api}"
IMAGE="$4"

export KUBECONFIG="$KUBECONFIG_FILE"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl -n "$NAMESPACE" apply -f k8s/rbac.yaml || true
if kubectl -n "$NAMESPACE" get deploy "$DEPLOYMENT" >/dev/null 2>&1; then
  kubectl -n "$NAMESPACE" set image deployment/"$DEPLOYMENT" "$DEPLOYMENT"="${IMAGE}" --record
else
  sed "s#<IMAGE_REGISTRY>/<IMAGE_NAME>:<IMAGE_TAG>#${IMAGE}#g" k8s/deploy.yaml | kubectl -n "$NAMESPACE" apply -f -
fi
kubectl -n "$NAMESPACE" rollout status deployment/"$DEPLOYMENT" --timeout=120s

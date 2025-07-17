#!/bin/bash

set -e

echo "deploy :: running post deploy hook - app/lib/kube/scripts/post-deploy.sh"

DEPLOYMENTS=$(kubectl get deployments -n "$KUBE_NS" -l app.kubernetes.io/instance="$KUBE_APP" -o json | jq -r '.items[].metadata.name')

FAILED_DEPLOYMENTS=()

for DEPLOYMENT in $DEPLOYMENTS; do
  echo "Waiting for deployment rollout: $DEPLOYMENT in $KUBE_NS..."
  if ! kubectl rollout status deployment "$DEPLOYMENT" -n "$KUBE_NS" --timeout=60s; then
    echo "Rollout failed for $DEPLOYMENT"
    FAILED_DEPLOYMENTS+=("$DEPLOYMENT")
  fi
done

if [ ${#FAILED_DEPLOYMENTS[@]} -eq 0 ]; then
  echo "Deployment finished successfully"
  exit 0
fi

for DEPLOYMENT in "${FAILED_DEPLOYMENTS[@]}"; do
  echo "Checking failed rollout for $DEPLOYMENT"

  PODS=$(kubectl get pods -n "$KUBE_NS" -l app.kubernetes.io/name="$DEPLOYMENT" -o jsonpath='{.items[*].metadata.name}')

  if [ -z "$PODS" ]; then
    echo "No pods found for deployment $DEPLOYMENT"
    continue
  fi

  for POD in $PODS; do
    echo "kubectl describe pod $POD -n $KUBE_NS"
    kubectl describe pod "$POD" -n "$KUBE_NS"

    echo "Logs for pod: $POD"
    kubectl logs "$POD" -n "$KUBE_NS"
  done
done

echo "One or more deployments failed rollout. Exiting with error."
exit 1

#!/bin/bash

set -e

echo "Deployment rollout status for $KUBE_APP in namespace $KUBE_NS"

# Ensure required env vars are set
if [[ -z "$KUBE_APP" || -z "$KUBE_NS" ]]; then
  echo "KUBE_APP or KUBE_NS is not set."
  exit 1
fi

# Set deployment names
WEB_DEPLOYMENT="$KUBE_APP-deployment"
TEMPORAL_DEPLOYMENT="$KUBE_APP-temporal-deployment"

# Wait for both rollouts to complete
echo "Waiting for rollout of $WEB_DEPLOYMENT and $TEMPORAL_DEPLOYMENT"
kubectl rollout status deploy/"$WEB_DEPLOYMENT" -n "$KUBE_NS"
kubectl rollout status deploy/"$TEMPORAL_DEPLOYMENT" -n "$KUBE_NS"

# Function to collect logs from a deployment
collect_logs_from_deployment() {
  local DEPLOYMENT_NAME=$1
  echo "Fetching pods for: $DEPLOYMENT_NAME"
  
  PODS=$(kubectl get pods -n "$KUBE_NS" -l "app.kubernetes.io/name=$DEPLOYMENT_NAME" -o name)

  if [[ -z "$PODS" ]]; then
    echo "No pods found for: $DEPLOYMENT_NAME"
    return
  fi

  for pod in $PODS; do
    echo -e "\nLogs from pod: $pod"
    containers=$(kubectl get "$pod" -n "$KUBE_NS" -o jsonpath='{.spec.containers[*].name}')
    for container in $containers; do
      echo "Container: $container"
      kubectl logs "$pod" -c "$container" -n "$KUBE_NS" || echo "Failed to get logs for $container"
    done
  done
}

# Collect logs from both deployments
collect_logs_from_deployment "$WEB_DEPLOYMENT"
collect_logs_from_deployment "$TEMPORAL_DEPLOYMENT"

echo -e "\n Deployment finished successfully"

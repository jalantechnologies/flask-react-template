#!/bin/bash

set -e

echo "Deployment rollout status for $KUBE_APP in namespace $KUBE_NS"


if [[ -z "$KUBE_APP" || -z "$KUBE_NS" ]]; then
  echo "KUBE_APP or KUBE_NS is not set."
  exit 1
fi

WEB_DEPLOYMENT="$KUBE_APP-deployment"
TEMPORAL_DEPLOYMENT="$KUBE_APP-temporal-deployment"

# Function to wait for rollout and handle failure gracefully
wait_for_rollout() {
  local DEPLOYMENT_NAME=$1
  echo "Waiting for rollout of $DEPLOYMENT_NAME"
  if ! kubectl rollout status deploy/"$DEPLOYMENT_NAME" -n "$KUBE_NS"; then
    echo "⚠️ Rollout failed or timed out for $DEPLOYMENT_NAME. Continuing to collect logs..."
  fi
}

# Function to collect logs from a deployment
collect_logs_from_deployment() {
  local DEPLOYMENT_NAME=$1
  echo -e "\nFetching pods for: $DEPLOYMENT_NAME"

  PODS=$(kubectl get pods -n "$KUBE_NS" -l "app.kubernetes.io/name=$DEPLOYMENT_NAME" -o name)

  if [[ -z "$PODS" ]]; then
    echo "No pods found for: $DEPLOYMENT_NAME"
    return
  fi

  for pod in $PODS; do
    echo -e "\nLogs from pod: $pod"
    containers=$(kubectl get "$pod" -n "$KUBE_NS" -o jsonpath='{.spec.containers[*].name}')
    for container in $containers; do
      echo "🔹 Container: $container"
      kubectl logs "$pod" -c "$container" -n "$KUBE_NS" || echo "⚠️ Failed to get logs for $container"
    done
  done
}

# Wait for rollouts without exiting on failure
wait_for_rollout "$WEB_DEPLOYMENT"
wait_for_rollout "$TEMPORAL_DEPLOYMENT"

# Collect logs from both deployments
collect_logs_from_deployment "$WEB_DEPLOYMENT"
collect_logs_from_deployment "$TEMPORAL_DEPLOYMENT"

echo -e "\nPost-deployment rollout and log collection complete."

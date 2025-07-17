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

# Track rollout success state
ROLL_OUT_SUCCESS=true

# Function to collect logs from a deployment
collect_logs_from_deployment() {
  local DEPLOYMENT_NAME=$1
  echo -e "\nFetching pods for: $DEPLOYMENT_NAME"

  PODS=$(kubectl get pods -n "$KUBE_NS" -o json \
    | jq -r --arg name "$DEPLOYMENT_NAME" '.items[] | select(.metadata.ownerReferences[].name == $name) | .metadata.name')

  if [[ -z "$PODS" ]]; then
    echo "No pods found for: $DEPLOYMENT_NAME"
    return
  fi

  for pod in $PODS; do
    echo -e "\nLogs from pod: $pod"
    containers=$(kubectl get pod "$pod" -n "$KUBE_NS" -o jsonpath='{.spec.containers[*].name}')
    for container in $containers; do
      echo "Container: $container"
      kubectl logs "$pod" -c "$container" -n "$KUBE_NS" || echo "Failed to get logs for $container"
    done
  done
}

# Function to wait for rollout and collect logs if failed
wait_for_rollout() {
  local DEPLOYMENT_NAME=$1
  echo "Waiting for rollout of $DEPLOYMENT_NAME"
  if ! kubectl rollout status deploy/"$DEPLOYMENT_NAME" -n "$KUBE_NS"; then
    echo "Rollout failed for $DEPLOYMENT_NAME"
    collect_logs_from_deployment "$DEPLOYMENT_NAME"  # <-- Print logs immediately on failure
    ROLL_OUT_SUCCESS=false
  fi
}

# Run rollouts (logs on failure printed inline)
wait_for_rollout "$WEB_DEPLOYMENT"
wait_for_rollout "$TEMPORAL_DEPLOYMENT"

# Optional: Collect logs again even if rollouts succeeded (for audit/debug)
collect_logs_from_deployment "$WEB_DEPLOYMENT"
collect_logs_from_deployment "$TEMPORAL_DEPLOYMENT"

# Final status
if [ "$ROLL_OUT_SUCCESS" = true ]; then
  echo -e "\nAll deployments rolled out successfully"
else
  echo -e "\nOne or more deployments failed. Exiting with error."
  exit 1
fi

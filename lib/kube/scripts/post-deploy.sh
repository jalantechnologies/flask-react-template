#!/bin/bash

DEPLOYMENTS=("${KUBE_APP}-deployment" "${KUBE_APP}-temporal-deployment")
FAILED_DEPLOYMENTS=()

# Check rollout status
for DEPLOYMENT in "${DEPLOYMENTS[@]}"; do
  echo "Waiting for deployment rollout: $DEPLOYMENT in $KUBE_NS..."
  if kubectl rollout status deployment "$DEPLOYMENT" -n "$KUBE_NS" --timeout=300s; then
    echo "Rollout successful for $DEPLOYMENT"
  else
    echo "Rollout failed for $DEPLOYMENT"
    FAILED_DEPLOYMENTS+=("$DEPLOYMENT")
  fi
done

# If any rollout failed, check logs and describe
if [ "${#FAILED_DEPLOYMENTS[@]}" -ne 0 ]; then
  for DEPLOYMENT in "${FAILED_DEPLOYMENTS[@]}"; do
    echo -e "\nChecking failed rollout for $DEPLOYMENT"
    echo "Getting label selector for $DEPLOYMENT..."

    selector=$(kubectl get deployment "$DEPLOYMENT" -n "$KUBE_NS" -o jsonpath='{.spec.selector.matchLabels}' \
      | jq -r 'to_entries | map("\(.key)=\(.value)") | join(",")')

    if [ -z "$selector" ]; then
      echo "Could not extract label selector for $DEPLOYMENT — skipping log check"
      continue
    fi

    echo "Getting pods for $DEPLOYMENT..."
    pods=$(kubectl get pods -n "$KUBE_NS" -l "$selector" -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n' | sort -u)

    if [ -z "$pods" ]; then
      echo "No pods found for $DEPLOYMENT — possible issue with rollout"
      continue
    fi

    for pod in $pods; do
      echo -e "\nLogs for pod: $pod"
      echo "::group::kubectl describe pod $pod"
      kubectl describe pod "$pod" -n "$KUBE_NS" || echo "Failed to describe pod $pod"
      echo "::endgroup::"

      container_names=$(kubectl get pod "$pod" -n "$KUBE_NS" -o json | jq -r '.spec.containers[].name')
      for container in $container_names; do
        echo "::group::Logs for container $container in pod $pod"
        kubectl logs "$pod" -n "$KUBE_NS" -c "$container" --tail=-1 || echo "Failed to fetch logs for container $container in $pod"
        echo "::endgroup::"
      done
    done
  done

  echo "One or more deployments failed rollout. Exiting with error."
  exit 1
fi

echo "Deployment finished successfully"

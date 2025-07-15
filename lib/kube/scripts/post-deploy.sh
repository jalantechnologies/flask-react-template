#!/bin/bash

DEPLOYMENTS=(
  "${KUBE_APP}-deployment"
  "${KUBE_APP}-temporal-deployment"
)

for DEPLOYMENT in "${DEPLOYMENTS[@]}"; do
  echo "Waiting for deployment rollout: $DEPLOYMENT in $KUBE_NS..."

  if kubectl rollout status deployment "$DEPLOYMENT" -n "$KUBE_NS"; then
    echo "Rollout successful for $DEPLOYMENT"
  else
    echo "Rollout failed or stuck for $DEPLOYMENT — checking pod logs"

    echo "Getting label selector for $DEPLOYMENT"
    selector=$(kubectl get deployment "$DEPLOYMENT" -n "$KUBE_NS" -o jsonpath='{.spec.selector.matchLabels}' | jq -r 'to_entries | map("\(.key)=\(.value)") | join(",")')

    if [ -z "$selector" ]; then
      echo "Could not extract label selector for $DEPLOYMENT — skipping log check"
      continue
    fi

    pods=$(kubectl get pods -n "$KUBE_NS" -l "$selector" --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n')

    if [ -z "$pods" ]; then
      echo "No failing pods found for $DEPLOYMENT — rollout issue might be unrelated to pod status."
    else
      for pod in $pods; do
        echo -e "\nLogs for pod: $pod\n"

        echo "::group::kubectl describe pod $pod"
        kubectl describe pod "$pod" -n "$KUBE_NS" || echo "Failed to describe pod $pod"
        echo "::endgroup::"

        echo "::group::kubectl logs $pod --all-containers"
        kubectl logs "$pod" -n "$KUBE_NS" --all-containers=true || echo "Failed to fetch logs for $pod"
        echo "::endgroup::"
      done
    fi
  fi
done

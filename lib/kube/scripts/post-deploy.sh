#!/bin/bash

DEPLOYMENTS=(
  "${KUBE_APP}-deployment"
  "${KUBE_APP}-temporal-deployment"
)

for DEPLOYMENT in "${DEPLOYMENTS[@]}"; do
  echo " Waiting for deployment rollout: $DEPLOYMENT in $KUBE_NS..."

  if ! kubectl rollout status deployment "$DEPLOYMENT" -n "$KUBE_NS" --timeout=100s; then
    echo " Deployment rollout failed for $DEPLOYMENT"

    echo " Getting label selector for $DEPLOYMENT"
    selector=$(kubectl get deployment "$DEPLOYMENT" -n "$KUBE_NS" -o jsonpath='{.spec.selector.matchLabels}' | jq -r 'to_entries | map("\(.key)=\(.value)") | join(",")')

    if [ -z "$selector" ]; then
      echo "Could not extract label selector for $DEPLOYMENT — skipping log dump"
      continue
    fi

    echo "Finding pods with selector: $selector"
    pods=$(kubectl get pods -n "$KUBE_NS" -l "$selector" --field-selector=status.phase!=Running -o jsonpath='{.items[*].metadata.name}')

    if [ -z "$pods" ]; then
      echo "No failing pods found for $DEPLOYMENT"
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

    exit 1
  else
    echo "$DEPLOYMENT successfully rolled out!"
  fi
done

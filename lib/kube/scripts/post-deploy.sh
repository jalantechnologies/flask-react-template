#!/bin/bash

DEPLOYMENTS=(
  "${KUBE_APP}-deployment"
  "${KUBE_APP}-temporal-deployment"
)

FAILED_DEPLOYMENTS=()

for DEPLOYMENT in "${DEPLOYMENTS[@]}"; do
  echo "Waiting for deployment rollout: $DEPLOYMENT in $KUBE_NS..."

  if kubectl rollout status deployment "$DEPLOYMENT" -n "$KUBE_NS" --timeout=300s; then
    echo "Rollout successful for $DEPLOYMENT"
  else
    echo "Rollout failed or stuck for $DEPLOYMENT"
    FAILED_DEPLOYMENTS+=("$DEPLOYMENT")
  fi
done

for DEPLOYMENT in "${FAILED_DEPLOYMENTS[@]}"; do
  echo -e "\nChecking failed rollout for $DEPLOYMENT"

  echo "Getting label selector for $DEPLOYMENT"
  selector=$(kubectl get deployment "$DEPLOYMENT" -n "$KUBE_NS" -o jsonpath='{.spec.selector.matchLabels}' \
    | jq -r 'to_entries | map("\(.key)=\(.value)") | join(",")')

  if [ -z "$selector" ]; then
    echo "Could not extract label selector for $DEPLOYMENT — skipping log check"
    continue
  fi

  echo "Getting pods for $DEPLOYMENT"
  pods=$(kubectl get pods -n "$KUBE_NS" -l "$selector" -o jsonpath='{.items[*].metadata.name}' | tr ' ' '\n')

  if [ -z "$pods" ]; then
    echo "No pods found for $DEPLOYMENT — possible issue with rollout"
    continue
  fi

  PODS_WITH_ISSUES=()

  for pod in $pods; do
    # Check if any container is in a failed or waiting state
    has_issue=$(kubectl get pod "$pod" -n "$KUBE_NS" -o json | jq '
      .status.containerStatuses[]? |
      select(
        (.state.waiting.reason != null and (.state.waiting.reason | test("CrashLoopBackOff|Error|ImagePullBackOff|RunContainerError"))) or
        (.state.terminated.reason != null)
      )
    ')

    if [ -n "$has_issue" ]; then
      PODS_WITH_ISSUES+=("$pod")
    fi
  done

  if [ ${#PODS_WITH_ISSUES[@]} -eq 0 ]; then
    echo "No crashing containers found for $DEPLOYMENT — issue may be unrelated to pod/container state"
  else
    for pod in "${PODS_WITH_ISSUES[@]}"; do
      echo -e "\nLogs for pod: $pod"

      echo "::group::kubectl describe pod $pod"
      kubectl describe pod "$pod" -n "$KUBE_NS" || echo "Failed to describe pod $pod"
      echo "::endgroup::"

      echo "::group::kubectl logs $pod --all-containers"
      kubectl logs "$pod" -n "$KUBE_NS" --all-containers=true --tail=100 || echo "Failed to fetch logs for $pod"
      echo "::endgroup::"
    done
  fi
done

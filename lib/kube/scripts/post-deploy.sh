#!/usr/bin/env bash
set -euo pipefail

: "${KUBE_NS:?KUBE_NS is required}"
: "${KUBE_APP:?KUBE_APP is required}"

APP_DEPLOY="${KUBE_APP}-deployment"
TEMPORAL_DEPLOY="${KUBE_APP}-temporal-deployment"

mkdir -p ci_artifacts

collect_diagnostics() {
  echo "diag :: collecting diagnostics for namespace=$KUBE_NS"

  # Recent events
  kubectl get events -n "$KUBE_NS" --sort-by=.lastTimestamp > ci_artifacts/events.txt || true

  # Resource overviews
  kubectl -n "$KUBE_NS" get deploy,sts,svc,pods -o wide > ci_artifacts/resources.txt || true
  kubectl -n "$KUBE_NS" get pods -o yaml > ci_artifacts/pods.yaml || true

  # Save describes for our deploys if they exist
  if kubectl -n "$KUBE_NS" get deploy "$APP_DEPLOY" >/dev/null 2>&1; then
    kubectl -n "$KUBE_NS" describe deploy "$APP_DEPLOY" > ci_artifacts/describe_${APP_DEPLOY}.txt || true
  fi
  if kubectl -n "$KUBE_NS" get deploy "$TEMPORAL_DEPLOY" >/dev/null 2>&1; then
    kubectl -n "$KUBE_NS" describe deploy "$TEMPORAL_DEPLOY" > ci_artifacts/describe_${TEMPORAL_DEPLOY}.txt || true
  fi

  # Critical services (extend this list if needed)
  for svc in temporal-grpc; do
    if kubectl -n "$KUBE_NS" get svc "$svc" >/dev/null 2>&1; then
      kubectl -n "$KUBE_NS" get svc "$svc" -o wide > "ci_artifacts/svc_${svc}.txt" || true
      kubectl -n "$KUBE_NS" get endpoints "$svc" -o wide > "ci_artifacts/endpoints_${svc}.txt" || true
    else
      echo "❌ Missing Service '$svc' in ns=$KUBE_NS" >> ci_artifacts/findings.txt
      echo "::error ::Missing Service '$svc' in namespace $KUBE_NS"
    fi
  done

  # Summaries / findings
  EVENTS=ci_artifacts/events.txt
  PODS=ci_artifacts/pods.yaml

  # Scheduling / memory pressure
  if grep -Eq "FailedScheduling|Insufficient memory" "$EVENTS"; then
    {
      echo "- ❌ Pods could not schedule (insufficient node memory)."
      echo "  Fix: Close inactive PRs, reduce preview memory requests/limits, or scale the preview node pool."
    } >> ci_artifacts/findings.txt
    echo "::error ::Pods could not schedule due to insufficient memory."
  fi

  # OOMKilled signals
  if grep -q "OOMKilled" "$EVENTS"; then
    {
      echo "- ❌ A container was OOMKilled (exceeded its memory limit)."
      echo "  Fix: Increase that container’s memory limit or reduce memory usage."
    } >> ci_artifacts/findings.txt
    echo "::error ::A container was OOMKilled."
  fi

  # CrashLoopBackOff / Error pods
  if kubectl -n "$KUBE_NS" get pods | grep -Eq "CrashLoopBackOff|Error"; then
    kubectl -n "$KUBE_NS" get pods | grep -E "CrashLoopBackOff|Error" > ci_artifacts/problem_pods.txt || true
    {
      echo "- ❌ Some pods are in CrashLoopBackOff/Error."
      echo "  Fix: Inspect logs with:"
      echo "    kubectl -n $KUBE_NS logs <pod> -c <container> --tail=200"
    } >> ci_artifacts/findings.txt
    echo "::error ::Some pods are in CrashLoopBackOff/Error."
  fi

  # Build a concise PR-friendly summary
  {
    echo "### Deployment diagnostics – namespace \`$KUBE_NS\`"
    echo
    echo "**App:** \`$KUBE_APP\`"
    echo
    if [[ -s ci_artifacts/findings.txt ]]; then
      echo "#### Findings"
      cat ci_artifacts/findings.txt
    else
      echo "✅ No obvious scheduling, OOM, missing Service, or crash-loop issues detected."
    fi
    echo
    echo "<details><summary>Recent events (latest)</summary>"
    echo
    tail -n 120 "$EVENTS" | sed 's/^/    /' || true
    echo
    echo "</details>"
  } > ci_artifacts/summary.md

  echo "diag :: diagnostics collection done"

  # ✅ NEW: also append diagnostics directly to the GitHub job summary so engineers see it without artifacts
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" && -f ci_artifacts/summary.md ]]; then
    echo "diag :: writing diagnostics to GitHub job summary"
    cat ci_artifacts/summary.md >> "$GITHUB_STEP_SUMMARY" || true
  fi
}

# Always collect diagnostics at the end, even if rollout fail
trap 'collect_diagnostics' EXIT

echo "rollout :: waiting for $APP_DEPLOY"
set +e
kubectl rollout status deploy/"$APP_DEPLOY" -n "$KUBE_NS" --timeout=5m
APP_ROLLOUT_RC=$?
set -e

# Temporal deploy is optional; only wait if it exists
if kubectl -n "$KUBE_NS" get deploy "$TEMPORAL_DEPLOY" >/dev/null 2>&1; then
  echo "rollout :: waiting for $TEMPORAL_DEPLOY"
  set +e
  kubectl rollout status deploy/"$TEMPORAL_DEPLOY" -n "$KUBE_NS" --timeout=5m
  TEMP_ROLLOUT_RC=$?
  set -e
else
  echo "rollout :: $TEMPORAL_DEPLOY not found, skipping wait"
  TEMP_ROLLOUT_RC=0
fi

# If either rollout failed, emit explicit errors so CI highlights them
if [[ "$APP_ROLLOUT_RC" -ne 0 ]]; then
  echo "::error ::Rollout did not complete for ${APP_DEPLOY} (ns=$KUBE_NS). See diagnostics above."
fi
if [[ "$TEMP_ROLLOUT_RC" -ne 0 ]]; then
  echo "::error ::Rollout did not complete for ${TEMPORAL_DEPLOY} (ns=$KUBE_NS). See diagnostics above."
fi

# Exit non-zero if there was a rollout failure
if [[ "$APP_ROLLOUT_RC" -ne 0 || "$TEMP_ROLLOUT_RC" -ne 0 ]]; then
  exit 1
fi

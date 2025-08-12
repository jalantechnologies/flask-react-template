#!/usr/bin/env bash
set -euo pipefail

# WHY: Structure into small functions; keep outputs/behavior identical.

: "${KUBE_NS:?KUBE_NS is required}"
: "${KUBE_APP:?KUBE_APP is required}"

APP_DEPLOY="${KUBE_APP}-deployment"
TEMPORAL_DEPLOY="${KUBE_APP}-temporal-deployment"
ART_DIR="ci_artifacts"

main() {
  mkdir -p "$ART_DIR"

  # Always collect diagnostics at the end, even if rollout fails (same behavior)
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
}

collect_diagnostics() {
  echo "diag :: collecting diagnostics for namespace=$KUBE_NS"

  # Give kubelet time to restart/crash pods so state reflects CrashLoopBackOff
  sleep 30

  # Only events for THIS deploy (prefix = "$KUBE_APP-$KUBE_DEPLOY_ID-") and only last 45m
  local deploy_prefix cutoff
  deploy_prefix="${KUBE_APP}-${KUBE_DEPLOY_ID}-"
  cutoff="$(date -u -d '45 minutes ago' +%Y-%m-%dT%H:%M:%SZ)"

  kubectl -n "$KUBE_NS" get events -o json \
    | jq --arg p "$deploy_prefix" --arg cutoff "$cutoff" '
        .items
        | map(select(
            ((.lastTimestamp // .eventTime // .series?.lastObservedTime // "") >= $cutoff)
            and ((.involvedObject.name // "") | startswith($p))
          ))
        | sort_by(.lastTimestamp // .eventTime // .series?.lastObservedTime // "")
        | .[]
        | "\((.lastTimestamp // .eventTime // .series?.lastObservedTime // ""))\t\(.type)\t\(.reason)\t\(.involvedObject.kind)/\(.involvedObject.name)\t\(.message)"
      ' > "$ART_DIR/events.filtered.txt" || true

  # Resource overviews
  kubectl -n "$KUBE_NS" get deploy,sts,svc,pods -o wide > "$ART_DIR/resources.txt" || true

  kubectl -n "$KUBE_NS" get pods -o json \
  | jq 'del(
      .items[].spec.containers[].env?,
      .items[].spec.initContainers[].env?,
      .items[].spec.containers[].envFrom?,
      .items[].spec.initContainers[].envFrom?
    )' > "$ART_DIR/pods.sanitized.json" || true

  # Save describes for our deploys if they exist
  describe_if_present "$KUBE_NS" "$APP_DEPLOY"
  describe_if_present "$KUBE_NS" "$TEMPORAL_DEPLOY"

  # Critical services (extend this list if needed)
  for svc in temporal-grpc; do
    capture_service_health "$KUBE_NS" "$svc"
  done

  # Summaries / findings
  EVENTS="$ART_DIR/events.filtered.txt"
  PODS="$ART_DIR/pods.sanitized.json"

  # Scheduling / memory pressure
  if grep -Eq "FailedScheduling|Insufficient memory" "$EVENTS"; then
    {
      echo "- ❌ Pods could not schedule (insufficient node memory)."
      echo "  Fix: Close inactive PRs, reduce preview memory requests/limits, or scale the preview node pool."
    } >> "$ART_DIR/findings.txt"
    echo "::error ::Pods could not schedule due to insufficient memory."
  fi

  # OOMKilled signals
  if grep -q "OOMKilled" "$EVENTS"; then
    {
      echo "- ❌ A container was OOMKilled (exceeded its memory limit)."
      echo "  Fix: Increase that container’s memory limit or reduce memory usage."
    } >> "$ART_DIR/findings.txt"
    echo "::error ::A container was OOMKilled."
  fi

  # CrashLoopBackOff / Error pods (only for this app)
  if kubectl -n "$KUBE_NS" get pods -l app="$KUBE_APP" --no-headers 2>/dev/null \
    | grep -Eq "CrashLoopBackOff|Error"; then
    kubectl -n "$KUBE_NS" get pods -l app="$KUBE_APP" --no-headers \
      | awk '/CrashLoopBackOff|Error/ {print}' > "$ART_DIR/problem_pods.txt" || true
    {
      echo "- ❌ Some pods for app '$KUBE_APP' are in CrashLoopBackOff/Error."
      echo "  Fix: Inspect logs with:"
      echo "    kubectl -n $KUBE_NS logs <pod> -c <container> --tail=200"
    } >> "$ART_DIR/findings.txt"
    echo "::error ::Some '$KUBE_APP' pods are in CrashLoopBackOff/Error."
  fi

  # Start summary fresh each time
  : > "$ART_DIR/summary.md"

  {
    echo "### Deployment diagnostics – namespace \`$KUBE_NS\`"
    echo
    echo "**App:** \`$KUBE_APP\`"
    echo
    if [[ -s "$ART_DIR/findings.txt" ]]; then
      echo "#### Findings"
      cat "$ART_DIR/findings.txt"
    else
      echo "✅ No obvious scheduling, OOM, missing Service, or crash-loop issues detected."
    fi

    echo
    echo "### Recent events (latest)"
    if [ -s "$ART_DIR/events.filtered.txt" ]; then
      echo
      echo '<details><summary>Show last 20</summary>'
      echo
      # Prefer Warning events (up to 20), else last 20 of all filtered events
      if grep -q $'\tWarning\t' "$ART_DIR/events.filtered.txt"; then
        grep $'\tWarning\t' "$ART_DIR/events.filtered.txt" | tail -n 20
      else
        tail -n 20 "$ART_DIR/events.filtered.txt"
      fi
      echo
      echo '</details>'
    elif [ -s "$ART_DIR/events.txt" ]; then
      # Fallback if filtered file unavailable
      echo
      echo '<details><summary>Show last 20</summary>'
      echo
      tail -n 20 "$ART_DIR/events.txt"
      echo
      echo '</details>'
    else
      echo
      echo "_No recent events._"
    fi
  } >> "$ART_DIR/summary.md"

  echo "diag :: diagnostics collection done"

  # ✅ also append diagnostics directly to the GitHub job summary so engineers see it without artifacts
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" && -f "$ART_DIR/summary.md" ]]; then
    echo "diag :: writing diagnostics to GitHub job summary"
    cat "$ART_DIR/summary.md" >> "$GITHUB_STEP_SUMMARY" || true
  fi
}

describe_if_present() {
  local ns="$1" deploy="$2"
  if kubectl -n "$ns" get deploy "$deploy" >/dev/null 2>&1; then
    kubectl -n "$ns" describe deploy "$deploy" > "$ART_DIR/describe_${deploy}.txt" || true
  fi
}

capture_service_health() {
  local ns="$1" svc="$2"
  if kubectl -n "$ns" get svc "$svc" >/dev/null 2>&1; then
    kubectl -n "$ns" get svc "$svc" -o wide > "$ART_DIR/svc_${svc}.txt" || true
    kubectl -n "$ns" get endpoints "$svc" -o wide > "$ART_DIR/endpoints_${svc}.txt" || true
  else
    echo "❌ Missing Service '$svc' in ns=$KUBE_NS" >> "$ART_DIR/findings.txt"
    echo "::error ::Missing Service '$svc' in namespace $KUBE_NS"
  fi
}

main "$@"

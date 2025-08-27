#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# post-deploy.sh
#
# GOAL:
#   1) Wait for the app deployment (and, if present, the temporal deployment)
#      to roll out successfully.
#   2) Whether rollouts succeed or fail, collect a helpful bundle of diagnostics
#      (events, resources, sanitized pod specs, key service snapshots, etc.)
#      and write a simple human summary.
#   3) If any rollout failed, exit non-zero *after* diagnostics are saved.
#
# IMPORTANT ABOUT "trap":
#   We use a Bash "trap" to guarantee diagnostics run at the end no matter what.
#   If the script exits (success OR failure), the function `collect_diagnostics`
#   will still run. This is a very common pattern in CI scripts to ensure
#   you always get logs/artifacts, even if something fails early.
#
# REQUIRED ENV:
#   - KUBE_NS  : namespace to work in
#   - KUBE_APP : app base name (we derive deployment/service names from this)
#
# NAMING CONVENTIONS USED (matched as per repo’s expectations):
#   - App Deployment            : "${KUBE_APP}-deployment"
#   - Temporal Deployment (opt) : "${KUBE_APP}-temporal-deployment"
#   - Web Service               : "${KUBE_APP}-service"
#   - Temporal Service          : "temporal-service"
#
# OUTPUT:
#   - Files under ci_artifacts/:
#       resources.txt
#       events.filtered.txt
#       pods.sanitized.json
#       describe_<deployment>.txt
#       svc_<service>.txt
#       endpoints_<service>.txt
#       problem_pods.txt (if any)
#       findings.txt (only if issues detected)
#       summary.md  (a human-readable summary; also echoed to GH job summary)
#
# NOTES:
#   - "rollout status" waits until a Deployment is considered successfully
#     rolled out (or times out after 5 minutes here).
#   - If a rollout fails, we still keep going (thanks to the trap)
#     so we can collect evidence about what went wrong.
# -----------------------------------------------------------------------------

set -euo pipefail

# Validate required env early with friendly messages.
: "${KUBE_NS:?KUBE_NS is required}"
: "${KUBE_APP:?KUBE_APP is required}"

# Standardized names derived from KUBE_APP (must match your manifests)
APP_DEPLOY="${KUBE_APP}-deployment"
TEMPORAL_DEPLOY="${KUBE_APP}-temporal-deployment"
ART_DIR="ci_artifacts"

main() {
  # Ensure the artifacts directory exists.
  mkdir -p "$ART_DIR"

  # ----------------------------------------------------------------------------
  # The trap below is here ON PURPOSE (matches current logic exactly).
  # WHY TRAP? If anything fails anywhere below, Bash will exit, but before it
  #           fully quits it will call collect_diagnostics. That guarantees we
  #           always produce logs for debugging. Without this, a failure might
  #           end the script early and you’d get no artifacts.
  # ----------------------------------------------------------------------------
  trap 'collect_diagnostics' EXIT

  echo "rollout :: waiting for $APP_DEPLOY"

  # We temporarily turn off "exit on error" to catch the rollout exit code
  # ourselves and continue the script (so the trap still fires later).
  set +e
  kubectl rollout status deploy/"$APP_DEPLOY" -n "$KUBE_NS" --timeout=5m
  APP_ROLLOUT_RC=$?
  set -e

  # Temporal is optional; only wait if it exists.
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

  # Tell CI clearly if a rollout failed. We do NOT exit yet (the trap will
  # still run after main finishes or exits).
  if [[ "$APP_ROLLOUT_RC" -ne 0 ]]; then
    echo "::error ::Rollout did not complete for ${APP_DEPLOY} (ns=$KUBE_NS). See diagnostics above."
  fi
  if [[ "$TEMP_ROLLOUT_RC" -ne 0 ]]; then
    echo "::error ::Rollout did not complete for ${TEMPORAL_DEPLOY} (ns=$KUBE_NS). See diagnostics above."
  fi

  # If either rollout failed, exit non-zero (this will trigger the trap first).
  if [[ "$APP_ROLLOUT_RC" -ne 0 || "$TEMP_ROLLOUT_RC" -ne 0 ]]; then
    exit 1
  fi
}

collect_diagnostics() {
  echo "diag :: collecting diagnostics for namespace=$KUBE_NS"

  # Give kubelet a short moment so transient states like CrashLoopBackOff
  # have time to show up in `kubectl get pods` and events.
  sleep 30

  # We only want events related to THIS deploy attempt. We build a prefix like:
  #   "<KUBE_APP>-<KUBE_DEPLOY_ID>-"
  # and only include events for the last 45 minutes.
  local deploy_prefix cutoff
  deploy_prefix="${KUBE_APP}-${KUBE_DEPLOY_ID}-"
  cutoff="$(date -u -d '45 minutes ago' +%Y-%m-%dT%H:%M:%SZ)"

  # 1) Filter and format events into a simple, tail-able text file.
  #    (We keep just the lines we care about and print them in time order.)
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

  # 2) A quick "big picture" list of basic resources in the namespace.
  kubectl -n "$KUBE_NS" get deploy,sts,svc,pods -o wide > "$ART_DIR/resources.txt" || true

  # 3) Pods JSON (sanitized): remove env/envFrom so secrets are not leaked
  #    into CI artifacts. Everything else is kept as-is.
  kubectl -n "$KUBE_NS" get pods -o json \
  | jq 'del(
      .items[].spec.containers[].env?,
      .items[].spec.initContainers[].env?,
      .items[].spec.containers[].envFrom?,
      .items[].spec.initContainers[].envFrom?
    )' > "$ART_DIR/pods.sanitized.json" || true

  # 4) Save `kubectl describe` for our deployments (if present).
  save_deploy_describe_if_present "$KUBE_NS" "$APP_DEPLOY"
  save_deploy_describe_if_present "$KUBE_NS" "$TEMPORAL_DEPLOY"

  # 5) Check critical Services exist and record their Endpoints.
  for svc in "$KUBE_APP-service" temporal-service; do
    save_service_and_endpoints_if_present "$KUBE_NS" "$svc"
  done

  # 6) Build findings by scanning events/pods for common failure signals.
  EVENTS="$ART_DIR/events.filtered.txt"
  PODS="$ART_DIR/pods.sanitized.json"  # kept for completeness; not parsed further below

  # Scheduling / memory pressure (pods couldn't be placed on any node)
  if grep -Eq "FailedScheduling|Insufficient memory" "$EVENTS"; then
    {
      echo "- ❌ Pods could not schedule (insufficient node memory)."
      echo "  Fix: Close inactive PRs, reduce preview memory requests/limits, or scale the preview node pool."
    } >> "$ART_DIR/findings.txt"
    echo "::error ::Pods could not schedule due to insufficient memory."
  fi

  # OOMKilled (container memory limit too low or app uses more than limit)
  if grep -q "OOMKilled" "$EVENTS"; then
    {
      echo "- ❌ A container was OOMKilled (exceeded its memory limit)."
      echo "  Fix: Increase that container’s memory limit or reduce memory usage."
    } >> "$ART_DIR/findings.txt"
    echo "::error ::A container was OOMKilled."
  fi

  # CrashLoopBackOff / Error states for pods belonging to this app label.
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

  # 7) Create/overwrite the human summary file.
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
      # Fallback if a plain events file exists
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

  # 8) If we are in GitHub Actions, append the summary to the job summary panel.
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" && -f "$ART_DIR/summary.md" ]]; then
    echo "diag :: writing diagnostics to GitHub job summary"
    cat "$ART_DIR/summary.md" >> "$GITHUB_STEP_SUMMARY" || true
  fi
}

# -----------------------------------------------------------------------------
# save_deploy_describe_if_present <namespace> <deployment>
# WHAT: If the deployment exists, save a detailed "describe" snapshot to a file.
# WHY: 'describe' includes conditions, events, and replica details that are
#      often the fastest way to see *why* a rollout is stuck/failing.
# -----------------------------------------------------------------------------
save_deploy_describe_if_present() {
  local namespace="$1" deploy_name="$2"
  if kubectl -n "$namespace" get deploy "$deploy_name" >/dev/null 2>&1; then
    kubectl -n "$namespace" describe deploy "$deploy_name" > "$ART_DIR/describe_${deploy_name}.txt" || true
  fi
}

# -----------------------------------------------------------------------------
# save_service_and_endpoints_if_present <namespace> <service_name>
# WHAT: If the Service exists, save the Service and its Endpoints to separate
#       files. If it does not exist, write a finding and a CI error line.
# WHY: Many "it’s up but I can’t reach it" issues are caused by Services
#      missing selectors/endpoints. These snapshots make that obvious.
# -----------------------------------------------------------------------------
save_service_and_endpoints_if_present() {
  local namespace="$1" service_name="$2"
  if kubectl -n "$namespace" get svc "$service_name" >/dev/null 2>&1; then
    kubectl -n "$namespace" get svc "$service_name" -o wide > "$ART_DIR/svc_${service_name}.txt" || true
    kubectl -n "$namespace" get endpoints "$service_name" -o wide > "$ART_DIR/endpoints_${service_name}.txt" || true
  else
    echo "❌ Missing Service '$service_name' in ns=$KUBE_NS" >> "$ART_DIR/findings.txt"
    echo "::error ::Missing Service '$service_name' in namespace $KUBE_NS"
  fi
}

# Run the main flow (the trap ensures diagnostics always run afterward).
main "$@"

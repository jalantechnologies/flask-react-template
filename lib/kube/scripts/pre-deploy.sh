#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# pre-deploy.sh
#
# GOAL:
#   Before we spin up *one more* preview environment, do a quick "capacity
#   estimate" of cluster memory to help us avoid noisy failures later.
#
# WHAT THIS SCRIPT ACTUALLY DOES:
#   1) Makes sure the JSON tool `jq` is available (installs it if missing).
#   2) Figures out how many preview deployments for this app are already in
#      the namespace (by name prefix).
#   3) Calculates the cluster's allocatable memory in MiB (sum across nodes).
#   4) Estimates memory that would be "requested" after adding one more preview
#      (uses a single, rough constant per preview).
#   5) If the estimate is more than the allocatable memory, **warns** loudly,
#      but does NOT fail the build (soft gate).
#
# IMPORTANT: This is a *preflight* helper. We intentionally do not block deploys
#            here (to keep developer flow smooth), but we provide a strong warning
#            if capacity looks tight so someone can take action.
#
# REQUIRED ENV:
#   - KUBE_NS  : the Kubernetes namespace to check (e.g., "preview")
#   - KUBE_APP : app name like "<app>-<env>-<hash>" (we use it to build a prefix)
#
# OPTIONAL ENV:
#   - REQ_MIB_PER_PR : rough memory requested *per* preview (default 700 MiB)
#
# EXAMPLE:
#   KUBE_NS=preview KUBE_APP=myapp-preview-abcdef ./pre-deploy.sh
#
# OUTPUT:
#   - How many active previews it sees
#   - Total allocatable memory across nodes (MiB)
#   - Estimated request after this deploy
#   - A warning if the estimate is larger than allocatable memory
#
# NOTES:
#   - `kubectl` is the Kubernetes CLI (we query cluster info with it).
#   - `jq` is a tool that reads JSON; we use it to pick/transform numbers.
#   - "allocatable memory" is what the scheduler thinks is free for Pods,
#     after reserving space for the system itself.
# -----------------------------------------------------------------------------

# Safety flags:
# -e  : exit when a command fails
# -u  : error on using undefined variables
# -o pipefail : if any command in a pipeline fails, the pipeline fails
set -euo pipefail

# NS = target Kubernetes namespace (from KUBE_NS)
# If KUBE_NS is missing/empty, stop with a clear error.
NS="${KUBE_NS:-}"
: "${NS:?KUBE_NS is required}"

main() {
  echo "preflight :: capacity check (namespace=$NS)"

  # Step 1: Ensure jq exists so JSON parsing works.
  ensure_jq_is_available

  # Step 2: Pick a simple constant for per-preview memory "request" (MiB).
  #         Why constant? We're doing a quick, rough estimate, not exact math.
  REQ_MIB_PER_PR="${REQ_MIB_PER_PR:-700}"

  # Step 3: Build the base prefix so we can count *all* previews for this app.
  # KUBE_APP looks like "<app>-<env>-<hash>". We drop the trailing "-<hash>"
  # and keep "<app>-<env>-". That lets us match *every* active preview of this app.
  BASE="${KUBE_APP%-*}-" || true

  # Step 4: Ask the cluster:
  #   - how many preview deployments are active for this prefix?
  #   - how much allocatable memory (MiB) do all nodes have in total?
  ACTIVE="$(count_active_preview_deployments "$NS" "$BASE")"
  TOTAL_ALLOC_MIB="$(calculate_cluster_allocatable_memory_mebibytes)"

  # Step 5: "What if we add one more preview?" → estimate rough memory needed.
  # This is not a scheduler decision; it's just a helpful heads-up number.
  NEEDED=$(( (ACTIVE + 1) * REQ_MIB_PER_PR ))

  # Speak human:
  echo "preflight :: active previews in ns=$NS: $ACTIVE"
  echo "preflight :: allocatable memory (MiB): $TOTAL_ALLOC_MIB"
  echo "preflight :: estimated after this deploy (MiB): $NEEDED"

  # Step 6: If estimate exceeds available, warn loudly (but do not fail).
  warn_if_capacity_insufficient "$NEEDED" "$TOTAL_ALLOC_MIB"
}

# -----------------------------------------------------------------------------
# ensure_jq_is_available
# WHY: We rely on jq to parse JSON from kubectl. If it's not installed,
#      we try to install it quietly. If installs fail (e.g., no sudo),
#      later jq calls will fail, which will stop the script (that’s OK).
# -----------------------------------------------------------------------------
ensure_jq_is_available() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "preflight :: installing jq (not found)"
    sudo apt-get update -y >/dev/null 2>&1 || true
    sudo apt-get install -y jq >/dev/null 2>&1 || true
  fi
}

# -----------------------------------------------------------------------------
# count_active_preview_deployments <namespace> <base_prefix>
# WHAT: Returns a number (count). We list deployments in the namespace as JSON,
#       pick the ones whose names start with the base prefix, and count them.
# EXAMPLE:
#   base_prefix="myapp-preview-"
#   matches: "myapp-preview-abc123", "myapp-preview-deadbeef", ...
# -----------------------------------------------------------------------------
count_active_preview_deployments() {
  local namespace="$1" base_prefix="$2"
  kubectl -n "$namespace" get deploy -o json \
    | jq --arg base "$base_prefix" \
         '[.items[].metadata.name | select(startswith($base))] | length'
}

# -----------------------------------------------------------------------------
# calculate_cluster_allocatable_memory_mebibytes
# WHAT: Sums allocatable memory across all nodes, normalizing everything to MiB.
# NOTE: Kubernetes reports memory like "8191832Ki" (KiB) or "2048Mi".
#       We convert:
#         Ki → Mi by dividing by 1024
#         Mi → Mi (no change)
#         (If some other unit appears, we just parse the number part.)
# OUTPUT: A single integer (MiB, floored).
# -----------------------------------------------------------------------------
calculate_cluster_allocatable_memory_mebibytes() {
  kubectl get nodes -o json \
    | jq '[.items[].status.allocatable.memory]
           | map(
               if test("Ki$") then
                 (sub("Ki$";"") | tonumber/1024)
               elif test("Mi$") then
                 (sub("Mi$";"") | tonumber)
               else
                 tonumber
               end
             )
           | add | floor'
}

# -----------------------------------------------------------------------------
# warn_if_capacity_insufficient <needed_mib> <total_alloc_mib>
# WHAT: If our rough estimate exceeds allocatable memory, print a CI-friendly
#       error line plus practical tips. We DO NOT hard-fail here (soft gate).
# WHY: We prefer to let the deploy continue but make the risk obvious.
# -----------------------------------------------------------------------------
warn_if_capacity_insufficient() {
  local needed_mib="$1" total_alloc_mib="$2"
  if (( needed_mib > total_alloc_mib )); then
    echo "::error ::This deploy likely exceeds cluster capacity (~${needed_mib}Mi needed > ~${total_alloc_mib}Mi available)."
    echo "💡 Fix: Close older preview PRs, reduce preview memory, or scale the node pool."
    # Soft gate: don’t exit 1 unless you want to block deploys.
    # exit 1
  else
    echo "preflight :: capacity looks OK"
  fi
}

# Kick everything off.
main "$@"

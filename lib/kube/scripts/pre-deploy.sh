#!/usr/bin/env bash
set -euo pipefail

# NS = target Kubernetes namespace (from KUBE_NS)
NS="${KUBE_NS:-}"
: "${NS:?KUBE_NS is required}"

main() {
  echo "preflight :: capacity check (namespace=$NS)"

  ensure_jq_is_available

  # Per-PR preview memory request (MiB)
  REQ_MIB_PER_PR="${REQ_MIB_PER_PR:-700}"

  # KUBE_APP like: <app>-<env>-<hash> → we match <app>-<env>-
  BASE="${KUBE_APP%-*}-" || true

  ACTIVE="$(count_active_preview_deployments "$NS" "$BASE")"
  TOTAL_ALLOC_MIB="$(calculate_cluster_allocatable_memory_mebibytes)"
  NEEDED=$(( (ACTIVE + 1) * REQ_MIB_PER_PR ))

  echo "preflight :: active previews in ns=$NS: $ACTIVE"
  echo "preflight :: allocatable memory (MiB): $TOTAL_ALLOC_MIB"
  echo "preflight :: estimated after this deploy (MiB): $NEEDED"

  warn_if_capacity_insufficient "$NEEDED" "$TOTAL_ALLOC_MIB"
}

ensure_jq_is_available() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "preflight :: installing jq (not found)"
    sudo apt-get update -y >/dev/null 2>&1 || true
    sudo apt-get install -y jq >/dev/null 2>&1 || true
  fi
}

count_active_preview_deployments() {
  local namespace="$1" base_prefix="$2"
  kubectl -n "$namespace" get deploy -o json \
    | jq --arg base "$base_prefix" '[.items[].metadata.name | select(startswith($base))] | length'
}

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

main "$@"

#!/usr/bin/env bash
set -euo pipefail

# WHY: Keep the exact env/echo/behavior but structure code into small, clear units.

NS="${KUBE_NS:-}"
: "${NS:?KUBE_NS is required}"

main() {
  echo "preflight :: capacity check (namespace=$NS)"

  ensure_jq

  # TUNE THIS to your preview per-PR memory *requests* (MiB)
  REQ_MIB_PER_PR="${REQ_MIB_PER_PR:-700}"

  # Count active preview deployments within this namespace by label 'app' prefix (KUBE_APP without the hash)
  # KUBE_APP like: <app>-<env>-<hash>  → base prefix: <app>-<env>-
  BASE="${KUBE_APP%-*}-" || true

  ACTIVE="$(count_active_previews "$NS" "$BASE")"
  TOTAL_ALLOC_MIB="$(cluster_allocatable_mib)"
  NEEDED=$(( (ACTIVE + 1) * REQ_MIB_PER_PR ))

  echo "preflight :: active previews in ns=$NS: $ACTIVE"
  echo "preflight :: allocatable memory (MiB): $TOTAL_ALLOC_MIB"
  echo "preflight :: estimated after this deploy (MiB): $NEEDED"

  capacity_gate "$NEEDED" "$TOTAL_ALLOC_MIB"
}

ensure_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "preflight :: installing jq (not found)"
    sudo apt-get update -y >/dev/null 2>&1 || true
    sudo apt-get install -y jq >/dev/null 2>&1 || true
  fi
}

count_active_previews() {
  local ns="$1" base="$2"
  kubectl -n "$ns" get deploy -o json \
    | jq --arg base "$base" '[.items[].metadata.name | select(startswith($base))] | length'
}

cluster_allocatable_mib() {
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

capacity_gate() {
  local needed="$1" total="$2"
  if (( needed > total )); then
    echo "::error ::This deploy likely exceeds cluster capacity (~${needed}Mi needed > ~${total}Mi available)."
    echo "💡 Fix: Close older preview PRs, reduce preview memory, or scale the node pool."
    # Soft gate: don’t exit 1 unless you want to block deploys.
    # exit 1
  else
    echo "preflight :: capacity looks OK"
  fi
}

main "$@"

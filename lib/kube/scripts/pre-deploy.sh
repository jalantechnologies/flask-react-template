#!/usr/bin/env bash
set -euo pipefail

NS="${KUBE_NS:-}"
: "${NS:?KUBE_NS is required}"

echo "preflight :: capacity check (namespace=$NS)"

if ! command -v jq >/dev/null 2>&1; then
  echo "preflight :: installing jq (not found)"
  sudo apt-get update -y >/dev/null 2>&1 || true
  sudo apt-get install -y jq >/dev/null 2>&1 || true
fi

# TUNE THIS to your preview per-PR memory *requests* (MiB)
REQ_MIB_PER_PR="${REQ_MIB_PER_PR:-700}"

# Count active preview deployments within this namespace by label 'app' prefix (KUBE_APP without the hash)
# KUBE_APP like: <app>-<env>-<hash>  → base prefix: <app>-<env>-
BASE="${KUBE_APP%-*}-" || true
ACTIVE=$(kubectl -n "$NS" get deploy -o json \
  | jq --arg base "$BASE" '[.items[].metadata.name | select(startswith($base))] | length')

TOTAL_ALLOC_MIB=$(kubectl get nodes -o json \
  | jq '[.items[].status.allocatable.memory] | map(sub("Ki$";"")|tonumber/1024) | add | floor')

NEEDED=$(( (ACTIVE + 1) * REQ_MIB_PER_PR ))

echo "preflight :: active previews in ns=$NS: $ACTIVE"
echo "preflight :: allocatable memory (MiB): $TOTAL_ALLOC_MIB"
echo "preflight :: estimated after this deploy (MiB): $NEEDED"

if (( NEEDED > TOTAL_ALLOC_MIB )); then
  echo "::error ::This deploy likely exceeds cluster capacity (~${NEEDED}Mi needed > ~${TOTAL_ALLOC_MIB}Mi available)."
  echo "💡 Fix: Close older preview PRs, reduce preview memory, or scale the node pool."
  # Soft gate: don’t exit 1 unless you want to block deploys.
  # exit 1
else
  echo "preflight :: capacity looks OK"
fi

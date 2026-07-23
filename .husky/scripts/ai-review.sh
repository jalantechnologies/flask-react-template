#!/usr/bin/env sh

set -u

if [ "${AI_REVIEW:-1}" = "0" ]; then
  exit 0
fi

if ! ( exec </dev/tty ) 2>/dev/null; then
  exit 0
fi

detect_cmd() {
  if [ -n "${AI_REVIEW_CMD:-}" ]; then
    override_bin="${AI_REVIEW_CMD%% *}"
    if ! command -v "$override_bin" >/dev/null 2>&1; then
      echo "local-ai-review: '$override_bin' (from AI_REVIEW_CMD='${AI_REVIEW_CMD}') not found on PATH — install it or add it to PATH; if the path contains spaces, wrap it in a space-free script and point AI_REVIEW_CMD at that; or unset AI_REVIEW_CMD to auto-detect" >&2
      return 1
    fi
    printf '%s\n' "$AI_REVIEW_CMD"
    return 0
  fi
  for c in claude codex cursor-agent; do
    if command -v "$c" >/dev/null 2>&1; then
      printf '%s\n' "$c"
      return 0
    fi
  done
  return 1
}

AI_CMD=$(detect_cmd) || {
  exit 0
}

AI_BIN=$(basename "${AI_CMD%% *}")

ZERO="0000000000000000000000000000000000000000"
RANGE=""
EXTRA_REFS_PUSHED=0
FOUND_REVIEWABLE_REF=0
while read -r _local_ref local_sha _remote_ref remote_sha; do
  [ -z "${local_sha:-}" ] && continue
  [ "$local_sha" = "$ZERO" ] && continue
  FOUND_REVIEWABLE_REF=1
  if [ "$remote_sha" = "$ZERO" ] || [ -z "${remote_sha:-}" ]; then
    base=$(git merge-base origin/main "$local_sha" 2>/dev/null) || base=""
    [ -n "$base" ] && RANGE="$base..$local_sha"
  else
    RANGE="$remote_sha..$local_sha"
  fi
  while read -r _extra_local_ref extra_sha _extra_remote_ref _extra_remote_sha; do
    if [ -n "${extra_sha:-}" ] && [ "$extra_sha" != "$ZERO" ]; then
      EXTRA_REFS_PUSHED=1
      break
    fi
  done
  break
done

if [ -z "$RANGE" ] && [ "$FOUND_REVIEWABLE_REF" = "1" ]; then
  if git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' >/dev/null 2>&1; then
    RANGE='@{upstream}..HEAD'
  elif git rev-parse --verify origin/main >/dev/null 2>&1; then
    RANGE='origin/main..HEAD'
  else
    echo "local-ai-review: could not determine the pushed range — reviewing only the last commit (HEAD~1..HEAD). For full coverage, review manually with 'git diff <base>..HEAD' against your branch point." >&2
    RANGE='HEAD~1..HEAD'
  fi
fi

[ -z "$RANGE" ] && exit 0
if [ -z "$(git diff --name-only "$RANGE" 2>/dev/null)" ]; then
  exit 0
fi

if [ "$EXTRA_REFS_PUSHED" = "1" ]; then
  echo "local-ai-review: only the first pushed ref ($RANGE) was reviewed — additional refs were skipped. Push refs one at a time to review each, or review the others manually." >&2
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROMPT_FILE="$SCRIPT_DIR/ai-review-prompt.md"
if [ ! -f "$PROMPT_FILE" ]; then
  echo "local-ai-review: prompt file missing at $PROMPT_FILE — restore it with 'git checkout -- .husky/scripts/ai-review-prompt.md', then push again" >&2
  exit 0
fi

PROMPT="The diff range to review is: $RANGE

$(cat "$PROMPT_FILE")"

printf '\n'
printf '%s\n' "▶ Local AI review ($AI_BIN) on $RANGE — fixing what's certain, asking when unsure."
printf '%s\n' "  Set AI_REVIEW=0 to skip, or git push --no-verify to bypass."
printf '\n'

trap 'exit 0' INT TERM
$AI_CMD "$PROMPT" </dev/tty >/dev/tty 2>&1

exit 0

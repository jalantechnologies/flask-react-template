#!/usr/bin/env bash
set -euo pipefail

SECRET_DIR="${SECRET_DIR:-/opt/app/secrets}"

normalize_key() {
  local raw="$1"
  local upper="${raw^^}"
  local cleaned="${upper//[^A-Z0-9_]/_}"
  if [[ -z "${cleaned}" ]]; then
    return 1
  fi
  if [[ "${cleaned}" =~ ^[0-9] ]]; then
    cleaned="_${cleaned}"
  fi
  echo "${cleaned}"
}

load_env_file() {
  local env_file="$1"
  set -a
  # shellcheck disable=SC1090
  . "${env_file}"
  set +a
}

if [ -d "${SECRET_DIR}" ]; then
  for secret_path in "${SECRET_DIR}"/*; do
    [ -f "${secret_path}" ] || continue
    file_name="$(basename "${secret_path}")"
    case "${file_name}" in
      *.env)
        load_env_file "${secret_path}"
        continue
        ;;
    esac
    key="$(normalize_key "${file_name}")" || continue
    value="$(cat "${secret_path}")"
    export "${key}"="${value}"
  done
fi

exec "$@"


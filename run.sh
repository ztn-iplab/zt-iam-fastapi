#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: ./run.sh [--build]"
  echo "  --build   rebuild images before starting"
}

compose_bin=""
engine_bin=""

if command -v podman >/dev/null 2>&1; then
  if podman compose version >/dev/null 2>&1; then
    compose_bin="podman compose"
    engine_bin="podman"
  fi
fi

if [[ -z "${compose_bin}" ]] && command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    compose_bin="docker compose"
    engine_bin="docker"
  fi
fi

if [[ -z "${compose_bin}" ]]; then
  echo "Error: podman compose or docker compose is required."
  echo "Install Podman or Docker, then re-run ./run.sh"
  exit 1
fi

cleanup_containers() {
  local names=("ztn_db" "ztn_mailpit" "ztn_momo_app" "ztn_nginx")
  for name in "${names[@]}"; do
    if ${engine_bin} ps -a --format "{{.Names}}" | grep -Fxq "${name}"; then
      ${engine_bin} stop "${name}" >/dev/null 2>&1 || true
      ${engine_bin} rm "${name}" >/dev/null 2>&1 || true
    fi
  done
}

bootstrap_db() {
  ${engine_bin} exec -w /app -e PYTHONPATH=/app ztn_momo_app python scripts/bootstrap_db.py
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--build" ]]; then
  cleanup_containers
  ${compose_bin} up --build -d
  bootstrap_db
elif [[ -z "${1:-}" ]]; then
  cleanup_containers
  ${compose_bin} up -d
  bootstrap_db
else
  echo "Unknown option: ${1}"
  usage
  exit 1
fi

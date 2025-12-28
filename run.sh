#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: ./run.sh [--build]"
  echo "  --build   rebuild images before starting"
}

compose_bin=""

if command -v podman >/dev/null 2>&1; then
  if podman compose version >/dev/null 2>&1; then
    compose_bin="podman compose"
  fi
fi

if [[ -z "${compose_bin}" ]] && command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    compose_bin="docker compose"
  fi
fi

if [[ -z "${compose_bin}" ]]; then
  echo "Error: podman compose or docker compose is required."
  echo "Install Podman or Docker, then re-run ./run.sh"
  exit 1
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--build" ]]; then
  ${compose_bin} up --build -d
elif [[ -z "${1:-}" ]]; then
  ${compose_bin} up -d
else
  echo "Unknown option: ${1}"
  usage
  exit 1
fi

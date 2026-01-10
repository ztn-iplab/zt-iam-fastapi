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

detect_host_ip() {
  local ip=""
  for iface in en0 en1 en2 en3 en4; do
    ip=$(ipconfig getifaddr "${iface}" 2>/dev/null || true)
    if [[ -n "${ip}" ]]; then
      echo "${ip}"
      return 0
    fi
  done
  return 1
}

update_dns_mapping() {
  local ip="${1}"
  if [[ -z "${ip}" ]]; then
    return 0
  fi

  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Skipping dnsmasq update."
    return 0
  fi

  local conf_dir
  conf_dir="$(brew --prefix)/etc/dnsmasq.d"
  mkdir -p "${conf_dir}"

  # Remove stale mappings from previous networks.
  rm -f "${conf_dir}/localhost.localdomain.com.conf"
  # Clean any hardcoded mappings from dnsmasq.conf.
  if [[ -f "$(brew --prefix)/etc/dnsmasq.conf" ]]; then
    sed -i.bak -E "/localhost\\.localdomain(\\.com)?/d" "$(brew --prefix)/etc/dnsmasq.conf"
    rm -f "$(brew --prefix)/etc/dnsmasq.conf.bak"
  fi

  {
    echo "address=/localhost.localdomain.com/${ip}"
    echo "address=/localhost.localdomain/${ip}"
  } | sudo tee "${conf_dir}/zt-iam.conf" >/dev/null

  if command -v sudo >/dev/null 2>&1; then
    sudo brew services restart dnsmasq >/dev/null 2>&1 || true
  fi
}

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
  if [[ "${engine_bin}" == "podman" ]]; then
    podman machine start >/dev/null 2>&1 || true
  fi
  host_ip=$(detect_host_ip || true)
  update_dns_mapping "${host_ip}"
  cleanup_containers
  ${compose_bin} up --build -d
  bootstrap_db
elif [[ -z "${1:-}" ]]; then
  if [[ "${engine_bin}" == "podman" ]]; then
    podman machine start >/dev/null 2>&1 || true
  fi
  host_ip=$(detect_host_ip || true)
  update_dns_mapping "${host_ip}"
  cleanup_containers
  ${compose_bin} up -d
  bootstrap_db
else
  echo "Unknown option: ${1}"
  usage
  exit 1
fi

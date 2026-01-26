#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_PATH="$ROOT_DIR/mobile/ca_mobile_app/lib/config.dart"

usage() {
  cat <<'EOF'
Usage: ./run.sh [--ip <LAN_IP>] [--emulator]

Options:
  --ip <LAN_IP>   Use the provided LAN IP for the mobile app base URL.
  --emulator      Use Android emulator host mapping (10.0.2.2).

Examples:
  ./run.sh --ip 192.168.1.50
  ./run.sh --emulator
EOF
}

detect_ip() {
  local ip=""
  ip="$(ipconfig getifaddr en0 2>/dev/null || true)"
  if [[ -z "$ip" ]]; then
    ip="$(ipconfig getifaddr en1 2>/dev/null || true)"
  fi
  echo "$ip"
}

target_ip=""
use_emulator="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ip)
      shift
      target_ip="${1:-}"
      ;;
    --emulator)
      use_emulator="true"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift || true
done

if [[ "$use_emulator" == "true" ]]; then
  target_ip="10.0.2.2"
elif [[ -z "$target_ip" ]]; then
  target_ip="$(detect_ip)"
fi

if [[ -z "$target_ip" ]]; then
  echo "Could not determine LAN IP. Use --ip <LAN_IP>." >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Missing config: $CONFIG_PATH" >&2
  exit 1
fi

sed -i '' "s|^const String apiBaseUrl = '.*';|const String apiBaseUrl = 'http://${target_ip}:8001';|" "$CONFIG_PATH"

echo "Updated mobile base URL: http://${target_ip}:8001"
echo "Starting backend services with Podman..."
podman compose up -d --build

cat <<EOF
Done.
Next:
- For physical device: flutter run -d <DEVICE_ID> --no-devtools
- For emulator: ./run.sh --emulator (then run the app)
EOF

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"

DOMAIN="${DOMAIN:-zt-iam.com}"
ALT_DOMAIN="${ALT_DOMAIN:-ztiam.com}"
HMS_DOMAIN="${HMS_DOMAIN:-hms.com}"
MAIL_DOMAIN="${MAIL_DOMAIN:-mail.${DOMAIN}}"
CERT_FILE="${CERT_FILE:-certs/zt-iam.com.pem}"
KEY_FILE="${KEY_FILE:-private/zt-iam.com-key.pem}"
CA_CERT="${CA_CERT:-certs/zt-iam-ca.crt}"
CA_KEY="${CA_KEY:-private/zt-iam-ca.key}"
DNSMASQ_CONF="${DNSMASQ_CONF:-/opt/homebrew/etc/dnsmasq.d/ztiam.conf}"
DNSMASQ_BASE_CONF="${DNSMASQ_BASE_CONF:-/opt/homebrew/etc/dnsmasq.conf}"
DNSMASQ_DIR="${DNSMASQ_DIR:-/opt/homebrew/etc/dnsmasq.d}"

APPLY_HOSTS=1
APPLY_DNSMASQ=1
LAN_IP=""

usage() {
  cat <<EOF_USAGE
Usage: ./run.sh [options]

Starts IAM stack (db, app, nginx, mailpit), auto-detects LAN IP, and refreshes hosts/dnsmasq mappings.

Options:
  --ip <LAN_IP>           Override detected LAN IP.
  --domain <IAM_DOMAIN>   IAM domain (default: ${DOMAIN})
  --alt-domain <ALT_IAM>  Additional IAM alias (default: ${ALT_DOMAIN})
  --hms-domain <HMS>      HMS domain (default: ${HMS_DOMAIN})
  --mail-domain <MAIL>    Mail domain (default: ${MAIL_DOMAIN})
  --no-hosts              Skip /etc/hosts rewrite.
  --no-dnsmasq            Skip dnsmasq rewrite/restart.
  -h, --help              Show this help.
EOF_USAGE
}

detect_lan_ip() {
  local iface
  local ip=""

  iface="$(route -n get default 2>/dev/null | awk '/interface:/{print $2; exit}')"
  if [[ -n "$iface" ]]; then
    ip="$(ifconfig "$iface" 2>/dev/null | awk '/inet /{print $2; exit}')"
  fi

  if [[ -z "$ip" ]]; then
    ip="$(ifconfig en0 2>/dev/null | awk '/inet /{print $2; exit}')"
  fi
  if [[ -z "$ip" ]]; then
    ip="$(ifconfig en1 2>/dev/null | awk '/inet /{print $2; exit}')"
  fi

  echo "$ip"
}

unique_domains() {
  awk '!seen[$0]++'
}

join_by_space() {
  local out=""
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if [[ -z "$out" ]]; then
      out="$line"
    else
      out="$out $line"
    fi
  done
  echo "$out"
}

build_domain_regex() {
  local regex=""
  local d
  while IFS= read -r d; do
    [[ -z "$d" ]] && continue
    d="${d//./\\.}"
    if [[ -z "$regex" ]]; then
      regex="$d"
    else
      regex="$regex|$d"
    fi
  done
  echo "$regex"
}

write_with_privilege() {
  local src="$1"
  local dst="$2"

  if cp "$src" "$dst" 2>/dev/null; then
    return 0
  fi

  if command -v sudo >/dev/null 2>&1; then
    sudo cp "$src" "$dst"
    return 0
  fi

  return 1
}

ensure_domain_cert() {
  local cert_path="$ROOT_DIR/$CERT_FILE"
  local key_path="$ROOT_DIR/$KEY_FILE"
  local ca_cert_path="$ROOT_DIR/$CA_CERT"
  local ca_key_path="$ROOT_DIR/$CA_KEY"
  local ext_file
  local csr_file

  if [[ -f "$cert_path" && -f "$key_path" ]]; then
    return 0
  fi

  if [[ ! -f "$ca_cert_path" || ! -f "$ca_key_path" ]]; then
    echo "Missing CA files for trusted signing: $ca_cert_path / $ca_key_path" >&2
    echo "Expected existing trusted CA. Aborting certificate generation." >&2
    exit 1
  fi

  mkdir -p "$(dirname "$cert_path")" "$(dirname "$key_path")"
  csr_file="$ROOT_DIR/private/zt-iam.com.csr"
  ext_file="$ROOT_DIR/certs/zt-iam.com.ext"

  cat > "$ext_file" <<EOF_EXT
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names
[alt_names]
DNS.1 = ${DOMAIN}
DNS.2 = ${ALT_DOMAIN}
DNS.3 = zt-aim.com
DNS.4 = localhost
IP.1 = 127.0.0.1
EOF_EXT

  openssl genrsa -out "$key_path" 2048 >/dev/null 2>&1
  openssl req -new -key "$key_path" \
    -subj "/C=US/ST=NA/L=NA/O=ZT-IAM/OU=Local Dev/CN=${DOMAIN}" \
    -out "$csr_file" >/dev/null 2>&1
  openssl x509 -req -in "$csr_file" -CA "$ca_cert_path" -CAkey "$ca_key_path" \
    -CAcreateserial -out "$cert_path" -days 825 -sha256 -extfile "$ext_file" >/dev/null 2>&1
  rm -f "$csr_file" "$ext_file"
}

refresh_hosts_file() {
  local domains="$1"
  local lan_ip="$2"
  local domain_regex="$3"
  local tmp_hosts

  if [[ -z "$domain_regex" ]]; then
    echo "Skipping /etc/hosts rewrite: no domains provided."
    return 0
  fi

  tmp_hosts="$(mktemp)"

  awk -v re="$domain_regex" '
    {
      if ($0 ~ /^[[:space:]]*#/) { print; next }
      if ($0 ~ "(^|[[:space:]])(" re ")([[:space:]]|$)") next
      print
    }
  ' /etc/hosts > "$tmp_hosts"

  {
    echo
    echo "127.0.0.1 ${domains}"
    if [[ -n "$lan_ip" ]]; then
      echo "${lan_ip} ${domains}"
    fi
  } >> "$tmp_hosts"

  if write_with_privilege "$tmp_hosts" /etc/hosts; then
    echo "Updated /etc/hosts with de-duplicated domain mappings."
  else
    echo "Warning: failed to update /etc/hosts (needs write permission)." >&2
  fi

  rm -f "$tmp_hosts"
}

refresh_dnsmasq() {
  local lan_ip="$1"
  local domains_file="$2"
  local domain_regex="$3"
  local tmp_conf
  local tmp_base_conf

  if [[ -z "$lan_ip" ]]; then
    echo "Skipping dnsmasq update: LAN IP not detected."
    return 0
  fi

  tmp_base_conf="$(mktemp)"
  {
    echo "# Auto-generated by ZT-IAM-fastapi/run.sh"
    echo "no-hosts"
    echo "bind-interfaces"
    echo "conf-dir=/opt/homebrew/etc/dnsmasq.d,*.conf"
    echo "listen-address=127.0.0.1"
    echo "listen-address=${lan_ip}"
  } > "$tmp_base_conf"

  if write_with_privilege "$tmp_base_conf" "$DNSMASQ_BASE_CONF"; then
    echo "Updated dnsmasq base config in $DNSMASQ_BASE_CONF"
  else
    echo "Warning: failed to write $DNSMASQ_BASE_CONF (needs write permission)." >&2
    rm -f "$tmp_base_conf"
    return 0
  fi
  rm -f "$tmp_base_conf"

  # Remove stale address mappings for our domains from other dnsmasq snippets.
  if [[ -n "$domain_regex" && -d "$DNSMASQ_DIR" ]]; then
    local conf
    for conf in "$DNSMASQ_DIR"/*.conf; do
      [[ -f "$conf" ]] || continue
      if [[ "$conf" == "$DNSMASQ_CONF" ]]; then
        continue
      fi
      local tmp_other
      tmp_other="$(mktemp)"
      awk -v re="$domain_regex" '
        # Drop any stale mapping lines for managed domains.
        $0 ~ "^[[:space:]]*address=/(" re ")/" { next }
        { print }
      ' "$conf" > "$tmp_other"
      write_with_privilege "$tmp_other" "$conf" >/dev/null 2>&1 || true
      rm -f "$tmp_other"
    done
  fi

  tmp_conf="$(mktemp)"
  {
    echo "# Auto-generated by ZT-IAM-fastapi/run.sh"
    while IFS= read -r d; do
      [[ -z "$d" ]] && continue
      echo "address=/${d}/${lan_ip}"
    done < "$domains_file"
  } > "$tmp_conf"

  if write_with_privilege "$tmp_conf" "$DNSMASQ_CONF"; then
    echo "Updated dnsmasq mappings in $DNSMASQ_CONF"
  else
    echo "Warning: failed to write $DNSMASQ_CONF (needs write permission)." >&2
    rm -f "$tmp_conf"
    return 0
  fi

  rm -f "$tmp_conf"

  local restarted=0
  if command -v brew >/dev/null 2>&1; then
    if brew services stop dnsmasq >/dev/null 2>&1; then
      pkill dnsmasq >/dev/null 2>&1 || true
      brew services start dnsmasq >/dev/null 2>&1
      restarted=1
      echo "Restarted dnsmasq via brew services (clean stop/start)."
    elif command -v sudo >/dev/null 2>&1 && sudo brew services stop dnsmasq >/dev/null 2>&1; then
      sudo pkill dnsmasq >/dev/null 2>&1 || true
      sudo brew services start dnsmasq >/dev/null 2>&1
      restarted=1
      echo "Restarted dnsmasq via sudo brew services (clean stop/start)."
    else
      echo "Warning: could not restart dnsmasq automatically." >&2
    fi
  else
    echo "Warning: brew not found; restart dnsmasq manually after updating config." >&2
  fi

  # Validate that the running resolver actually bound the expected LAN IP.
  local has_loopback=0
  local has_lan=0
  if netstat -anv -p udp 2>/dev/null | awk '$4=="127.0.0.1.53" && $NF ~ /dnsmasq/ {found=1} END{exit found?0:1}'; then
    has_loopback=1
  fi
  if netstat -anv -p udp 2>/dev/null | awk -v ip="$lan_ip" '$4==(ip ".53") && $NF ~ /dnsmasq/ {found=1} END{exit found?0:1}'; then
    has_lan=1
  fi

  if [[ "$has_loopback" -eq 1 && "$has_lan" -eq 1 ]]; then
    echo "dnsmasq is listening on 127.0.0.1 and ${lan_ip}."
  else
    echo "Warning: dnsmasq did not bind expected addresses after config update." >&2
    if [[ "$restarted" -eq 1 ]]; then
      echo "A stale root-managed dnsmasq instance may still be running." >&2
    fi
    echo "Run these commands manually:" >&2
    echo "  sudo brew services stop dnsmasq" >&2
    echo "  sudo pkill dnsmasq || true" >&2
    echo "  sudo brew services start dnsmasq" >&2
    echo "  nslookup ${DOMAIN} 127.0.0.1" >&2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --ip)
      shift
      LAN_IP="${1:-}"
      ;;
    --domain)
      shift
      DOMAIN="${1:-$DOMAIN}"
      ;;
    --hms-domain)
      shift
      HMS_DOMAIN="${1:-$HMS_DOMAIN}"
      ;;
    --alt-domain)
      shift
      ALT_DOMAIN="${1:-$ALT_DOMAIN}"
      ;;
    --mail-domain)
      shift
      MAIL_DOMAIN="${1:-$MAIL_DOMAIN}"
      ;;
    --no-hosts)
      APPLY_HOSTS=0
      ;;
    --no-dnsmasq)
      APPLY_DNSMASQ=0
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

if [[ -z "$LAN_IP" ]]; then
  LAN_IP="$(detect_lan_ip)"
fi

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Missing compose file: $COMPOSE_FILE" >&2
  exit 1
fi

DOMAINS_FILE="$(mktemp)"
printf '%s\n' "$DOMAIN" "$ALT_DOMAIN" "$HMS_DOMAIN" "$MAIL_DOMAIN" | sed '/^$/d' | unique_domains > "$DOMAINS_FILE"
DOMAINS_LIST="$(join_by_space < "$DOMAINS_FILE")"
DOMAIN_REGEX="$(build_domain_regex < "$DOMAINS_FILE")"

ensure_domain_cert

echo "Starting IAM stack..."
podman compose -f "$COMPOSE_FILE" up -d --build db ztn_app nginx mailpit

if [[ "$APPLY_HOSTS" -eq 1 ]]; then
  refresh_hosts_file "$DOMAINS_LIST" "$LAN_IP" "$DOMAIN_REGEX"
else
  echo "Skipping /etc/hosts update (--no-hosts)."
fi

if [[ "$APPLY_DNSMASQ" -eq 1 ]]; then
  refresh_dnsmasq "$LAN_IP" "$DOMAINS_FILE" "$DOMAIN_REGEX"
else
  echo "Skipping dnsmasq update (--no-dnsmasq)."
fi

echo
echo "LAN IP: ${LAN_IP:-not-detected}"
echo "IAM URLs"
echo "  https://${DOMAIN}"
echo "  https://${ALT_DOMAIN}"
echo
echo "HMS URL"
echo "  https://${HMS_DOMAIN}:5443"
echo
echo "MailPit URLs"
echo "  http://${MAIL_DOMAIN}:8025"
echo "  http://localhost:8025"

rm -f "$DOMAINS_FILE"

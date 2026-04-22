#!/usr/bin/env bash
set -euo pipefail

NETWORK_NAME="${NETWORK_NAME:-training-net}"
PROJECT_ID="${OS_PROJECT_ID:-${PROJECT_ID:-}}"
TOFU_BIN="${TOFU_BIN:-tofu}"

if [[ -z "${PROJECT_ID}" ]]; then
  echo "ERROR: PROJECT_ID is not set. Export OS_PROJECT_ID (preferred) or PROJECT_ID before running reconciliation." >&2
  exit 2
fi

PLANNED_IPS=(
  "10.10.0.1"
  "10.10.0.2"
  "10.10.0.3"
  "10.10.0.4"
  "10.10.0.5"
  "10.10.0.6"
  "10.10.0.7"
  "10.10.0.8"
  "10.10.0.9"
)

ports_json="$(openstack port list --network "${NETWORK_NAME}" --project "${PROJECT_ID}" -f json)"

declare -A allocated_port_by_ip=()
declare -A allocated_name_by_ip=()
while IFS='|' read -r ip port_id port_name; do
  [[ -z "${ip}" ]] && continue
  allocated_port_by_ip["${ip}"]="${port_id}"
  allocated_name_by_ip["${ip}"]="${port_name}"
done < <(python3 - <<'PY' <<<"${ports_json}"
import json
import re
import sys

ports = json.loads(sys.stdin.read())
for port in ports:
    fixed = str(port.get("Fixed IP Addresses", ""))
    ips = re.findall(r"ip_address='(\d+\.\d+\.\d+\.\d+)'", fixed)
    for ip in ips:
        print(f"{ip}|{port.get('ID', '')}|{port.get('Name', '')}")
PY
)

declare -A managed_port_ids=()
declare -A managed_ips=()

state_resources="$(${TOFU_BIN} state list 2>/dev/null || true)"
while IFS= read -r resource; do
  [[ -z "${resource}" ]] && continue
  [[ "${resource}" != openstack_networking_port_v2.* ]] && continue

  state_show="$(${TOFU_BIN} state show -no-color "${resource}" 2>/dev/null || true)"
  [[ -z "${state_show}" ]] && continue

  port_id="$(awk -F' = ' '/^id = / {print $2; exit}' <<<"${state_show}" | tr -d '"')"
  port_ip="$(awk -F' = ' '/^    ip_address = / {print $2; exit}' <<<"${state_show}" | tr -d '"')"

  [[ -n "${port_id}" ]] && managed_port_ids["${port_id}"]=1
  [[ -n "${port_ip}" ]] && managed_ips["${port_ip}"]=1
done <<<"${state_resources}"

conflicts=()
for ip in "${PLANNED_IPS[@]}"; do
  port_id="${allocated_port_by_ip[${ip}]:-}"
  [[ -z "${port_id}" ]] && continue

  if [[ -n "${managed_port_ids[${port_id}]:-}" || -n "${managed_ips[${ip}]:-}" ]]; then
    continue
  fi

  port_name="${allocated_name_by_ip[${ip}]:-(unnamed)}"
  conflicts+=("${ip}|${port_id}|${port_name}")
done

if (( ${#conflicts[@]} > 0 )); then
  echo "ERROR: Reconciliation failed before tofu apply." >&2
  echo "The following planned static IPs for 10.10.0.0/24 are already allocated by ports not tracked in the current OpenTofu state:" >&2
  for item in "${conflicts[@]}"; do
    IFS='|' read -r ip port_id port_name <<<"${item}"
    echo "  - ${ip} -> port ${port_id} (${port_name})" >&2
  done
  echo >&2
  echo "Recovery options:" >&2
  echo "  1) Import each existing port into state (tofu import openstack_networking_port_v2.<resource_name> <port-id>)." >&2
  echo "  2) Delete stale/orphaned ports, then re-run this reconciliation step and tofu apply." >&2
  exit 1
fi

echo "Reconciliation successful: no unmanaged conflicts found for planned static IPs on ${NETWORK_NAME}."

#!/bin/bash
set -euo pipefail

RANGE_LOG="${RANGE_LOG:-/var/log/cyber_range/launch.log}"
VULN_PROFILE="${VULN_PROFILE:-baseline}"
COMPOSE_FILE="$(dirname "$0")/../docker-compose.yml"

usage() {
    echo "Usage: $0 [--down]"
    echo "Deploy or tear down the cyber range environment using Docker Compose."
    echo "Set ALLOW_NO_DOCKER=1 to start only the base services (apache2/mysql) when Docker is unavailable."
}

log() {
    mkdir -p "$(dirname "$RANGE_LOG")"
    echo "$(date) $1" >> "$RANGE_LOG"
}

start_service() {
    local service_name=$1
    if command -v systemctl >/dev/null 2>&1; then
        systemctl start "$service_name"
    else
        service "$service_name" start
    fi
}

start_alternative_services() {
    log "Starting base services without Docker"
    start_service apache2
    start_service mysql
}

deploy() {
    log "Launching cyber range with profile $VULN_PROFILE"
    docker compose -f "$COMPOSE_FILE" up -d
}

teardown() {
    log "Stopping cyber range"
    docker compose -f "$COMPOSE_FILE" down
}

case "${1:-up}" in
    --down|down)
        teardown
        ;;
    --help|-h)
        usage
        ;;
    *)
        if ! command -v docker >/dev/null 2>&1; then
            if [ "${ALLOW_NO_DOCKER:-0}" -eq 1 ]; then
                echo "Docker not found; starting base services only." >&2
                start_alternative_services
                exit 0
            fi
            echo "ERROR: docker command not found. Docker is required for full cyber range deployment." >&2
            exit 1
        fi
        if ! docker compose version >/dev/null 2>&1; then
            echo "ERROR: Docker Compose plugin is required." >&2
            exit 1
        fi
        deploy
        ;;
 esac

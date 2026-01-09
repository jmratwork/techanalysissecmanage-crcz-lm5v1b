#!/bin/bash
set -euo pipefail

SERVICE_DIR="$(dirname "$0")/../training_platform"
PYTHON_BIN="python3"
if [ -x "$SERVICE_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$SERVICE_DIR/.venv/bin/python"
fi
CLI="$PYTHON_BIN $SERVICE_DIR/cli.py"
INSTRUCTOR="${INSTRUCTOR:-instructor}"
PASSWORD="${PASSWORD:-changeme}"
COURSE_NAME="${COURSE_NAME:-PenTest 101}"
COURSE_CONTENT="${COURSE_CONTENT:-Introduction to penetration testing}"
LOG_DIR="${LOG_DIR:-/var/log/training_platform}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/courses.log}"
SERVER_LOG="${SERVER_LOG:-$LOG_DIR/server.log}"
PID_FILE="${PID_FILE:-/var/run/training_platform.pid}"

# LTI private key for KYPO integration. The key can be supplied directly
# via the LTI_TOOL_PRIVATE_KEY environment variable or mounted as a
# Docker/Podman secret at /run/secrets/lti_tool_private_key.
LTI_TOOL_PRIVATE_KEY="${LTI_TOOL_PRIVATE_KEY:-}"

# refuse to run with an insecure default instructor password
if [ "$PASSWORD" = "changeme" ]; then
    echo "ERROR: Set PASSWORD to a non-default value before starting the training platform." >&2
    exit 1
fi

# ensure LTI private key is available
if [ -z "$LTI_TOOL_PRIVATE_KEY" ]; then
    DEFAULT_SECRET=/run/secrets/lti_tool_private_key
    if [ -f "$DEFAULT_SECRET" ]; then
        LTI_TOOL_PRIVATE_KEY="$DEFAULT_SECRET"
    else
        echo "ERROR: LTI_TOOL_PRIVATE_KEY is not set and $DEFAULT_SECRET not found." >&2
        exit 1
    fi
fi

# export so child processes can access the key
export LTI_TOOL_PRIVATE_KEY

mkdir -p "$LOG_DIR" "$(dirname "$PID_FILE")"

# start service in background if not already running
if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Training platform already running with PID $(cat "$PID_FILE")."
else
    "$PYTHON_BIN" "$SERVICE_DIR/app.py" >>"$SERVER_LOG" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 1
fi

# register instructor if needed and obtain token
$CLI register --username "$INSTRUCTOR" --password "$PASSWORD" --role instructor >/dev/null 2>&1 || true
TOKEN="$($CLI login --username "$INSTRUCTOR" --password "$PASSWORD")"

# create course via API
$CLI create-course --token "$TOKEN" --title "$COURSE_NAME" --content "$COURSE_CONTENT"
echo "$(date) Instructor $INSTRUCTOR created course $COURSE_NAME" >> "$LOG_FILE"

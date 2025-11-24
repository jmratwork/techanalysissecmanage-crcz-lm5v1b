#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PLAYBOOK_DIR="${REPO_ROOT}/subcase_1b/caldera_profiles"
VALIDATOR=""
COMMIT_MESSAGE="${COMMIT_MESSAGE:-chore: update automation profiles}"

if [ ! -d "${PLAYBOOK_DIR}" ]; then
    echo "Directorio de perfiles no encontrado en ${PLAYBOOK_DIR}" >&2
    exit 1
fi

if [ -n "${VALIDATOR}" ] && [ -f "${VALIDATOR}" ]; then
    PYTHONPATH="${REPO_ROOT}" python3 "${VALIDATOR}"
fi

if ! command -v git >/dev/null 2>&1; then
    echo "git no está disponible en la ruta" >&2
    exit 1
fi

if git -C "${REPO_ROOT}" diff --quiet -- "${PLAYBOOK_DIR}"; then
    echo "No hay cambios en los perfiles de automatización para versionar"
    exit 0
fi

git -C "${REPO_ROOT}" add "${PLAYBOOK_DIR}"
if git -C "${REPO_ROOT}" commit -m "${COMMIT_MESSAGE}" >/dev/null 2>&1; then
    echo "Perfiles versionados con el mensaje: ${COMMIT_MESSAGE}"
else
    echo "No se pudo crear el commit para los perfiles" >&2
    exit 1
fi

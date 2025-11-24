#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
IDS_MODULE_PATH="${REPO_ROOT}/subcase_1b/training_platform/results_service.py"

if [ ! -f "${IDS_MODULE_PATH}" ]; then
    echo "No se encontró un módulo de analítica en ${IDS_MODULE_PATH}; se omite la actualización del modelo." >&2
    exit 0
fi

PYTHONPATH="${REPO_ROOT}" IDS_MODULE_PATH="${IDS_MODULE_PATH}" python3 - <<'PY'
import importlib.util
import os
import pathlib

module_path = pathlib.Path(os.environ["IDS_MODULE_PATH"])
spec = importlib.util.spec_from_file_location("ids_ml", module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

if hasattr(module, "train_model"):
    module.train_model()
    if hasattr(module, "log_sequence"):
        module.log_sequence("BIPS model retrained via update_bips_model.sh")
    model_file = getattr(module, "MODEL_FILE", "modelo")
    print(f"BIPS model updated: {model_file}")
else:
    print(f"No train_model function found in {module_path}; skipping model update.")
PY

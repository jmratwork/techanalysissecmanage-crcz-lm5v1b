#!/usr/bin/env python3
"""Preflight check for integration environment variables.

Validates required variables declared in ``docs/env_variables.md`` and detects
``__REQUIRED_*__`` placeholders in environment values and provisioning var files.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ENV_DOC_PATH = Path("docs/env_variables.md")
PLACEHOLDER_RE = re.compile(r"__REQUIRED_[A-Z0-9_]+__")
TABLE_VAR_RE = re.compile(r"^\|\s*`([A-Z0-9_]+)`\s*\|\s*(.+?)\s*\|\s*$")
YAML_KV_RE = re.compile(r"^\s*([A-Z0-9_]+)\s*:\s*(.*?)\s*$")


@dataclass(frozen=True)
class ComponentRule:
    name: str
    required_all: Tuple[str, ...] = ()
    required_any_groups: Tuple[Tuple[str, ...], ...] = ()


COMPONENT_RULES: Tuple[ComponentRule, ...] = (
    ComponentRule(
        name="Open edX",
        required_all=("OPENEDX_URL",),
        required_any_groups=(("OPENEDX_API_TOKEN", "OPENEDX_SESSION_COOKIE"),),
    ),
    ComponentRule(name="IRIS", required_all=("IRIS_URL", "IRIS_API_KEY")),
    ComponentRule(name="MISP", required_all=("MISP_URL", "MISP_API_KEY")),
    ComponentRule(
        name="KYPO",
        required_all=(
            "LTI_TOOL_PRIVATE_KEY",
            "LTI_CLIENT_ID",
            "LTI_DEPLOYMENT_ID",
            "KYPO_LTI_LAUNCH_URL",
        ),
    ),
)


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    if (value.startswith("\"") and value.endswith("\"")) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1].strip()
    return value


def parse_env_doc(doc_path: Path) -> Dict[str, str]:
    variables: Dict[str, str] = {}
    for line in doc_path.read_text(encoding="utf-8").splitlines():
        match = TABLE_VAR_RE.match(line)
        if match:
            variables[match.group(1)] = match.group(2)
    return variables


def infer_required_variables(var_descriptions: Dict[str, str]) -> List[str]:
    required: set[str] = set()
    for rule in COMPONENT_RULES:
        for var in rule.required_all:
            if var in var_descriptions:
                required.add(var)
        for group in rule.required_any_groups:
            for var in group:
                if var in var_descriptions:
                    required.add(var)

    for var, description in var_descriptions.items():
        if "required" in description.lower():
            required.add(var)

    return sorted(required)


def parse_yaml_like_variables(file_path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not file_path.exists():
        return values

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue
        match = YAML_KV_RE.match(line)
        if not match:
            continue
        key, value = match.groups()
        values[key] = _strip_quotes(value)
    return values


def collect_sources(file_paths: Iterable[Path]) -> Dict[str, str]:
    sourced: Dict[str, str] = {}
    for file_path in file_paths:
        sourced.update(parse_yaml_like_variables(file_path))
    return sourced


def find_placeholders(values: Dict[str, str]) -> Dict[str, str]:
    placeholders: Dict[str, str] = {}
    for var, value in values.items():
        if not value:
            continue
        match = PLACEHOLDER_RE.search(value)
        if match:
            placeholders[var] = match.group(0)
    return placeholders


def is_set(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip()
    if not normalized:
        return False
    return PLACEHOLDER_RE.fullmatch(normalized) is None


def component_status(rule: ComponentRule, values: Dict[str, str | None]) -> Tuple[bool, List[str]]:
    missing: List[str] = []

    for var in rule.required_all:
        if not is_set(values.get(var)):
            missing.append(var)

    for group in rule.required_any_groups:
        if not any(is_set(values.get(var)) for var in group):
            missing.append(" o ".join(group))

    return (len(missing) == 0, missing)


def build_effective_values(required_vars: Iterable[str], file_values: Dict[str, str]) -> Dict[str, str | None]:
    effective: Dict[str, str | None] = {}
    for var in required_vars:
        env_value = os.getenv(var)
        effective[var] = env_value if env_value is not None else file_values.get(var)
    return effective


def resolve_default_var_files() -> List[Path]:
    candidates = [
        Path("provisioning/group_vars/all.yml"),
        Path("provisioning/group_vars/subcase_1b.yml"),
    ]

    existing = [path for path in candidates if path.exists()]
    if existing:
        return existing

    return [
        Path("provisioning/group_vars/all.example.yml"),
        Path("provisioning/group_vars/subcase_1b.example.yml"),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validates required variables from docs/env_variables.md and detects "
            "placeholders __REQUIRED_*__."
        )
    )
    parser.add_argument(
        "--env-doc",
        default=str(ENV_DOC_PATH),
        help="Ruta al documento markdown con la tabla de variables.",
    )
    parser.add_argument(
        "--vars-file",
        action="append",
        default=[],
        help="Archivo YAML de variables a inspeccionar (puede repetirse).",
    )
    args = parser.parse_args()

    env_doc = Path(args.env_doc)
    if not env_doc.exists():
        print(f"ERROR: Variable file not found: {env_doc}")
        return 2

    var_descriptions = parse_env_doc(env_doc)
    if not var_descriptions:
        print(f"ERROR: No se encontraron variables en la tabla de {env_doc}")
        return 2

    required_vars = infer_required_variables(var_descriptions)
    var_files = [Path(path) for path in args.vars_file] if args.vars_file else resolve_default_var_files()
    file_values = collect_sources(var_files)

    effective_values = build_effective_values(required_vars, file_values)

    placeholder_sources = dict(file_values)
    placeholder_sources.update({var: value for var, value in os.environ.items() if var in required_vars})
    placeholders = find_placeholders(placeholder_sources)

    print("Preflight de integraciones externas")
    print(f"Documento de referencia: {env_doc}")
    print("Archivos inspeccionados:")
    for path in var_files:
        suffix = "(no existe)" if not path.exists() else ""
        print(f"  - {path} {suffix}".rstrip())
    print()

    global_missing_set: set[str] = set()
    for rule in COMPONENT_RULES:
        ready, missing = component_status(rule, effective_values)
        status_label = "READY" if ready else "NOT READY"
        print(f"[{status_label}] {rule.name}")
        if ready:
            print(" - Integration ready for deployment.")
        else:
            global_missing_set.update(missing)
            for missing_item in missing:
                print(
                    " - Action: define a valid variable for "
                    f"{missing_item} (shell o group_vars) y vuelve a ejecutar el preflight."
                )
        print()

    if placeholders:
        print("Placeholders detectados (__REQUIRED_*__):")
        for var in sorted(placeholders):
            print(f"  - {var} = {placeholders[var]}")
        print("Action: Replace these placeholders with real values ​​before displaying.")
        print()

    if global_missing_set:
        print("Global result: NOT READY")
        print("Variables obligatorias pendientes:")
        for var in sorted(global_missing_set):
            print(f"  - {var}")
        return 1

    if placeholders:
        print("Global result: NOT READY (there are pending placeholders)")
        return 1

    print("Global result: READY")
    return 0


if __name__ == "__main__":
    sys.exit(main())

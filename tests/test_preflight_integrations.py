from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_preflight_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "preflight_integrations.py"
    spec = importlib.util.spec_from_file_location("preflight_integrations", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


preflight = _load_preflight_module()


def _write_env_doc(tmp_path: Path) -> None:
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "env_variables.md").write_text(
        "| Variable | Descripción |\n"
        "| --- | --- |\n"
        "| `OPENEDX_URL` | required |\n"
        "| `OPENEDX_API_TOKEN` | required |\n"
        "| `IRIS_URL` | required |\n"
        "| `IRIS_API_KEY` | required |\n"
        "| `MISP_URL` | required |\n"
        "| `MISP_API_KEY` | required |\n"
        "| `LTI_TOOL_PRIVATE_KEY` | required |\n"
        "| `LTI_CLIENT_ID` | required |\n"
        "| `LTI_DEPLOYMENT_ID` | required |\n"
        "| `KYPO_LTI_LAUNCH_URL` | required |\n",
        encoding="utf-8",
    )


def _set_required_integration_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENEDX_URL", "https://openedx.example")
    monkeypatch.setenv("OPENEDX_API_TOKEN", "token")
    monkeypatch.setenv("IRIS_URL", "https://iris.example")
    monkeypatch.setenv("IRIS_API_KEY", "iris-key")
    monkeypatch.setenv("MISP_URL", "https://misp.example")
    monkeypatch.setenv("MISP_API_KEY", "misp-key")
    monkeypatch.setenv("LTI_TOOL_PRIVATE_KEY", "private-key")
    monkeypatch.setenv("LTI_CLIENT_ID", "client-id")
    monkeypatch.setenv("LTI_DEPLOYMENT_ID", "deployment-id")
    monkeypatch.setenv("KYPO_LTI_LAUNCH_URL", "https://kypo.example/launch")


def _run_preflight(tmp_path: Path, monkeypatch, capsys) -> tuple[int, str]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.argv", ["preflight_integrations.py"])
    exit_code = preflight.main()
    output = capsys.readouterr().out
    return exit_code, output


def test_fails_when_subcase_1b_yml_is_missing(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_env_doc(tmp_path)
    (tmp_path / "provisioning" / "group_vars").mkdir(parents=True, exist_ok=True)

    _set_required_integration_env(monkeypatch)
    exit_code, output = _run_preflight(tmp_path, monkeypatch, capsys)

    assert exit_code == 1
    assert "No existe provisioning/group_vars/subcase_1b.yml." in output


def test_fails_for_docker_with_placeholders(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_env_doc(tmp_path)
    group_vars_dir = tmp_path / "provisioning" / "group_vars"
    group_vars_dir.mkdir(parents=True, exist_ok=True)
    (group_vars_dir / "subcase_1b.yml").write_text(
        "bips_install_method: docker\n"
        "bips_docker_enabled: true\n"
        "bips_docker_image: __REQUIRED_BIPS_IMAGE__\n"
        "bips_docker_tag: stable\n",
        encoding="utf-8",
    )

    _set_required_integration_env(monkeypatch)
    exit_code, output = _run_preflight(tmp_path, monkeypatch, capsys)

    assert exit_code == 1
    assert "Validación BIPS fallida" in output
    assert "bips_docker_image" in output


def test_passes_for_docker_with_valid_values(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_env_doc(tmp_path)
    group_vars_dir = tmp_path / "provisioning" / "group_vars"
    group_vars_dir.mkdir(parents=True, exist_ok=True)
    (group_vars_dir / "subcase_1b.yml").write_text(
        "bips_install_method: docker\n"
        "bips_docker_enabled: true\n"
        "bips_docker_image: ghcr.io/acme/bips\n"
        "bips_docker_tag: 1.2.3\n",
        encoding="utf-8",
    )

    _set_required_integration_env(monkeypatch)
    exit_code, output = _run_preflight(tmp_path, monkeypatch, capsys)

    assert exit_code == 0
    assert "Global result: READY" in output


def test_fails_for_deb_with_empty_values(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_env_doc(tmp_path)
    group_vars_dir = tmp_path / "provisioning" / "group_vars"
    group_vars_dir.mkdir(parents=True, exist_ok=True)
    (group_vars_dir / "subcase_1b.yml").write_text(
        "bips_install_method: deb\n"
        "bips_repo_url: ''\n"
        "bips_package_path: /tmp/bips.deb\n"
        "bips_package_checksum: ''\n",
        encoding="utf-8",
    )

    _set_required_integration_env(monkeypatch)
    exit_code, output = _run_preflight(tmp_path, monkeypatch, capsys)

    assert exit_code == 1
    assert "Validación BIPS fallida" in output
    assert "bips_repo_url" in output
    assert "bips_package_checksum" in output


def test_passes_for_deb_with_valid_values(tmp_path: Path, monkeypatch, capsys) -> None:
    _write_env_doc(tmp_path)
    group_vars_dir = tmp_path / "provisioning" / "group_vars"
    group_vars_dir.mkdir(parents=True, exist_ok=True)
    (group_vars_dir / "subcase_1b.yml").write_text(
        "bips_install_method: deb\n"
        "bips_repo_url: https://packages.example.local/repo\n"
        "bips_package_path: bips_1.0.0_amd64.deb\n"
        "bips_package_checksum: sha256:deadbeef\n",
        encoding="utf-8",
    )

    _set_required_integration_env(monkeypatch)
    exit_code, output = _run_preflight(tmp_path, monkeypatch, capsys)

    assert exit_code == 0
    assert "Global result: READY" in output

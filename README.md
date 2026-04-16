# TechAnalysisSecManage CRCZ

This repository provides complete, ready‑to‑deploy instructions for CyberRangeCZ scenario using only the NG‑SOC components from the activity diagram: BIPS, NG‑SIEM, NG‑SOAR, CICMS, etc. It includes file layouts, Ansible roles, and step‑by‑step workflows so instructors and trainees can complete the training without confusion. The scenario delivers penetration testing and vulnerability assessment training through a dedicated platform and Cyber Range simulation. This repository contains materials for deploying and managing security analysis exercises on CyberRangeCZ using this platform.

## Prerequisites

- Active account on [CyberRangeCZ](https://www.cyberrange.cz/) with permissions to deploy cyber range scenarios.
- SSH access to the range and ability to run privileged commands.
- Local tools: `git`, `kubectl`, `helm`, and a modern web browser.
- Recommended familiarity with the CyberRangeCZ interface and the training platform runner used in Subcase 1b.
- The provided startup scripts rely on `systemctl`. If your environment lacks systemd, set `DIRECT_START=1` to attempt starting services with legacy `service` commands or direct scripts.
- Prepare required environment variables such as `LTI_TOOL_PRIVATE_KEY` and `OPENEDX_URL` as described in [docs/env_variables.md](docs/env_variables.md).

## Deployment on CRCZ

See [deployment manual](docs/deployment_manual.md) for detailed steps including VM preparation, service orchestration, teardown, and environment reset.

## Fuente canónica única (Subcaso 1b)

Para evitar derivaciones entre árboles legacy y wrappers, este repositorio define una única fuente canónica de aprovisionamiento:

- **Playbook canónico:** `provisioning/playbook.yml`
- **Inventario canónico:** `provisioning/inventory.ini`

Wrappers soportados (solo compatibilidad de rutas):

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Regla operativa: ejecuta aprovisionamiento manual únicamente con:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

No mantengas ni introduzcas lógica de aprovisionamiento paralela en `sandboxes/` o en `subcase_1b/ansible/roles/**`.

Los archivos de `subcase_1b/ansible/roles/**` se conservan como snapshot legado para trazabilidad y no deben considerarse fuente de verdad ni runtime del flujo principal.

## CI checks (equivalentes locales)

Estos son los mismos comandos ejecutados por `.github/workflows/ci.yml`:

```bash
yamllint .
ansible-lint provisioning/
ansible-playbook --syntax-check -i provisioning/inventory.ini provisioning/playbook.yml
PYTHONPATH=. pytest tests/ soc_alerts/tests/
```


## Estado de aprovisionamiento por host (playbook canónico)

El aprovisionamiento canónico de Subcaso 1b vive en `provisioning/playbook.yml`.
La decisión actual por host es:

- `training_platform`: provisión activa (`training_platform`).
- `trainee_workstation`: provisión activa (`trainee_workstation`).
- `cyber_range`: provisión activa (`cyber_range_setup`).
- `randomization_platform`: **sí tiene provisión mínima activa** mediante un rol dedicado (`randomization_platform`) que instala runtime mínimo (bash), crea directorios de logs y despliega/ejecuta el script artefacto como servicio systemd.
- `bips`: provisión activa (`common_bootstrap` + `bips`).
- `ng_siem`: provisión activa (`common_bootstrap` + `ng_siem`).
- `cicms`: provisión activa (`common_bootstrap` + `cicms`).
- `ng_soar`: provisión activa (`common_bootstrap` + `ng_soar`).
- `router`: **sin provisión activa funcional** en este repositorio; se mantiene un rol explícito `router_noop` con `assert`/`debug` para dejar esta condición visible y evitar silencio ambiguo.

Host/grupo legado aislado:

- `soc_server`: **deprecado/legacy**. No está en el inventario canónico ni se debe usar para ejecutar `provisioning/playbook.yml`.

Verificación rápida por host (flujo canónico):

- `ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit randomization_platform` valida la provisión mínima real de `randomization_platform`.
- `ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit router` ejecuta el no-op explícito (`router_noop`) y deja trazabilidad visible.
- **No ejecutar** `--limit soc_server`: ese grupo no forma parte del inventario canónico de Subcaso 1b.

Para detalles operativos y comandos Ansible exactos, consulta `provisioning/README.md`.


1. **Clone the Repository**
   ```bash
   git clone https://github.com/example/techanalysissecmanage-crcz.git
   cd techanalysissecmanage-crcz
   ```
2. **Authenticate to CyberRangeCZ** – Ensure VPN or direct connectivity and log into the portal.
3. **Prepare the Scenario** – Upload the penetration testing helper scripts from `subcase_1b/scripts/` to the appropriate CRCZ repositories so they are accessible to the exercise.
4. **Launch the Cyber Range** – Use `subcase_1b/scripts/cyber_range_start.sh` to start the simulated environment for Subcase 1b and provision the trainee workstation.
5. **Start the Training Platform (canónico)** – Provisiona `training_platform` desde Ansible canónico:
   ```bash
   ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit training_platform
   ```
   `subcase_1b/scripts/training_platform_start.sh` se mantiene como helper de compatibilidad/lab (no como flujo operativo principal).

### Phishing Quiz Module

Tras aprovisionar `training_platform` por el flujo canónico, la aplicación incluye un phishing-awareness quiz. Si usas el helper legacy `subcase_1b/scripts/training_platform_start.sh`, define `PASSWORD` con un valor fuerte antes de arrancar. Una vez activo el servicio, puedes usar:

- `GET /quiz/start` – obtain questions.
- `POST /quiz/submit` – send answers and record the score.
- `GET /quiz/score` – retrieve stored scores per user and course.

See [`docs/subcase_1b_guide.md`](docs/subcase_1b_guide.md) for detailed examples.

### Tool Launch Endpoint

The training platform also provides a `POST /launch_tool` route to run
predefined **Nmap**, **ZAP**, or **Caldera** operations against the KYPO
subnet. Supply the authentication `token` and desired `tool` in the JSON
body to start a job. The response returns a `job_id` and initial
`status`. Poll `GET /launch_tool/<job_id>?token=...` to obtain the latest
status and command output, allowing the UI to show progress or completion
to the trainee.

### Importing Open edX Content

Sample lessons and a quiz are provided under `open_edx/course`. To load this material into Open edX Studio:

1. Archive the directory:
   ```bash
   zip -r phishing_course.zip open_edx/course
   ```
2. In Studio, open the target course and navigate to **Tools → Import**.
3. Upload `phishing_course.zip` to add the lessons and quiz.

### IRIS Case Closure Automation

The repository includes `scripts/iris_case_closed_poll.py`, a helper that
polls an IRIS case-management instance for cases marked as **closed**. When a
newly closed case is discovered it will:

1. Run `subcase_1b/scripts/collect_artifacts.sh` to gather
   post-incident evidence.
2. Tag the associated MISP event with `lessons learned` via the MISP API.

Configuration is handled through environment variables such as `IRIS_URL`,
`IRIS_API_KEY`, `MISP_URL`, and `MISP_API_KEY`. Execute the script with:

```bash
python scripts/iris_case_closed_poll.py
```

The script keeps track of processed case IDs in `scripts/.iris_processed_cases.json`
to avoid duplicate reports.

## Teardown

1. Stop the scenario from the CRCZ dashboard.
2. Remove any temporary resources or virtual machines associated with the exercise.
3. Archive logs and reports for after-action review.
4. Verify that no residual network configurations remain on CyberRangeCZ.

## Troubleshooting and Tool References

- **Connectivity Issues** – Confirm VPN status and that required ports (e.g., 22 for SSH) are open.
- **Scenario Fails to Start** – Ensure the Subcase 1b helper scripts are uploaded and that the repository path is correct.
- **Training Platform Logs** – Refer to the `subcase_1b/scripts` directory for runner logs and consult [`docs/subcase_1b_guide.md`](docs/subcase_1b_guide.md) for expected service behavior.

Additional theoretical background and workflow guidance can be found in [`docs/training_workflows.md`](docs/training_workflows.md). For day‑to‑day alert handling, analysts should review the [`SOC Analyst Playbook`](docs/soc_analyst_playbook.md).

## Known limitations / TODOs reales

- El host `router` permanece como no-op documentado (`router_noop`), sin tareas de hardening/enrutamiento aplicadas desde este repositorio.
- El grupo `soc_server` está aislado como legado: no forma parte del flujo canónico de aprovisionamiento.
- La carpeta `subcase_1b/ansible/roles/**` sigue siendo legacy (compatibilidad); los cambios funcionales deben aplicarse en `provisioning/roles/**`.
- Persisten dependencias de integraciones externas (Open edX, IRIS, MISP, KYPO) que requieren credenciales y endpoints válidos fuera de este repositorio.

## Scenario Resources

- [Subcase 1b resources](docs/subcase_1b_guide.md)

## CRCZ/KYPO Training Packaging

After adding or modifying sandbox definitions, you can validate and publish the training module using the `kypo` CLI:

1. **Validate** the training specification:
   ```bash
   kypo training validate training.yaml
   ```
2. **Pack** the training for distribution:
   ```bash
   kypo training pack training.yaml
   ```
3. **Publish** the package to a KYPO portal:
   ```bash
   kypo training publish training.yaml
   ```
   The publish command expects authentication details appropriate for your CRCZ/KYPO instance.

### Sandbox agenda definition

The sandbox agenda is defined in two forms. `sandboxes/sandbox_agenda.yaml`
contains the agenda steps list that KYPO expects in the **Sandbox Agenda** field
(a top-level YAML sequence). The full sandbox definition with metadata lives in
`sandboxes/sandbox_agenda_definition.yaml`. If you upload a file with the wrapper
structure instead of the direct list, KYPO raises the error “Expected a
SequenceNode start”, because it expects a YAML sequence as the top-level node.
The agenda steps **must** be a flat sequence of `- action: ...` entries (no
`phase`/`steps` wrappers). The same topology and provisioning files referenced in
`training.yaml` are reused, so validation and packaging work identically while
providing clearer handoff notes for instructors.

> ⚠️ **Sube únicamente `sandboxes/sandbox_agenda_ui.yaml` en el campo _Sandbox Agenda_.** Debe ser una secuencia plana (lista de `- action: ...`). No uses `sandbox_agenda_definition.yaml` en la UI de KYPO.

> ℹ️ **Required topology**: when creating the topology in KYPO, use the exact name `subcase-1b-topology` (as shown in [`sandboxes/topology_subcase_1b.yaml`](sandboxes/topology_subcase_1b.yaml)) and select the file `sandboxes/topology_subcase_1b.yaml`. In the KYPO form, fill in the key fields with these values to avoid introducing variants such as `subcase_to_topology`:
>
> - **Topology name**: `subcase-1b-topology`
> - **Topology YAML**: `sandboxes/topology_subcase_1b.yaml`
> - **Description (optional)**: “Subcase 1b topology for NG‑SOC labs”
>
> This example matches the definition included in this repository and prevents discrepancies during packaging and publication.

#### CLI walkthrough

Use the KYPO CLI (or the equivalent KYPO UI steps) to reproduce the agenda-driven
workflow with the exact repository files. The examples below assume you are
already authenticated in the target KYPO instance.

> ✅ **Validate the agenda after every change**: any time you edit
> `sandboxes/sandbox_agenda.yaml`, run a YAML/sequence validation before
> publishing. For example:
> ```bash
> kypo sandbox validate sandboxes/sandbox_agenda.yaml
> ```
> This ensures the agenda remains a valid top-level sequence and catches syntax
> regressions before upload.

1. **Import the topology** with the expected name and YAML:
   ```bash
   kypo sandbox topology import \
     --name subcase-1b-topology \
     sandboxes/topology_subcase_1b.yaml
   ```
   *UI:* In **Sandboxes → Topologies**, choose **Import topology**, select the
   `sandboxes/topology_subcase_1b.yaml` file, and set the **Name** to
   `subcase-1b-topology`.

2. **Create the sandbox** from the agenda without adding wrapper keys. The YAML
   must start directly with the sequence to avoid `SequenceNode` parse errors:
   ```bash
   kypo sandbox create \
     --topology subcase-1b-topology \
     sandboxes/sandbox_agenda.yaml
   ```
   *UI:* In **Sandboxes → Create sandbox**, select the `subcase-1b-topology`
   topology and upload `sandboxes/sandbox_agenda.yaml` as-is. Do not insert
   extra root fields (for example, `version:` or a wrapper object), because the
   parser requires the top-level sequence.

3. **Verify the provisioning playbook association** so that machines are
   configured automatically during creation:
   ```bash
   kypo sandbox show subcase-1b-topology
   ```
   Confirm the listed provisioning playbook points to the agenda entry that
   references `sandboxes/provisioning_subcase_1b/site.yml`.

   > Compatibility note: `sandboxes/provisioning_subcase_1b/site.yml` is a
   > wrapper that imports the canonical entrypoint `provisioning/playbook.yml`.
   > To avoid drift, run Ansible manually only with:
   > `ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml`.

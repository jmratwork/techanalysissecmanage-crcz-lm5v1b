# Provisioning Playbook

`provisioning/playbook.yml` is the **canonical entrypoint** of Subcase 1b provisioning.
The canonical inventory is `provisioning/inventory.ini`.

## Precedence rule (canonical vs wrappers)

Formal repository reference contract: [`docs/canonical_provisioning_contract.md`](../docs/canonical_provisioning_contract.md).


Order of precedence for Subcase 1b:

1. `provisioning/playbook.yml` + `provisioning/inventory.ini` (**canonical**).
2. `sandboxes/provisioning_subcase_1b/site.yml` (**wrapper** for compatibility).
3. `subcase_1b/ansible/playbook.yml` (**wrapper** for legacy compatibility).

Wrappers must not contain alternative or divergent functional logic.

## Flujo recomendado (docker mode)

Always run from the root of the repository and follow this order:

1. **Copiar archivos de ejemplo a archivos reales**:
   ```bash
   cp provisioning/group_vars/all.example.yml provisioning/group_vars/all.yml
   cp provisioning/group_vars/subcase_1b.example.yml provisioning/group_vars/subcase_1b.yml
   ```
2. **Fill required variables** in `all.yml` and `subcase_1b.yml` (images, tags, credentials and other `__REQUIRED_*__` placeholders).
3. **Mandatory external integrations preflight**:
   ```bash
   python scripts/preflight_integrations.py
   ```
   This step validates required variables defined in `docs/env_variables.md`, detects `__REQUIRED_*__` placeholders, and must return `READY` before deployment.
4. **Ejecutar el playbook**:
   ```bash
   ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
   ```

> Importante: antes de ejecutar en docker mode, deben existir los archivos reales `provisioning/group_vars/all.yml` y `provisioning/group_vars/subcase_1b.yml`.

### Explicit consistency: topology ↔ inventory ↔ playbook

Topology reference for Subcase 1b: `sandboxes/topology_subcase_1b.yaml`.

| Canonical Host | IP in topology (`sandboxes/topology_subcase_1b.yaml`) | Group in `provisioning/inventory.ini` | Role applied in `provisioning/playbook.yml` |
|---|---|---|---|
| `training_platform` | `10.10.0.2` | `training_platform` | `training_platform` |
| `trainee_workstation` | `10.10.0.3` | `trainee_workstation` | `trainee_workstation` |
| `cyber_range` | `10.10.0.4` | `cyber_range` | `cyber_range_setup` |
| `randomization_platform` | `10.10.0.5` | `randomization_platform` | `randomization_platform` |
| `bips` | `10.10.0.6` | `bips` | `common_bootstrap` + `bips` |
| `ng_siem` | `10.10.0.7` | `ng_siem` | `common_bootstrap` + `ng_siem` |
| `cicms` | `10.10.0.8` | `cicms` | `common_bootstrap` + `cicms` |
| `ng_soar` | `10.10.0.9` | `ng_soar` | `common_bootstrap` + `ng_soar` |
| `router` | `10.10.0.1` | `router` | `router_noop` ​​(explicit no-op, final decision out of scope) |

Notas de coherencia:
- `inventory.ini` uses `ansible_host=<hostname>` (resolution by name), so topology IP values ​​are not duplicated in the canonical inventory.
- `soc_server` does not exist in the topology or canonical inventory of Subcase 1b.

### Contrato de direccionamiento de `training-net`

- Subred: `10.10.0.0/24`.
- Gateway/router reservado: `10.10.0.1`.
- IPs estáticas de servicios (sin DHCP): `10.10.0.2-10.10.0.9`.
- Pool DHCP permitido para asignación dinámica: `10.10.0.20-10.10.0.254`.

Este contrato debe mantenerse en:

1. `topology.yml` y `sandboxes/topology_subcase_1b.yaml` (definición de red).
2. `scripts/generate_deploy_tf.py` y `deploy.tf` regenerado (`openstack_networking_subnet_v2` con `allocation_pool`).

Antes de `tofu apply`, ejecuta reconciliación de puertos para detectar conflictos de IP estática no gestionados por estado:

```bash
tofu init
tofu plan
OS_PROJECT_ID=<target-project-id> ./scripts/reconcile_training_net_ports.sh
tofu apply
```

El script falla de forma explícita si `10.10.0.1` o `10.10.0.2-10.10.0.9` ya están asignadas por puertos existentes fuera del estado OpenTofu. En ese caso, recupera con una de estas opciones:

- Importar puertos existentes al estado (`tofu import openstack_networking_port_v2.<resource_name> <port-id>`).
- Eliminar puertos huérfanos/obsoletos (`openstack port delete <port-id>`) y reintentar.

Validación post-despliegue (OpenStack):

```bash
openstack port list --network training-net --device-owner network:dhcp -f value -c "Fixed IP Addresses"
```

Las IPs reportadas para puertos DHCP no deben pertenecer al bloque `10.10.0.1-10.10.0.19`.

#### Verifiable coherence contract (source of truth)

To consider the state **consistent** between topology, inventory and canonical playbook, these rules must be met simultaneously:

1. Every host declared in `sandboxes/topology_subcase_1b.yaml` (`training_platform`, `trainee_workstation`, `cyber_range`, `randomization_platform`, `bips`, `ng_siem`, `cicms`, `ng_soar`, `router`) exists as a canonical host/group in `provisioning/inventory.ini`.
2. Each canonical group in `provisioning/inventory.ini` has exactly one corresponding `hosts:` block in `provisioning/playbook.yml` (with `router` pointing to `router_noop`).
3. The aggregate group `subcase_1b:children` contains only canonical Subcase 1b groups (no legacy aliases or dummy groups like `soc_server`).
4. Any change in naming or role assignment must update **in the same delivery** this consistency table and the main documentation.

### Grupos reales del inventario

Los grupos definidos actualmente en `provisioning/inventory.ini` son:

- `training_platform`
- `trainee_workstation`
- `cyber_range`
- `randomization_platform`
- `bips`
- `ng_siem`
- `cicms`
- `ng_soar`
- `router`
- `subcase_1b` (parent group via `:children`)

> Note: the `soc_server` group is **deprecated** and should not be used.
> It is maintained only as an isolated legacy reference outside of the canonical flow.

## What is deployed locally vs external integrations

### Local deployment (within topology/lab)

El playbook `provisioning/playbook.yml` aplica roles locales sobre estos grupos:

- `all` → `logging`
- `training_platform` → `training_platform`
- `trainee_workstation` → `trainee_workstation`
- `cyber_range` → `cyber_range_setup`
- `bips` → `common_bootstrap` + `bips`
- `cicms` → `common_bootstrap` + `cicms`
- `ng_siem` → `common_bootstrap` + `ng_siem`
- `ng_soar` → `common_bootstrap` + `ng_soar`
- `randomization_platform` → `randomization_platform` (real minimum provision: bash runtime, logs directory, artifact script and systemd service)
- `router` → `router_noop` ​​(explicit no-op with `assert` + `debug`: “no active provisioning in this repository”)

Final scoping decision for `router`:
- In this repository, managed network provisioning (NAT/firewall/routing) is **not** implemented.
- The expected canonical behavior is to keep `router_noop` ​​as an explicit contract.

### Estado exacto por host (activo vs no-op)

- **Hosts con rol activo**: `training_platform`, `trainee_workstation`, `cyber_range`, `randomization_platform`, `bips`, `ng_siem`, `cicms`, `ng_soar`.
- **Host documentado como no-op**: `router` (rol `router_noop`).
- **Host/grupo legacy aislado**: `soc_server` (no inventariado en `provisioning/inventory.ini`, no ejecutar `--limit soc_server`).

#### Explicit acceptance criteria (complete project without managed router)

The provisioning state is considered **complete** even if `router` remains no-op when simultaneously satisfied:

1. `router` is present in canonical topology + inventory + playbook.
2. `router` points only to `router_noop`.
3. There is no active network automation for `router` in `provisioning/roles/**`.
4. The canonical documentation expressly maintains that the managed router is out of scope.

### External integrations (not provisioned as services here)

These platforms are consumed via variables/config, but are **not** raised as part of this playbook:

- **Open edX**: `training_platform` integration for authentication/gradebook/LTI.
- **MISP**: integration for CTI/events from scripts and services.
- **IRIS**: integration for case management via scripts (`rules_to_iris_bridge.py`, `iris_case_closed_poll.py`).

## Variables requeridas y opcionales

The central reference for environment variables is at:

- [`docs/env_variables.md`](../docs/env_variables.md)

Resumen operativo para provisioning:

### Required (if you enable external integration)

- Open edX: `OPENEDX_URL` y credenciales (`OPENEDX_API_TOKEN` o `OPENEDX_SESSION_COOKIE`).
- MISP: `MISP_URL` y `MISP_API_KEY`.
- IRIS: `IRIS_URL` (y normalmente `IRIS_API_KEY` en entornos protegidos).
- LTI/KYPO (training platform): `LTI_TOOL_PRIVATE_KEY`, `LTI_CLIENT_ID`, `LTI_DEPLOYMENT_ID`.

### Opcionales

- Open edX gradebook: `OPENEDX_GRADEBOOK_ENDPOINT`, `OPENEDX_GRADEBOOK_TOKEN`.
- KYPO: `KYPO_URL`, `KYPO_LTI_LAUNCH_URL`, `KYPO_SUBNET`, `KYPO_TARGET_HOST`.
- Escaneo/seguridad: `OPENVAS_TARGET_HOST`.
- TLS MISP: `MISP_CA_BUNDLE`.

### Training platform: code strategy (actual path vs synchronization)

The `training_platform` role supports two explicit modes for code availability:

- `training_platform_source_mode: assert_present` (role default): Requires the code to already exist in `training_platform_app_dir` on the remote host.
- `training_platform_source_mode: sync_from_repo`: synchronises `subcase_1b/training_platform` from the controller (`training_platform_source_dir`) to `training_platform_app_dir` before creating venv/systemd/nginx.

Canonical CRCZ subcase_1b deployment for this repository should use `sync_from_repo` (see `provisioning/group_vars/subcase_1b.example.yml`), because the repository is checked out on the controller and is not pre-mounted at `/opt/subcase_1b/training_platform` inside the VM.

`training_platform_source_dir` has a portable default based on `role_path`:
`{{ role_path }}/../../../subcase_1b/training_platform`.
This keeps the lookup repo-relative even if provisioning is launched through compatibility wrappers (for example `sandboxes/provisioning_subcase_1b/site.yml`).

Use `assert_present` only when another process (golden image, external bootstrap, pre-sync job) has already installed the training platform code on the remote host.

## CYNET components in docker mode

The `bips`, `ng_siem`, `cicms` and `ng_soar` roles support `deb` and `docker` via `*_install_method`.

> Important: `common_bootstrap` is already running before these roles and with `common_bootstrap_install_docker: true`, so the Docker installation (engine, compose plugin and prerequisites) **should not be duplicated** within each role.

For Docker in Subcase 1b, use as a base:

- `provisioning/group_vars/all.example.yml`
- `provisioning/group_vars/subcase_1b.example.yml`

And then copy them to their real equivalents (`all.yml`, `subcase_1b.yml`) before running.

## Comandos Ansible exactos (incluyendo `--limit` por grupo)

### Complete execution

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

### Execution by group

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit training_platform
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit trainee_workstation
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit cyber_range
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit randomization_platform
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit bips
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit ng_siem
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit cicms
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit ng_soar
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit router
```

### Useful examples of compound limits

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit subcase_1b
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit 'bips:ng_siem:cicms:ng_soar'
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit 'training_platform,trainee_workstation'
```


## Validation/CI commands (local equivalents)

El workflow de CI ejecuta estos checks sobre este repositorio:

```bash
yamllint .
ansible-lint provisioning/
ansible-playbook --syntax-check -i provisioning/inventory.ini provisioning/playbook.yml
PYTHONPATH=. pytest tests/ soc_alerts/tests/
```

## Compatibilidad

The compatibility wrappers that import the canonical stream are:

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Ambos delegan en `provisioning/playbook.yml` para evitar desalineaciones entre playbooks/roles heredados.
Do not duplicate provisioning tasks in sandbox or legacy playbooks.

Additionally, `subcase_1b/ansible/roles/**` is considered **legacy/non-canonical** and its final policy is **retain snapshot read-only**:

- It must not be edited for functional changes.
- Any functional change must be made in `provisioning/roles/**`.
- It is preserved as historical evidence/compatibility, but should not receive new features or functional corrections.
- Any functional evolution must be implemented in `provisioning/roles/**` and, if necessary, reflected only as a documentary note in the legacy snapshot.

## Known limitations / TODOs reales

- `router` remains an intentional and definitive non-op host in this scope: there are no network/firewall/NAT/routing configuration tasks in the canonical flow.
- `soc_server` remains as isolated legacy alias for historical documentation; any references should be migrated to canonical groups.
- `subcase_1b/ansible/roles/**` is kept as a read-only legacy snapshot; It is not part of the path of functional evolution.
- Part of the deployment depends on external platforms (Open edX, IRIS, MISP, KYPO), so the playbook cannot validate those integrations without real credentials.

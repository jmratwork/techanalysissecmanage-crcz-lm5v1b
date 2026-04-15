# Provisioning Playbook

`provisioning/playbook.yml` es el **entrypoint canónico** del aprovisionamiento de Subcaso 1b.
El inventario canónico es `provisioning/inventory.ini`.

## Playbook e inventario definitivos

Ejecuta siempre desde la raíz del repositorio:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

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
- `subcase_1b` (grupo padre vía `:children`)

> Nota: el grupo `soc_server` está **deprecado** y no debe usarse.

## Qué se despliega localmente vs integraciones externas

### Despliegue local (dentro de la topología/lab)

El playbook `provisioning/playbook.yml` aplica roles locales sobre estos grupos:

- `all` → `logging`
- `training_platform` → `training_platform`
- `trainee_workstation` → `trainee_workstation`
- `cyber_range` → `cyber_range_setup`
- `bips` → `common_bootstrap` + `bips`
- `cicms` → `common_bootstrap` + `cicms`
- `ng_siem` → `common_bootstrap` + `ng_siem`
- `ng_soar` → `common_bootstrap` + `ng_soar`

### Integraciones externas (no se aprovisionan como servicios aquí)

Estas plataformas se consumen vía variables/configuración, pero **no** se levantan como parte de este playbook:

- **Open edX**: integración del `training_platform` para autenticación/gradebook/LTI.
- **MISP**: integración para CTI/eventos desde scripts y servicios.
- **IRIS**: integración para gestión de casos vía scripts (`rules_to_iris_bridge.py`, `iris_case_closed_poll.py`).

## Variables requeridas y opcionales

La referencia central de variables de entorno está en:

- [`docs/env_variables.md`](../docs/env_variables.md)

Resumen operativo para provisioning:

### Requeridas (si habilitas integración externa)

- Open edX: `OPENEDX_URL` y credenciales (`OPENEDX_API_TOKEN` o `OPENEDX_SESSION_COOKIE`).
- MISP: `MISP_URL` y `MISP_API_KEY`.
- IRIS: `IRIS_URL` (y normalmente `IRIS_API_KEY` en entornos protegidos).
- LTI/KYPO (training platform): `LTI_TOOL_PRIVATE_KEY`, `LTI_CLIENT_ID`, `LTI_DEPLOYMENT_ID`.

### Opcionales

- Open edX gradebook: `OPENEDX_GRADEBOOK_ENDPOINT`, `OPENEDX_GRADEBOOK_TOKEN`.
- KYPO: `KYPO_URL`, `KYPO_LTI_LAUNCH_URL`, `KYPO_SUBNET`, `KYPO_TARGET_HOST`.
- Escaneo/seguridad: `OPENVAS_TARGET_HOST`.
- TLS MISP: `MISP_CA_BUNDLE`.

## Comandos Ansible exactos (incluyendo `--limit` por grupo)

### Ejecución completa

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

### Ejecución por grupo

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

### Ejemplos útiles de límites compuestos

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit subcase_1b
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit 'bips:ng_siem:cicms:ng_soar'
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit 'training_platform,trainee_workstation'
```

## Compatibilidad

Existe un wrapper de compatibilidad en `sandboxes/provisioning_subcase_1b/site.yml` que importa el playbook canónico.
No dupliques tareas de aprovisionamiento en playbooks de sandbox.

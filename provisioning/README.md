# Provisioning Playbook

`provisioning/playbook.yml` es el **entrypoint canónico** del aprovisionamiento de Subcaso 1b.
El inventario canónico es `provisioning/inventory.ini`.

## Regla de precedencia (canónico vs wrappers)

Orden de precedencia para Subcaso 1b:

1. `provisioning/playbook.yml` + `provisioning/inventory.ini` (**canónico**).
2. `sandboxes/provisioning_subcase_1b/site.yml` (**wrapper** por compatibilidad).
3. `subcase_1b/ansible/playbook.yml` (**wrapper** por compatibilidad legacy).

Los wrappers no deben contener lógica funcional alternativa ni divergente.

## Flujo recomendado (docker mode)

Ejecuta siempre desde la raíz del repositorio y sigue este orden:

1. **Copiar archivos de ejemplo a archivos reales**:
   ```bash
   cp provisioning/group_vars/all.example.yml provisioning/group_vars/all.yml
   cp provisioning/group_vars/subcase_1b.example.yml provisioning/group_vars/subcase_1b.yml
   ```
2. **Rellenar variables obligatorias** en `all.yml` y `subcase_1b.yml` (imágenes, tags, credenciales y demás placeholders `__REQUIRED_*__`).
3. **Ejecutar el playbook**:
   ```bash
   ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
   ```

> Importante: antes de ejecutar en docker mode, deben existir los archivos reales `provisioning/group_vars/all.yml` y `provisioning/group_vars/subcase_1b.yml`.

### Coherencia explícita: topología ↔ inventario ↔ playbook

Referencia de topología para Subcaso 1b: `sandboxes/topology_subcase_1b.yaml`.

| Host canónico | IP en topología (`sandboxes/topology_subcase_1b.yaml`) | Grupo en `provisioning/inventory.ini` | Rol aplicado en `provisioning/playbook.yml` |
|---|---|---|---|
| `training_platform` | `10.10.0.2` | `training_platform` | `training_platform` |
| `trainee_workstation` | `10.10.0.3` | `trainee_workstation` | `trainee_workstation` |
| `cyber_range` | `10.10.0.4` | `cyber_range` | `cyber_range_setup` |
| `randomization_platform` | `10.10.0.5` | `randomization_platform` | `randomization_platform` |
| `bips` | `10.10.0.6` | `bips` | `common_bootstrap` + `bips` |
| `ng_siem` | `10.10.0.7` | `ng_siem` | `common_bootstrap` + `ng_siem` |
| `cicms` | `10.10.0.8` | `cicms` | `common_bootstrap` + `cicms` |
| `ng_soar` | `10.10.0.9` | `ng_soar` | `common_bootstrap` + `ng_soar` |
| `router` | `10.10.0.1` | `router` | `router_noop` (no-op explícito) |

Notas de coherencia:
- `inventory.ini` usa `ansible_host=<hostname>` (resolución por nombre), por lo que los valores IP de la topología no se duplican en el inventario canónico.
- `soc_server` no existe en la topología ni en el inventario canónico de Subcaso 1b.

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
> Se mantiene únicamente como referencia legacy aislada fuera del flujo canónico.

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
- `randomization_platform` → `randomization_platform` (provisión mínima real: runtime bash, directorio de logs, script artefacto y servicio systemd)
- `router` → `router_noop` (no-op explícito con `assert` + `debug`: “sin provisión activa en este repositorio”)

### Estado exacto por host (activo vs no-op)

- **Hosts con rol activo**: `training_platform`, `trainee_workstation`, `cyber_range`, `randomization_platform`, `bips`, `ng_siem`, `cicms`, `ng_soar`.
- **Host documentado como no-op**: `router` (rol `router_noop`).
- **Host/grupo legacy aislado**: `soc_server` (no inventariado en `provisioning/inventory.ini`, no ejecutar `--limit soc_server`).

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

## CYNET components in docker mode

Los roles `bips`, `ng_siem`, `cicms` y `ng_soar` soportan `deb` y `docker` vía `*_install_method`.

> Importante: `common_bootstrap` ya se ejecuta antes de estos roles y con `common_bootstrap_install_docker: true`, por lo que la instalación de Docker (engine, compose plugin y prerequisitos) **no debe duplicarse** dentro de cada rol.

Para Docker en Subcaso 1b, usa como base:

- `provisioning/group_vars/all.example.yml`
- `provisioning/group_vars/subcase_1b.example.yml`

Y luego cópialos a sus equivalentes reales (`all.yml`, `subcase_1b.yml`) antes de ejecutar.

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


## Comandos de validación/CI (equivalentes locales)

El workflow de CI ejecuta estos checks sobre este repositorio:

```bash
yamllint .
ansible-lint provisioning/
ansible-playbook --syntax-check -i provisioning/inventory.ini provisioning/playbook.yml
PYTHONPATH=. pytest tests/ soc_alerts/tests/
```

## Compatibilidad

Los wrappers de compatibilidad que importan el flujo canónico son:

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Ambos delegan en `provisioning/playbook.yml` para evitar desalineaciones entre playbooks/roles heredados.
No dupliques tareas de aprovisionamiento en playbooks de sandbox o legacy.

Además, `subcase_1b/ansible/roles/**` se considera **legado/no canónico**:

- No debe editarse para cambios funcionales.
- Cualquier cambio funcional debe hacerse en `provisioning/roles/**`.
- Opcional recomendado: migrar/reducir el contenido legacy a wrappers o eliminarlo si no participa en el runtime de KYPO, conservando únicamente `subcase_1b/ansible/playbook.yml` como wrapper.

## Known limitations / TODOs reales

- `router` permanece como host no-op intencional: no hay tareas de configuración de red/firewall en el flujo canónico.
- `soc_server` sigue como alias legacy aislado para documentación histórica; cualquier referencia debe migrarse a grupos canónicos.
- Aún existe código/roles legacy en `subcase_1b/ansible/roles/**` por compatibilidad; falta completar su reducción a wrappers mínimos.
- Parte del despliegue depende de plataformas externas (Open edX, IRIS, MISP, KYPO), por lo que el playbook no puede validar esas integraciones sin credenciales reales.

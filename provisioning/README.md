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

## CYNET components in docker mode

Los roles `bips`, `ng_siem`, `cicms` y `ng_soar` soportan `deb` y `docker` vía `*_install_method`.

> Importante: `common_bootstrap` ya se ejecuta antes de estos roles y con `common_bootstrap_install_docker: true`, por lo que la instalación de Docker (engine, compose plugin y prerequisitos) **no debe duplicarse** dentro de cada rol.

### Variables nuevas por rol (docker)

Cada rol mantiene el mismo patrón de variables, cambiando el prefijo:

- `bips_*`
- `ng_siem_*`
- `cicms_*`
- `ng_soar_*`

Variables clave por componente:

- Método: `*_install_method` (`deb`/`docker`) y `*_docker_enabled`.
- Imagen: `*_docker_image`, `*_docker_tag`, `*_docker_container_name`.
- Puertos: `*_docker_ports`.
- Volúmenes: `*_docker_volumes`.
- Redes: `*_docker_networks`.
- TLS: `*_docker_tls_enabled`, `*_docker_tls_cert_src`, `*_docker_tls_key_src`, `*_docker_tls_cert_dest`, `*_docker_tls_key_dest`.
- Verificación TLS en healthcheck: `*_docker_healthcheck_validate_certs`.

Defaults reales por rol (fuente: `provisioning/roles/*/defaults/main.yml`):

| Rol | `*_install_method` por defecto | `*_docker_enabled` por defecto | Imagen por defecto | Tag por defecto | Puertos por defecto | Redes por defecto | TLS verify healthcheck |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `bips` | `{{ 'docker' if bips_docker_enabled else 'deb' }}` | `false` | `__REQUIRED_DOCKER_IMAGE__` | `__REQUIRED_DOCKER_TAG__` | `8600:8080` | `bips_net` | `false` |
| `ng_siem` | `{{ 'docker' if ng_siem_docker_enabled else 'deb' }}` | `false` | `__REQUIRED_DOCKER_IMAGE__` | `__REQUIRED_DOCKER_TAG__` | `8700:5601` | `ng_siem_net` | `false` |
| `cicms` | `{{ 'docker' if cicms_docker_enabled else 'deb' }}` | `false` | `__REQUIRED_DOCKER_IMAGE__` | `__REQUIRED_DOCKER_TAG__` | `8800:8080` | `cicms_net` | `false` |
| `ng_soar` | `{{ 'docker' if ng_soar_docker_enabled else 'deb' }}` | `false` | `__REQUIRED_DOCKER_IMAGE__` | `__REQUIRED_DOCKER_TAG__` | `8900:8443` | `ng_soar_net` | `false` |

Comportamiento real de `*_install_method`:

- Es una variable derivada: si `*_docker_enabled` es `true`, el método efectivo pasa a `docker`.
- Si `*_docker_enabled` se mantiene en `false` (default), el método efectivo permanece en `deb`.
- Para evitar ambigüedades en inventario, en subcase 1b se recomienda fijar ambos (`*_install_method: docker` y `*_docker_enabled: true`).

## Mínimo requerido para Docker en subcase 1b

Para cada rol CYNET (`bips`, `ng_siem`, `cicms`, `ng_soar`), define **exactamente** estas variables obligatorias en `group_vars` del entorno (por ejemplo `inventory/group_vars/all.yml`):

- `<rol>_install_method: docker`
- `<rol>_docker_enabled: true`
- `<rol>_docker_image: <imagen_real>`
- `<rol>_docker_tag: <tag_real>`

Ejemplo mínimo completo:

```yaml
bips_install_method: docker
bips_docker_enabled: true
bips_docker_image: __REQUIRED_DOCKER_IMAGE__
bips_docker_tag: "__REQUIRED_DOCKER_TAG__"

ng_siem_install_method: docker
ng_siem_docker_enabled: true
ng_siem_docker_image: __REQUIRED_DOCKER_IMAGE__
ng_siem_docker_tag: "__REQUIRED_DOCKER_TAG__"

cicms_install_method: docker
cicms_docker_enabled: true
cicms_docker_image: __REQUIRED_DOCKER_IMAGE__
cicms_docker_tag: "__REQUIRED_DOCKER_TAG__"

ng_soar_install_method: docker
ng_soar_docker_enabled: true
ng_soar_docker_image: __REQUIRED_DOCKER_IMAGE__
ng_soar_docker_tag: "__REQUIRED_DOCKER_TAG__"
```

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

### Ejemplos de ejecución en modo docker para CYNET

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml \
  --limit 'bips:ng_siem:cicms:ng_soar' \
  -e bips_install_method=docker -e bips_docker_enabled=true \
  -e ng_siem_install_method=docker -e ng_siem_docker_enabled=true \
  -e cicms_install_method=docker -e cicms_docker_enabled=true \
  -e ng_soar_install_method=docker -e ng_soar_docker_enabled=true
```

Ejemplo con overrides de imagen/puertos/red/TLS verify para un rol:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml \
  --limit 'ng_siem' \
  -e ng_siem_install_method=docker \
  -e ng_siem_docker_enabled=true \
  -e ng_siem_docker_image=__REQUIRED_DOCKER_IMAGE__ \
  -e ng_siem_docker_tag=__REQUIRED_DOCKER_TAG__ \
  -e 'ng_siem_docker_ports=["15601:5601"]' \
  -e 'ng_siem_docker_networks=["soc_backbone"]' \
  -e ng_siem_docker_healthcheck_validate_certs=true
```

## Compatibilidad

Los wrappers de compatibilidad que importan el flujo canónico son:

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Ambos delegan en `provisioning/playbook.yml` para evitar desalineaciones entre playbooks/roles heredados.
No dupliques tareas de aprovisionamiento en playbooks de sandbox o legacy.

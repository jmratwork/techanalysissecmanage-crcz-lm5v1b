# NG-SOAR role

## Variables principales
- `ng_soar_enabled`: activa/desactiva el rol.
- `ng_soar_install_method`: effective installation method (`deb` or `docker`).
- `ng_soar_repo_url`, `ng_soar_package_path`, `ng_soar_package_checksum`: origen e integridad del paquete para modo `deb`.
- `ng_soar_service_name`, `ng_soar_config_path`, `ng_soar_dashboard_path`: service and configuration paths.
- `ng_soar_check_connectivity`, `ng_soar_min_free_kb`: validaciones previas opcionales.
- `ng_soar_docker_enabled`, `ng_soar_docker_image`, `ng_soar_docker_tag`: Docker deployment control and artefact.
- `ng_soar_docker_wait_for`, `ng_soar_docker_healthcheck_enabled`, `ng_soar_docker_healthcheck_url`: post-deploy runtime validation (port and/or HTTP endpoint).

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `ng_soar_install_method` | `{{ 'docker' if ng_soar_docker_enabled else 'deb' }}` | It is calculated dynamically with `ng_soar_docker_enabled`. |
| `ng_soar_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `ng_soar_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `ng_soar_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `ng_soar_docker_ports` | `["8900:8443"]` | Puerto host:contenedor por defecto. |

## Minimum required for Docker in subcase 1b

To run this role with Docker in Subcase 1b, you must define **exactly** these variables:

- `ng_soar_install_method: docker`
- `ng_soar_docker_enabled: true`
- `ng_soar_docker_image: <imagen_real>`
- `ng_soar_docker_tag: <tag_real>`

Ejemplo (en `inventory/group_vars/all.yml` del entorno o equivalente):

```yaml
ng_soar_install_method: docker
ng_soar_docker_enabled: true
ng_soar_docker_image: __REQUIRED_DOCKER_IMAGE__
ng_soar_docker_tag: "__REQUIRED_DOCKER_TAG__"
```

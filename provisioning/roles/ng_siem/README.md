# NG-SIEM role

## Variables principales
- `ng_siem_enabled`: activa/desactiva el rol.
- `ng_siem_install_method`: effective installation method (`deb` or `docker`).
- `ng_siem_repo_url`, `ng_siem_package_path`, `ng_siem_package_checksum`: origen e integridad del paquete para modo `deb`.
- `ng_siem_service_name`, `ng_siem_config_path`, `ng_siem_filebeat_config_path`: service and configuration paths.
- `ng_siem_check_connectivity`, `ng_siem_min_free_kb`: validaciones previas opcionales.
- `ng_siem_docker_enabled`, `ng_siem_docker_image`, `ng_siem_docker_tag`: Docker deployment control and artefact.
- `ng_siem_docker_wait_for`, `ng_siem_docker_healthcheck_enabled`, `ng_siem_docker_healthcheck_url`: post-deploy runtime validation (port and/or HTTP endpoint).

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `ng_siem_install_method` | `{{ 'docker' if ng_siem_docker_enabled else 'deb' }}` | It is calculated dynamically with `ng_siem_docker_enabled`. |
| `ng_siem_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `ng_siem_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `ng_siem_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `ng_siem_docker_ports` | `["8700:5601"]` | Puerto host:contenedor por defecto. |

## Minimum required for Docker in subcase 1b

To run this role with Docker in Subcase 1b, you must define **exactly** these variables:

- `ng_siem_install_method: docker`
- `ng_siem_docker_enabled: true`
- `ng_siem_docker_image: <imagen_real>`
- `ng_siem_docker_tag: <tag_real>`

Ejemplo (en `inventory/group_vars/all.yml` del entorno o equivalente):

```yaml
ng_siem_install_method: docker
ng_siem_docker_enabled: true
ng_siem_docker_image: __REQUIRED_DOCKER_IMAGE__
ng_siem_docker_tag: "__REQUIRED_DOCKER_TAG__"
```

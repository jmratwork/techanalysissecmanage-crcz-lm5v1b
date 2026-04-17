# CICMS role

## Variables principales
- `cicms_enabled`: activa/desactiva el rol.
- `cicms_install_method`: effective installation method (`deb` or `docker`).
- `cicms_repo_url`, `cicms_package_path`, `cicms_package_checksum`: origen e integridad del paquete para modo `deb`.
- `cicms_service_name`, `cicms_config_path`: service and configuration path.
- `cicms_check_connectivity`, `cicms_min_free_kb`: validaciones previas opcionales.
- `cicms_docker_enabled`, `cicms_docker_image`, `cicms_docker_tag`: Docker deployment control and artefact.
- `cicms_docker_wait_for`, `cicms_docker_healthcheck_enabled`, `cicms_docker_healthcheck_url`: post-deploy runtime validation (port and/or HTTP endpoint).

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `cicms_install_method` | `{{ 'docker' if cicms_docker_enabled else 'deb' }}` | It is calculated dynamically with `cicms_docker_enabled`. |
| `cicms_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `cicms_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `cicms_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `cicms_docker_ports` | `["8800:8080"]` | Puerto host:contenedor por defecto. |

## Minimum required for Docker in subcase 1b

To run this role with Docker in Subcase 1b, you must define **exactly** these variables:

- `cicms_install_method: docker`
- `cicms_docker_enabled: true`
- `cicms_docker_image: <imagen_real>`
- `cicms_docker_tag: <tag_real>`

Ejemplo (en `inventory/group_vars/all.yml` del entorno o equivalente):

```yaml
cicms_install_method: docker
cicms_docker_enabled: true
cicms_docker_image: __REQUIRED_DOCKER_IMAGE__
cicms_docker_tag: "__REQUIRED_DOCKER_TAG__"
```

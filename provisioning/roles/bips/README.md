# BIPS role

## Variables principales
- `bips_enabled`: activa/desactiva el rol.
- `bips_install_method`: effective installation method (`deb` or `docker`).
- `bips_repo_url`, `bips_package_path`, `bips_package_checksum`: origen e integridad del paquete para modo `deb`.
- `bips_service_name`, `bips_config_path`: service and configuration path.
- `bips_check_connectivity`, `bips_min_free_kb`: validaciones previas opcionales.
- `bips_docker_enabled`, `bips_docker_image`, `bips_docker_tag`: Docker deployment control and artefact.
- `bips_docker_wait_for`, `bips_docker_healthcheck_enabled`, `bips_docker_healthcheck_url`: post-deploy runtime validation (port and/or HTTP endpoint).

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

> Compatibility note: the `install_method: deb` flow uses `apt` over `.deb` packages, so it requires Debian-family hosts.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `beeps_install_method` | `{{ 'docker' if beeps_docker_enabled else 'deb' }}` | It is calculated dynamically with `bips_docker_enabled`. |
| `bips_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `bips_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `bips_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Mandatory placeholder; must be replaced in environment `group_vars`. |
| `bips_docker_ports` | `["8600:8080"]` | Puerto host:contenedor por defecto. |

## Minimum required for Docker in subcase 1b

To run this role with Docker in Subcase 1b, you must define **exactly** these variables:

- `bips_install_method: docker`
- `bips_docker_enabled: true`
- `bips_docker_image: <imagen_real>`
- `bips_docker_tag: <tag_real>`

Ejemplo (en `inventory/group_vars/all.yml` del entorno o equivalente):

```yaml
bips_install_method: docker
bips_docker_enabled: true
bips_docker_image: __REQUIRED_DOCKER_IMAGE__
bips_docker_tag: "__REQUIRED_DOCKER_TAG__"
```

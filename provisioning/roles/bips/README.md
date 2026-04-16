# BIPS role

## Variables principales
- `bips_enabled`: activa/desactiva el rol.
- `bips_install_method`: método efectivo de instalación (`deb` o `docker`).
- `bips_repo_url`, `bips_package_path`, `bips_package_checksum`: origen e integridad del paquete para modo `deb`.
- `bips_service_name`, `bips_config_path`: servicio y ruta de configuración.
- `bips_check_connectivity`, `bips_min_free_kb`: validaciones previas opcionales.
- `bips_docker_enabled`, `bips_docker_image`, `bips_docker_tag`: control y artefacto de despliegue en Docker.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `bips_install_method` | `{{ 'docker' if bips_docker_enabled else 'deb' }}` | Se calcula dinámicamente con `bips_docker_enabled`. |
| `bips_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `bips_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `bips_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `bips_docker_ports` | `["8600:8080"]` | Puerto host:contenedor por defecto. |

## Mínimo requerido para Docker en subcase 1b

Para ejecutar este rol en Docker en Subcaso 1b debes definir **exactamente** estas variables:

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

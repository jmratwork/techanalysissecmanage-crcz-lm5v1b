# CICMS role

## Variables principales
- `cicms_enabled`: activa/desactiva el rol.
- `cicms_install_method`: método efectivo de instalación (`deb` o `docker`).
- `cicms_repo_url`, `cicms_package_path`, `cicms_package_checksum`: origen e integridad del paquete para modo `deb`.
- `cicms_service_name`, `cicms_config_path`: servicio y ruta de configuración.
- `cicms_check_connectivity`, `cicms_min_free_kb`: validaciones previas opcionales.
- `cicms_docker_enabled`, `cicms_docker_image`, `cicms_docker_tag`: control y artefacto de despliegue en Docker.
- `cicms_docker_wait_for`, `cicms_docker_healthcheck_enabled`, `cicms_docker_healthcheck_url`: validación runtime post-deploy (puerto y/o endpoint HTTP).

> Nota de compatibilidad: el flujo `install_method: deb` usa `apt` sobre paquetes `.deb`, por lo que requiere hosts Debian-family.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `cicms_install_method` | `{{ 'docker' if cicms_docker_enabled else 'deb' }}` | Se calcula dinámicamente con `cicms_docker_enabled`. |
| `cicms_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `cicms_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `cicms_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `cicms_docker_ports` | `["8800:8080"]` | Puerto host:contenedor por defecto. |

## Mínimo requerido para Docker en subcase 1b

Para ejecutar este rol en Docker en Subcaso 1b debes definir **exactamente** estas variables:

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

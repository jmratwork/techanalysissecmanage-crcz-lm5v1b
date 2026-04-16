# NG-SOAR role

## Variables principales
- `ng_soar_enabled`: activa/desactiva el rol.
- `ng_soar_install_method`: método efectivo de instalación (`deb` o `docker`).
- `ng_soar_repo_url`, `ng_soar_package_path`, `ng_soar_package_checksum`: origen e integridad del paquete para modo `deb`.
- `ng_soar_service_name`, `ng_soar_config_path`, `ng_soar_dashboard_path`: servicio y rutas de configuración.
- `ng_soar_check_connectivity`, `ng_soar_min_free_kb`: validaciones previas opcionales.
- `ng_soar_docker_enabled`, `ng_soar_docker_image`, `ng_soar_docker_tag`: control y artefacto de despliegue en Docker.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `ng_soar_install_method` | `{{ 'docker' if ng_soar_docker_enabled else 'deb' }}` | Se calcula dinámicamente con `ng_soar_docker_enabled`. |
| `ng_soar_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `ng_soar_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `ng_soar_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `ng_soar_docker_ports` | `["8900:8443"]` | Puerto host:contenedor por defecto. |

## Mínimo requerido para Docker en subcase 1b

Para ejecutar este rol en Docker en Subcaso 1b debes definir **exactamente** estas variables:

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

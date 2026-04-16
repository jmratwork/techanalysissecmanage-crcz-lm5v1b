# NG-SIEM role

## Variables principales
- `ng_siem_enabled`: activa/desactiva el rol.
- `ng_siem_install_method`: método efectivo de instalación (`deb` o `docker`).
- `ng_siem_repo_url`, `ng_siem_package_path`, `ng_siem_package_checksum`: origen e integridad del paquete para modo `deb`.
- `ng_siem_service_name`, `ng_siem_config_path`, `ng_siem_filebeat_config_path`: servicio y rutas de configuración.
- `ng_siem_check_connectivity`, `ng_siem_min_free_kb`: validaciones previas opcionales.
- `ng_siem_docker_enabled`, `ng_siem_docker_image`, `ng_siem_docker_tag`: control y artefacto de despliegue en Docker.

## Defaults reales (fuente: `defaults/main.yml`)

| Variable | Default actual | Notas |
| --- | --- | --- |
| `ng_siem_install_method` | `{{ 'docker' if ng_siem_docker_enabled else 'deb' }}` | Se calcula dinámicamente con `ng_siem_docker_enabled`. |
| `ng_siem_docker_enabled` | `false` | Si no se sobreescribe, el flujo resultante es `deb`. |
| `ng_siem_docker_image` | `__REQUIRED_DOCKER_IMAGE__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `ng_siem_docker_tag` | `__REQUIRED_DOCKER_TAG__` | Placeholder obligatorio; debe reemplazarse en `group_vars` del entorno. |
| `ng_siem_docker_ports` | `["8700:5601"]` | Puerto host:contenedor por defecto. |

## Mínimo requerido para Docker en subcase 1b

Para ejecutar este rol en Docker en Subcaso 1b debes definir **exactamente** estas variables:

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

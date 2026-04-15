# NG-SOAR role

## Variables principales
- `ng_soar_enabled`: activa/desactiva el rol.
- `ng_soar_install_method`: método de instalación (`deb`).
- `ng_soar_repo_url`, `ng_soar_package_path`, `ng_soar_package_checksum`: origen e integridad del paquete.
- `ng_soar_service_name`, `ng_soar_config_path`, `ng_soar_dashboard_path`: servicio y rutas de configuración.
- `ng_soar_check_connectivity`, `ng_soar_min_free_kb`: validaciones previas opcionales.
- `ng_soar_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

## Imágenes Docker obligatorias
Cuando `ng_soar_install_method: docker` (o `ng_soar_docker_enabled: true`) debes inyectar valores reales para:
- `ng_soar_docker_image`
- `ng_soar_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
ng_soar_docker_enabled: true
ng_soar_docker_image: registry.interna.example/ng-soar
ng_soar_docker_tag: "2026.04.0"
```

Si mantienes placeholders (`__REQUIRED_DOCKER_IMAGE__` o `__REQUIRED_DOCKER_TAG__`), el rol fallará en `tasks/main.yml` con un mensaje explícito.

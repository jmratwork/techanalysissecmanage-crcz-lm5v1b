# NG-SOAR role

## Variables principales
- `ng_soar_enabled`: activa/desactiva el rol.
- `ng_soar_install_method`: installation method (`deb`).
- `ng_soar_repo_url`, `ng_soar_package_path`, `ng_soar_package_checksum`: origen e integridad del paquete.
- `ng_soar_service_name`, `ng_soar_config_path`, `ng_soar_dashboard_path`: service and configuration paths.
- `ng_soar_check_connectivity`, `ng_soar_min_free_kb`: validaciones previas opcionales.
- `ng_soar_has_docker_artifacts`: if real Docker artifact exists, do not use `.deb` installation.

## Required Docker images
Cuando `ng_soar_install_method: docker` (o `ng_soar_docker_enabled: true`) debes inyectar valores reales para:
- `ng_soar_docker_image`
- `ng_soar_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
ng_soar_docker_enabled: true
ng_soar_docker_image: registry.interna.example/ng-soar
ng_soar_docker_tag: "2026.04.0"
```

If you maintain placeholders (`__REQUIRED_DOCKER_IMAGE__` or `__REQUIRED_DOCKER_TAG__`), the role will fail in `tasks/main.yml` with an explicit message.

# NG-SIEM role

## Variables principales
- `ng_siem_enabled`: activa/desactiva el rol.
- `ng_siem_install_method`: installation method (`deb`).
- `ng_siem_repo_url`, `ng_siem_package_path`, `ng_siem_package_checksum`: origen e integridad del paquete.
- `ng_siem_service_name`, `ng_siem_config_path`, `ng_siem_filebeat_config_path`: service and configuration paths.
- `ng_siem_check_connectivity`, `ng_siem_min_free_kb`: validaciones previas opcionales.
- `ng_siem_has_docker_artifacts`: if real Docker artifact exists, do not use `.deb` installation.

## Required Docker images
Cuando `ng_siem_install_method: docker` (o `ng_siem_docker_enabled: true`) debes inyectar valores reales para:
- `ng_siem_docker_image`
- `ng_siem_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
ng_siem_docker_enabled: true
ng_siem_docker_image: registry.interna.example/ng-siem
ng_siem_docker_tag: "2026.04.0"
```

If you maintain placeholders (`__REQUIRED_DOCKER_IMAGE__` or `__REQUIRED_DOCKER_TAG__`), the role will fail in `tasks/main.yml` with an explicit message.

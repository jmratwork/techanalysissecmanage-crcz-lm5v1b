# CICMS role

## Variables principales
- `cicms_enabled`: activa/desactiva el rol.
- `cicms_install_method`: installation method (`deb`).
- `cicms_repo_url`, `cicms_package_path`, `cicms_package_checksum`: origen e integridad del paquete.
- `cicms_service_name`, `cicms_config_path`: service and configuration path.
- `cicms_check_connectivity`, `cicms_min_free_kb`: validaciones previas opcionales.
- `cicms_has_docker_artifacts`: if real Docker artifact exists, do not use `.deb` installation.

## Required Docker images
Cuando `cicms_install_method: docker` (o `cicms_docker_enabled: true`) debes inyectar valores reales para:
- `cicms_docker_image`
- `cicms_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
cicms_docker_enabled: true
cicms_docker_image: registry.interna.example/cicms
cicms_docker_tag: "2026.04.0"
```

If you maintain placeholders (`__REQUIRED_DOCKER_IMAGE__` or `__REQUIRED_DOCKER_TAG__`), the role will fail in `tasks/main.yml` with an explicit message.

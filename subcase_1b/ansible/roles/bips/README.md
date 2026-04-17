# BIPS role

## Variables principales
- `bips_enabled`: activa/desactiva el rol.
- `bips_install_method`: installation method (`deb`).
- `bips_repo_url`, `bips_package_path`, `bips_package_checksum`: origen e integridad del paquete.
- `bips_service_name`, `bips_config_path`: service and configuration path.
- `bips_check_connectivity`, `bips_min_free_kb`: validaciones previas opcionales.
- `bips_has_docker_artifacts`: if real Docker artifact exists, do not use `.deb` installation.

## Required Docker images
Cuando `bips_install_method: docker` (o `bips_docker_enabled: true`) debes inyectar valores reales para:
- `bips_docker_image`
- `bips_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
bips_docker_enabled: true
bips_docker_image: registry.interna.example/bips
bips_docker_tag: "2026.04.0"
```

If you maintain placeholders (`__REQUIRED_DOCKER_IMAGE__` or `__REQUIRED_DOCKER_TAG__`), the role will fail in `tasks/main.yml` with an explicit message.

# BIPS role

## Variables principales
- `bips_enabled`: activa/desactiva el rol.
- `bips_install_method`: método de instalación (`deb`).
- `bips_repo_url`, `bips_package_path`, `bips_package_checksum`: origen e integridad del paquete.
- `bips_service_name`, `bips_config_path`: servicio y ruta de configuración.
- `bips_check_connectivity`, `bips_min_free_kb`: validaciones previas opcionales.
- `bips_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

## Imágenes Docker obligatorias
Cuando `bips_install_method: docker` (o `bips_docker_enabled: true`) debes inyectar valores reales para:
- `bips_docker_image`
- `bips_docker_tag`

Ejemplo en `inventory/group_vars/all.yml`:

```yaml
bips_docker_enabled: true
bips_docker_image: registry.interna.example/bips
bips_docker_tag: "2026.04.0"
```

Si mantienes placeholders (`__REQUIRED_DOCKER_IMAGE__` o `__REQUIRED_DOCKER_TAG__`), el rol fallará en `tasks/main.yml` con un mensaje explícito.

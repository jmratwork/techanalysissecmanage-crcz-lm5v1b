# BIPS role

## Variables principales
- `bips_enabled`: activa/desactiva el rol.
- `bips_install_method`: método de instalación (`deb`).
- `bips_repo_url`, `bips_package_path`, `bips_package_checksum`: origen e integridad del paquete.
- `bips_service_name`, `bips_config_path`: servicio y ruta de configuración.
- `bips_check_connectivity`, `bips_min_free_kb`: validaciones previas opcionales.
- `bips_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

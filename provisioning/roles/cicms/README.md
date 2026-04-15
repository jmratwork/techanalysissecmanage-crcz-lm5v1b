# CICMS role

## Variables principales
- `cicms_enabled`: activa/desactiva el rol.
- `cicms_install_method`: método de instalación (`deb`).
- `cicms_repo_url`, `cicms_package_path`, `cicms_package_checksum`: origen e integridad del paquete.
- `cicms_service_name`, `cicms_config_path`: servicio y ruta de configuración.
- `cicms_check_connectivity`, `cicms_min_free_kb`: validaciones previas opcionales.
- `cicms_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

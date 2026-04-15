# NG-SOAR role

## Variables principales
- `ng_soar_enabled`: activa/desactiva el rol.
- `ng_soar_install_method`: método de instalación (`deb`).
- `ng_soar_repo_url`, `ng_soar_package_path`, `ng_soar_package_checksum`: origen e integridad del paquete.
- `ng_soar_service_name`, `ng_soar_config_path`, `ng_soar_dashboard_path`: servicio y rutas de configuración.
- `ng_soar_check_connectivity`, `ng_soar_min_free_kb`: validaciones previas opcionales.
- `ng_soar_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

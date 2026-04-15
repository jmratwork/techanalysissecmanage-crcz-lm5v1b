# NG-SIEM role

## Variables principales
- `ng_siem_enabled`: activa/desactiva el rol.
- `ng_siem_install_method`: método de instalación (`deb`).
- `ng_siem_repo_url`, `ng_siem_package_path`, `ng_siem_package_checksum`: origen e integridad del paquete.
- `ng_siem_service_name`, `ng_siem_config_path`, `ng_siem_filebeat_config_path`: servicio y rutas de configuración.
- `ng_siem_check_connectivity`, `ng_siem_min_free_kb`: validaciones previas opcionales.
- `ng_siem_has_docker_artifacts`: si existe artefacto Docker real, no usar instalación `.deb`.

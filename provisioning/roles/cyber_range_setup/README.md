# cyber_range_setup role

Prepara una base operativa verificable para el host `cyber_range`.

## Qué **sí** hace

- Incluye `common_bootstrap` con Docker habilitado para alinear el host con el resto del laboratorio.
- Valida parámetros mínimos del rol (directorios y ownership) con `assert`.
- Instala paquetes base realmente usados por scripts/operación del escenario:
  - runtime y utilidades (`bash`, `coreutils`, `curl`, `jq`, `python3`, `python3-pip`),
  - utilidades de red (`iproute2`, `net-tools`, `dnsutils`, `iputils-ping`, `traceroute`, `tcpdump`, `nmap`),
  - hardening/utilidades mínimas (`ca-certificates`, `unattended-upgrades`, `fail2ban`, `ufw`).
- Crea directorios de trabajo y logs (`/opt/cyber_range`, `/var/log/cyber_range` por defecto).
- Aplica hardening mínimo con un perfil sysctl idempotente en `/etc/sysctl.d/99-cyber-range-hardening.conf`.
- Valida artefactos de escenario del repositorio (en controlador) con `stat` + `assert/debug`:
  - `subcase_1b/scenario.yml`,
  - `subcase_1b/scripts/cyber_range_start.sh`,
  - `subcase_1b/scripts/lab_runner.sh`,
  - `subcase_1b/scripts/collect_artifacts.sh`.

## Qué **no** hace

- No despliega por sí solo todos los servicios de escenario completo (SIEM/SOAR/CICMS/BIPS/etc.).
- No intenta “inventar” artefactos faltantes.
- No soporta familias de OS fuera de Debian (falla explícitamente con `assert`).

## Limitación documentada cuando faltan artefactos

Para evitar un rol “vacío”, el comportamiento es explícito y verificable:

- `cyber_range_setup_require_full_target: true`  
  Falla si falta cualquier artefacto requerido.
- `cyber_range_setup_require_full_target: false` (default)  
  Continúa con la provisión base y registra una **limitación explícita** (`debug`) indicando qué artefactos faltan y que el target completo no quedó provisionado.

## Variables principales

Ver `defaults/main.yml`.

- `cyber_range_setup_work_dir`
- `cyber_range_setup_log_dir`
- `cyber_range_setup_owner`
- `cyber_range_setup_group`
- `cyber_range_setup_require_full_target`
- `cyber_range_setup_required_artifacts`
- `cyber_range_setup_packages_by_os_family`

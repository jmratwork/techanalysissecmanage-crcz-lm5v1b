# cyber_range_setup role

Prepara una base operativa verificable para el host `cyber_range`.

## What **does** it do

- Incluye `common_bootstrap` con Docker habilitado para alinear el host con el resto del laboratorio.
- Validate minimum role parameters (directories and ownership) with `assert`.
- Install base packages actually used by scripts/scenario operation:
  - runtime y utilidades (`bash`, `coreutils`, `curl`, `jq`, `python3`, `python3-pip`),
  - utilidades de red (`iproute2`, `net-tools`, `dnsutils`, `iputils-ping`, `traceroute`, `tcpdump`, `nmap`),
  - minimal hardening/utilities (`ca-certificates`, `unattended-upgrades`, `fail2ban`, `ufw`).
- Crea directorios de trabajo y logs (`/opt/cyber_range`, `/var/log/cyber_range` por defecto).
- Apply minimal hardening with an idempotent sysctl profile in `/etc/sysctl.d/99-cyber-range-hardening.conf`.
- Valida artefactos de escenario del repositorio (en controlador) con `stat` + `assert/debug`:
  - `subcase_1b/scenario.yml`,
  - `subcase_1b/scripts/cyber_range_start.sh`,
  - `subcase_1b/scripts/lab_runner.sh`,
  - `subcase_1b/scripts/collect_artifacts.sh`.

## What **doesn't** do

- It does not deploy all the full scenario services on its own (SIEM/SOAR/CICMS/BIPS/etc.).
- No intenta “inventar” artefactos faltantes.
- Does not support OS families outside of Debian (fails explicitly with `assert`).

## Documented limitation when artifacts are missing

To avoid an “empty” role, the behavior is explicit and verifiable:

- `cyber_range_setup_require_full_target: true`  
  Falla si falta cualquier artefacto requerido.
- `cyber_range_setup_require_full_target: false` (default)  
  Continue with the base provisioning and log an explicit limitation (`debug`) indicating which artifacts are missing and that the entire target was not provisioned.

## Variables principales

Ver `defaults/main.yml`.

- `cyber_range_setup_work_dir`
- `cyber_range_setup_log_dir`
- `cyber_range_setup_owner`
- `cyber_range_setup_group`
- `cyber_range_setup_require_full_target`
- `cyber_range_setup_required_artifacts`
- `cyber_range_setup_packages_by_os_family`

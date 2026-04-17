# randomization_platform role

Configure the randomization platform for Debian/Kali environments with minimal operational and idempotent:

- instala dependencias base del runtime (`bash`, `coreutils`),
- valida que exista el script artefacto esperado,
- crea `/var/log/randomization_platform`,
- deploys and manages a systemd service (or controlled execution without systemd).

## Variables principales

Ver `defaults/main.yml`.

- `randomization_platform_script_src`: ruta del script origen en el controlador.
- `randomization_platform_script_path`: destino en el host gestionado.
- `randomization_platform_user`: usuario/grupo para logs y servicio.
- `randomization_platform_service_name`: nombre de la unidad.
- `randomization_platform_manage_systemd`: enables/disables systemd deployment.
- `randomization_platform_service_enabled`: habilitar al arranque.
- `randomization_platform_service_state`: estado deseado (`started`, `stopped`, etc.).
- `randomization_platform_run_controlled_script`: ejecuta el script sin systemd cuando `manage_systemd` es `false`.

## Notas de uso

Por defecto el rol copia `subcase_1b/scripts/randomization_platform_start.sh` al host remoto.
If the artifact does not exist, the role fails with a helpful error message to aid diagnosis.

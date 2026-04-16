# randomization_platform role

Configura la plataforma de randomización para entornos Debian/Kali con un mínimo operativo e idempotente:

- instala dependencias base del runtime (`bash`, `coreutils`),
- valida que exista el script artefacto esperado,
- crea `/var/log/randomization_platform`,
- despliega y gestiona un servicio systemd (o ejecución controlada sin systemd).

## Variables principales

Ver `defaults/main.yml`.

- `randomization_platform_script_src`: ruta del script origen en el controlador.
- `randomization_platform_script_path`: destino en el host gestionado.
- `randomization_platform_user`: usuario/grupo para logs y servicio.
- `randomization_platform_service_name`: nombre de la unidad.
- `randomization_platform_manage_systemd`: activa/desactiva despliegue systemd.
- `randomization_platform_service_enabled`: habilitar al arranque.
- `randomization_platform_service_state`: estado deseado (`started`, `stopped`, etc.).
- `randomization_platform_run_controlled_script`: ejecuta el script sin systemd cuando `manage_systemd` es `false`.

## Notas de uso

Por defecto el rol copia `subcase_1b/scripts/randomization_platform_start.sh` al host remoto.
Si el artefacto no existe, el rol falla con un mensaje de error útil para facilitar el diagnóstico.

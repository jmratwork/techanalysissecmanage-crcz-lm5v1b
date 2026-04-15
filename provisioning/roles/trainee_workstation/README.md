# trainee_workstation role

Instala herramientas operativas para el host `trainee_workstation` con mapeo de paquetes
por distribución para tolerar diferencias entre Kali y Debian.

## Paquetes gestionados

Por defecto instala:

- `nmap`
- `gvm`
- `gvm-tools` (provee `gvm-cli`)
- `zaproxy`
- `python3-pip`

Si un paquete no existe en los repositorios configurados, el rol no aborta la ejecución;
registra mensajes claros indicando qué paquete no se pudo instalar y continúa.

## Caldera CLI (opcional)

El flujo actual contiene acciones que invocan `caldera run` (por ejemplo,
`subcase_1b/scripts/lab_runner.sh` y `subcase_1b/training_platform/app.py`).
Para reflejar esta dependencia sin forzar su instalación en todos los entornos, se expone:

- `install_caldera_cli` (bool, default `false`)
- `trainee_workstation_caldera_cli_package` (string, default `caldera-cli`)

Actívalo cuando tu repositorio/imagen proporcione dicho paquete.

## Variables

```yaml
install_caldera_cli: false
trainee_workstation_caldera_cli_package: caldera-cli
trainee_workstation_packages_by_distribution:
  Kali:
    - nmap
    - gvm
    - gvm-tools
    - zaproxy
    - python3-pip
  Debian:
    - nmap
    - gvm
    - gvm-tools
    - zaproxy
    - python3-pip
```

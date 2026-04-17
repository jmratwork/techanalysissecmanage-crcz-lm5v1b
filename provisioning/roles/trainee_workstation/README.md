# trainee_workstation role

Instala herramientas operativas para el host `trainee_workstation` con mapeo de paquetes
by distribution to tolerate differences between Kali and Debian.

## Paquetes gestionados

Por defecto instala:

- `nmap`
- `gvm`
- `gvm-tools` (provee `gvm-cli`)
- `zaproxy`
- `python3-pip`

If a package does not exist in the configured repositories, the role does not abort the execution;
logs clear messages indicating which package could not be installed and continues.

## Caldera CLI (opcional)

El flujo actual contiene acciones que invocan `caldera run` (por ejemplo,
`subcase_1b/scripts/lab_runner.sh` y `subcase_1b/training_platform/app.py`).
To reflect this dependency without forcing its installation in all environments, we expose:

- `install_caldera_cli` (bool, default `false`)
- `trainee_workstation_caldera_cli_package` (string, default `caldera-cli`)

Activate it when your repository/image provides such a package.

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

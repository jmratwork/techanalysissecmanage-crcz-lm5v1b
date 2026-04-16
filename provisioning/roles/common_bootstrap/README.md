# common_bootstrap role

Rol reusable de bootstrap para hosts canónicos.

## Objetivo

- Instalar paquetes base por familia de SO.
- Opcionalmente bootstrapear Docker Engine + plugins cuando `common_bootstrap_install_docker: true`.
- Evitar duplicación: los roles SOC (`bips`, `ng_siem`, `cicms`, `ng_soar`) consumen este rol y no deben reinstalar Docker por su cuenta.

## Variables principales

- `common_bootstrap_base_packages`: mapa por `os_family` para paquetes base.
- `common_bootstrap_install_docker`: activa flujo de Docker bootstrap.
- `common_bootstrap_manage_docker_service`: controla `enabled/started` del servicio Docker.
- `common_bootstrap_docker_users`: usuarios a añadir al grupo `docker`.
- `common_bootstrap_docker_packages`: paquetes Docker a instalar.

## Dependencias de colecciones

Los roles SOC usan módulos `community.docker.*` para despliegues en modo Docker.
Antes de ejecutar provisioning/lint en entornos limpios instala:

```bash
ansible-galaxy collection install -r provisioning/requirements.yml
```

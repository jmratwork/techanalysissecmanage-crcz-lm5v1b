# Provisioning Subcase 1b Packages

This sandbox directory provides packaging notes and helper scripts, but **does not define its own
provisioning logic**. The single operational provisioning flow uses the canonical root playbook:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

For compatibility, `site.yml` in this folder is only a wrapper (`import_playbook`) that delegates to
`../../provisioning/playbook.yml`.

> Regla de operación: este árbol no es un segundo entrypoint de provisioning.
> Úsalo solo para empaquetado/compatibilidad; toda lógica funcional vive en `provisioning/`.

## Alcance de este directorio (wrapper-only)

- `site.yml` debe permanecer como wrapper (`import_playbook`) sin tareas propias de aprovisionamiento.
- No se deben añadir aquí catálogos de paquetes, recetas de instalación manual ni defaults operativos.
- Las variables y artefactos reales de despliegue se definen en `provisioning/group_vars/*.yml` y `provisioning/roles/**`.
- Cualquier ajuste funcional debe implementarse únicamente en `provisioning/`.

## Nota sobre documentación de paquetes

Para evitar flujos competidores o placeholders engañosos, este árbol no mantiene tablas de paquetes ni
instrucciones de instalación manual. La única referencia operativa válida para aprovisionamiento es
`provisioning/README.md`.

## Trainee workstation tool versions

The `build_trainee_workstation.sh` script installs pre-downloaded packages for the trainee
workstation. The following versions are bundled and verified using SHA256 hashes:

| Tool | Version | Verification command |
|------|---------|---------------------|
| Nmap | 7.93+dfsg1-1 | `nmap --version` |
| GVM  | 25.04.0 | `gvmd --version` |
| OWASP ZAP | 2.16.1 | `zaproxy -version` |
| Caldera | 5.3.0 | `python3 /opt/caldera/server.py --help` |

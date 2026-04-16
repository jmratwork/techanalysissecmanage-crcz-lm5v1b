# Ansible Playbooks for Subcase 1b

These playbooks deploy BIPS, CICMS, NG-SIEM, and NG-SOAR components.

> **Note:** The canonical playbook and inventory now live in the repository-level `provisioning/` directory so you can run Ansible from the repo root. Use `provisioning/playbook.yml` together with `provisioning/inventory.ini` for day-to-day deployments.

## Variables

- `ngsoar_repo_url`: Base URL for NG-SOAR package repository. Defaults to `https://packages.internal.example.com`. Override in inventory or group vars to use environment-specific repositories.

## Compatibilidad y entrypoint canónico

Este directorio se mantiene solo por compatibilidad de rutas heredadas.

- **Entrypoint canónico Subcaso 1b:** `provisioning/playbook.yml`
- **Inventario canónico:** `provisioning/inventory.ini`
- **Estado de `subcase_1b/ansible/roles/**`:** snapshot legado / **no canónico** / fuera del runtime principal.
- **Regla de mantenimiento:** no editar `subcase_1b/ansible/roles/**` para cambios funcionales; cualquier cambio de comportamiento debe implementarse en `provisioning/roles/**` y consumirse desde el entrypoint canónico.
- **Regla operativa:** no ejecutar aprovisionamiento diario con este árbol; usar siempre el comando canónico desde la raíz.
- **Referencia explícita:** ver `subcase_1b/ansible/roles/README.md` para la política de uso de los roles legacy.

Comando recomendado (desde la raíz del repo):

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

`subcase_1b/ansible/playbook.yml` ahora es un wrapper (`import_playbook`) hacia el playbook canónico para evitar divergencias entre árboles de roles/playbooks.

Opcional recomendado: reemplazar contenido legacy por wrappers o eliminarlo si no se usa en runtime de KYPO, dejando solo `playbook.yml` wrapper en este árbol de compatibilidad.

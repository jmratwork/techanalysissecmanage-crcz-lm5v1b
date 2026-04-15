# Ansible Playbooks for Subcase 1b

These playbooks deploy BIPS, CICMS, NG-SIEM, and NG-SOAR components.

> **Note:** The canonical playbook and inventory now live in the repository-level `provisioning/` directory so you can run Ansible from the repo root. Use `provisioning/playbook.yml` together with `provisioning/inventory.ini` for day-to-day deployments.

## Variables

- `ngsoar_repo_url`: Base URL for NG-SOAR package repository. Defaults to `https://packages.internal.example.com`. Override in inventory or group vars to use environment-specific repositories.

## Compatibilidad y entrypoint canónico

Este directorio se mantiene solo por compatibilidad de rutas heredadas.

- **Entrypoint canónico Subcaso 1b:** `provisioning/playbook.yml`
- **Inventario canónico:** `provisioning/inventory.ini`

Comando recomendado (desde la raíz del repo):

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

`subcase_1b/ansible/playbook.yml` ahora es un wrapper (`import_playbook`) hacia el playbook canónico para evitar divergencias entre árboles de roles/playbooks.

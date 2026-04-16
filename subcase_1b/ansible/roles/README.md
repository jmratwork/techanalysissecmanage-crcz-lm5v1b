# Legacy roles snapshot (non-canonical)

This directory is kept only as a **legacy snapshot** for historical traceability.
It is **not** part of the canonical provisioning execution path.

Canonical Subcase 1b provisioning entrypoint:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

Compatibility wrappers that delegate to canonical provisioning:

- `subcase_1b/ansible/playbook.yml`
- `sandboxes/provisioning_subcase_1b/site.yml`

## Maintenance rule

- Do **not** introduce new functional provisioning logic in this directory.
- Do **not** treat these roles as runtime source of truth.
- Implement behavior changes only under `provisioning/roles/**`.

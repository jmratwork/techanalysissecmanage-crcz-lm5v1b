# Ansible compatibility wrapper for Subcase 1b

This directory is no longer a stand-alone operational implementation.
It is retained only for legacy route compatibility.

## Compatibility and canonical entrypoint

This directory is kept only for legacy path compatibility.

- **Canonical Entrypoint Subcase 1b:** `provisioning/playbook.yml`
- **Canonical inventory:** `provisioning/inventory.ini`
- **State of `subcase_1b/ansible/roles/**`:** legacy snapshot / **non-canonical** / outside the main runtime.
- **Maintenance rule:** do not edit `subcase_1b/ansible/roles/**` for functional changes; any behavior changes should be implemented in `provisioning/roles/**` and consumed from the canonical entrypoint.
- **Operating rule:** do not run daily provisioning with this tree; always use the canonical command from the root.
- **Explicit reference:** see `subcase_1b/ansible/roles/README.md` for the policy on using legacy roles.

Recommended command (from repo root):

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

`subcase_1b/ansible/playbook.yml` is now a wrapper (`import_playbook`) towards the canonical playbook to avoid divergences between role trees/playbooks.

Optional recommended: replace legacy content with wrappers or remove it if not used in KYPO runtime, leaving only `playbook.yml` wrapper in this compatibility tree.

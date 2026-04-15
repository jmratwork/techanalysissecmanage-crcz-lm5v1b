# Provisioning Playbook

`provisioning/playbook.yml` is the **canonical entry point** for Subcase 1b infrastructure provisioning.
All provisioning roles and host-specific configuration must be maintained from this root playbook and
its roles under `provisioning/roles/`.

## Single operational flow

Run provisioning from the repository root with the canonical inventory and playbook:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

A compatibility wrapper exists at `sandboxes/provisioning_subcase_1b/site.yml` and simply imports the
canonical root playbook. Do not duplicate provisioning tasks in sandbox playbooks.

The inventory groups map 1:1 with topology hostnames using snake_case (`training_platform`,
`trainee_workstation`, `cyber_range`, `randomization_platform`, `bips`, `ng_siem`, `cicms`,
`ng_soar`, `router`).

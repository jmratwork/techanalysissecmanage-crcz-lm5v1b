# Provisioning Playbook

Root-level Ansible assets for deploying the Subcase 1b cyber range scenario live under this `provisioning/` directory. The playbook references the roles needed to configure the cyber range, trainee workstation, training platform, and SOC components.

## Run the playbook

Use the bundled inventory and playbook from the repository root:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

The inventory groups map 1:1 with the topology hostnames using snake_case (`training_platform`, `trainee_workstation`, `cyber_range`, `randomization_platform`, `bips`, `ng_siem`, `cicms`, `ng_soar`, `router`).

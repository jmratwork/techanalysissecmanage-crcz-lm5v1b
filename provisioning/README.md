# Provisioning Playbook

Root-level Ansible assets for deploying the Subcase 1b cyber range scenario live under this `provisioning/` directory. The playbook references the roles needed to configure the cyber range, trainee workstation, training platform, and SOC components.

## Run the playbook

Use the bundled inventory and playbook from the repository root:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

The inventory groups map to the training platform, trainee workstation, SOC server, and the combined `cyber_range` group defined in `inventory.ini`.

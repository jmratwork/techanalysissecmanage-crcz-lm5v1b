# CRCZ/KYPO Deployment Manual

This manual describes how to deploy KYPO training scenarios in this repository. It covers uploading a scenario to the KYPO portal, preparing virtual machines, orchestrating services, and cleaning up afterward.

## Scenario Upload

1. **Validate and package the training**
   ```bash
   kypo training validate training.yaml
   kypo training pack training.yaml
   ```
2. **Upload to KYPO**
   - Using the web portal: create a new training and upload the generated package.
   - Using the CLI:
     ```bash
     kypo training publish training.yaml
     ```
3. **Confirm availability**
   - The training should appear in the KYPO interface and be assignable to exercises.
   - Ensure repository paths referenced in `scenario.yml` files are accessible.

## VM Preparation

1. **Import base images** – Upload or select images for each VM role (e.g., trainee workstation, BIPS, NG‑SIEM).
2. **Update and configure**
   - Apply package updates.
   - Configure network interfaces and hostnames.
   - Create service accounts and SSH keys as required.
3. **Snapshot** – Take a snapshot of each VM after configuration so it can be restored for future exercises.

## Offline Environments

For systems without Internet access, pre-download required packages and modules used by the subcase 1b environment:

- Copy any necessary `.deb` files (e.g., Docker engine and Compose plugin) to `/opt/offline` so that startup scripts can install them without reaching external mirrors.
- Save PowerShell modules for offline use if Windows assets are involved:
  ```powershell
  Save-Module -Name PowerShellGet,PackageManagement -Path /opt/offline/psmodules
  ```
- Ensure these paths are available on the target machines before running the scenario scripts.

## Service Orchestration

1. **Provision VMs** – Start VMs from the prepared images or snapshots and verify connectivity.
2. **Run canonical provisioning**
   ```bash
   ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
   ```
   For focused operations, use `--limit` (for example `--limit training_platform`).
3. **Use scripts only as compatibility helpers**
   - `subcase_1b/scripts/*.sh` remain available for lab/bootstrap scenarios, but are not a second canonical provisioning implementation.
   - Prefer the Ansible-managed systemd/nginx services created by `provisioning/roles/**`.
4. **Validate operation**
   - Confirm ports are listening and dashboards are reachable.
   - Run the scenario‑specific validation steps from the respective guide.

## Teardown

1. **Stop the scenario** from the KYPO dashboard.
2. **Shut down services** using the provided stop scripts or `systemctl stop` commands.
3. **Archive artifacts** such as logs, reports, and captured packets for after‑action review.
4. **Remove temporary resources** including VM instances or storage volumes not needed after the exercise.

## Environment Reset

1. **Revert snapshots** or destroy and recreate VMs to return to a clean state.
2. **Clear persistent data** – Remove leftover logs, temporary files, and database contents.
3. **Reset network configuration** – Delete custom routes or firewall rules applied for the scenario.
4. **Verify baseline** – Ensure no services are running and that the environment matches the initial configuration before the next deployment.

Following these steps ensures consistent deployments and clean teardowns for all scenarios in this repository.

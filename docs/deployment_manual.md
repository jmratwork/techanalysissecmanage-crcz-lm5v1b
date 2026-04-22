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
2. **Apply network addressing contract before deployment**
   - `training-net` subnet: `10.10.0.0/24`.
   - Reserved infrastructure addresses:
     - `10.10.0.1` → router/gateway.
     - `10.10.0.2-10.10.0.9` → static service IPs.
   - DHCP allocation pool for dynamic ports: `10.10.0.20-10.10.0.254`.
   - This is implemented in topology definitions and in the generated `openstack_networking_subnet_v2`.
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
   - Confirm DHCP does not consume infrastructure static IPs:
     ```bash
     openstack port list --network training-net --device-owner network:dhcp -f value -c "Fixed IP Addresses"
     ```
     The returned DHCP port IPs must be outside `10.10.0.1-10.10.0.19`.
3. **Run `deploy.tf` with reconciliation before `tofu apply`**
   ```bash
   tofu init
   tofu plan
   OS_PROJECT_ID=<target-project-id> ./scripts/reconcile_training_net_ports.sh
   tofu apply
   ```
   The reconciliation script checks existing Neutron ports in `training-net` (`10.10.0.0/24`) for the target project and fails fast if static IPs reserved by this deployment (`10.10.0.1`, `10.10.0.2-10.10.0.9`) are already allocated by resources that are not currently tracked in OpenTofu state.
4. **Operator recovery path for partial applies or stale ports**
   - **Option A: import existing ports into state** when the ports are valid and should be managed by this stack:
     ```bash
     tofu import openstack_networking_port_v2.training_platform_training_net <port-id-for-10.10.0.2>
     tofu import openstack_networking_port_v2.trainee_workstation_training_net <port-id-for-10.10.0.3>
     tofu import openstack_networking_port_v2.cyber_range_training_net <port-id-for-10.10.0.4>
     tofu import openstack_networking_port_v2.randomization_platform_training_net <port-id-for-10.10.0.5>
     tofu import openstack_networking_port_v2.bips_training_net <port-id-for-10.10.0.6>
     tofu import openstack_networking_port_v2.ng_siem_training_net <port-id-for-10.10.0.7>
     tofu import openstack_networking_port_v2.cicms_training_net <port-id-for-10.10.0.8>
     tofu import openstack_networking_port_v2.ng_soar_training_net <port-id-for-10.10.0.9>
     ```
   - **Option B: remove stale/orphaned ports** if they should not exist, then rerun:
     ```bash
     openstack port delete <stale-port-id> [<stale-port-id> ...]
     OS_PROJECT_ID=<target-project-id> ./scripts/reconcile_training_net_ports.sh
     tofu apply
     ```
   This recovery flow prevents repeated `tofu apply` failures and makes partial-apply cleanup explicit and safe.

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

# CYNET Topology Overview

## Subcase 1b
- Network segment `training_net` (10.10.0.0/24)
- Virtual machines (canonical host naming):
  - **training_platform** – Debian 11
  - **trainee_workstation** – Kali
  - **cyber_range** – Debian 11
  - **randomization_platform** – Debian 11
  - **bips** – Debian 11
  - **ng_siem** – Debian 11
  - **cicms** – Debian 11
  - **ng_soar** – Debian 11
  - **router** – Debian 11 (declared in inventory; `router_noop` role only, no active provisioning in this repository)

### Provisioning status for Subcase 1b

Based on the canonical playbook (`provisioning/playbook.yml`):

- **Active provisioning roles**:
  - `training_platform`
  - `trainee_workstation`
  - `cyber_range` (role `cyber_range_setup`)
  - `randomization_platform`
  - `bips`
  - `ng_siem`
  - `cicms`
  - `ng_soar`
- **Documented no-op host**:
  - `router` (role `router_noop`)

## Subcase 1c
- Network segment `malnet` (10.20.0.0/24)
- Virtual machines:
  - **infected_host** – Kali
  - **c2_server** – Debian 11
  - **soc_server** – Debian 11 (**legacy/isolated**: not part of canonical Subcase 1b inventory or provisioning flow)
  - **cti_component** – Debian 11

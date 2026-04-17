# Canonical supply contract (Subcase 1b)

This document defines the **operational source of truth** for provisioning.
Si otro archivo contradice este contrato, este contrato tiene prioridad.

## Single canonical source

- **Canonical playbook:** `provisioning/playbook.yml`
- **Canonical inventory:** `provisioning/inventory.ini`
- **Subcase Topology 1b:** `sandboxes/topology_subcase_1b.yaml`

Single operating command:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

## Allowed wrappers (compatibility only)

The following files exist for compatibility/packaging and **cannot** contain alternative functional logic:

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Rule: they must delegate by `import_playbook` to the canonical playbook.

## Contrato de coherencia verificable

To consider the repository coherent in Subcase 1b, all these rules must be met:

1. Every host/router in `sandboxes/topology_subcase_1b.yaml` exists in the canonical inventory.
2. Each canonical group in the inventory has a corresponding `hosts:` block in `provisioning/playbook.yml`.
3. `subcase_1b:children` exclusively includes canonical groups from Subcase 1b.
4. There is no `soc_server` in canonical inventory/playbook.
5. `router` uses explicit `router_noop` ​​role (final decision: out of functional scope in this repository).

### Shutdown acceptance criteria (unmanaged router)

The Subcase 1b provisioning project is considered **complete** without a managed router if, and only if, all of the following are met:

1. Host `router` exists in canonical topology/inventory/playbook.
2. The `router` block in `provisioning/playbook.yml` references only the `router_noop` ​​role.
3. The `router_noop` ​​role does not configure network/firewall/NAT/routing; it only leaves explicit evidence of “out of reach.”
4. The canonical documentation (`docs/canonical_provisioning_contract.md` and `provisioning/README.md`) maintains this decision unambiguously.

These rules are partially automated by `tests/test_provisioning_coherence.py`.

## Status per host/group (canonical)

| Host/group | State in canonical flow | Role(s) |
|---|---|---|
| `training_platform` | Activo | `training_platform` |
| `trainee_workstation` | Activo | `trainee_workstation` |
| `cyber_range` | Activo | `cyber_range_setup` |
| `randomization_platform` | Active (actual minimum) | `randomization_platform` |
| `bips` | Activo | `common_bootstrap` + `bips` |
| `ng_siem` | Activo | `common_bootstrap` + `ng_siem` |
| `cicms` | Activo | `common_bootstrap` + `cicms` |
| `ng_soar` | Activo | `common_bootstrap` + `ng_soar` |
| `router` | Explicit no-op | `router_noop` ​​|
| `soc_server` | Legacy/deprecated | Out of canonical flow |

## Scope and limits

- Este repositorio **no** levanta Open edX, MISP, IRIS ni KYPO como servicios internos del playbook.
- Router network management (NAT/firewall/routing) is **officially out of scope** in this repository; only `router_noop` ​​is kept as a contractual marker.
- Estas integraciones dependen de variables/credenciales externas.
- If material is missing for a complete deployment of a component, it must be documented as a real limitation or use an explicit minimum/no-op role.

## Maintenance policy

- Cambios funcionales: `provisioning/roles/**`.
- Do not introduce parallel provisioning logic in `sandboxes/**` or `subcase_1b/ansible/**`.
- Final policy for `subcase_1b/ansible/roles/**`: **retain legacy snapshot in read-only mode** for traceability/compatibility, without functional changes or use as a canonical source.
- Any change in naming/topology/inventory/playbook must update this contract and the main documentation in the same delivery.

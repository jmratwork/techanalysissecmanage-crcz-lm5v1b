# Contrato canónico de aprovisionamiento (Subcaso 1b)

Este documento define la **fuente de verdad operativa** para el aprovisionamiento.
Si otro archivo contradice este contrato, este contrato tiene prioridad.

## Fuente canónica única

- **Playbook canónico:** `provisioning/playbook.yml`
- **Inventario canónico:** `provisioning/inventory.ini`
- **Topología de Subcaso 1b:** `sandboxes/topology_subcase_1b.yaml`

Comando operativo único:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

## Wrappers permitidos (solo compatibilidad)

Los siguientes archivos existen por compatibilidad/packaging y **no** pueden contener lógica funcional alternativa:

- `sandboxes/provisioning_subcase_1b/site.yml`
- `subcase_1b/ansible/playbook.yml`

Regla: deben delegar por `import_playbook` al playbook canónico.

## Contrato de coherencia verificable

Para considerar el repositorio coherente en Subcaso 1b, deben cumplirse todas estas reglas:

1. Cada host/router de `sandboxes/topology_subcase_1b.yaml` existe en el inventario canónico.
2. Cada grupo canónico del inventario tiene bloque `hosts:` correspondiente en `provisioning/playbook.yml`.
3. `subcase_1b:children` incluye exclusivamente grupos canónicos de Subcaso 1b.
4. No existe `soc_server` en inventario/playbook canónicos.
5. `router` usa rol `router_noop` explícito (decisión final: fuera de alcance funcional en este repositorio).

### Criterio de aceptación de cierre (router no gestionado)

El proyecto de aprovisionamiento de Subcaso 1b se considera **completo** sin router gestionado si, y solo si, se cumple todo lo siguiente:

1. El host `router` existe en topología/inventario/playbook canónicos.
2. El bloque `router` en `provisioning/playbook.yml` referencia únicamente el rol `router_noop`.
3. El rol `router_noop` no configura red/firewall/NAT/routing; solo deja evidencia explícita de “fuera de alcance”.
4. La documentación canónica (`docs/canonical_provisioning_contract.md` y `provisioning/README.md`) mantiene esta decisión sin ambigüedad.

Estas reglas están parcialmente automatizadas por `tests/test_provisioning_coherence.py`.

## Estado por host/grupo (canónico)

| Host/grupo | Estado en flujo canónico | Rol(es) |
|---|---|---|
| `training_platform` | Activo | `training_platform` |
| `trainee_workstation` | Activo | `trainee_workstation` |
| `cyber_range` | Activo | `cyber_range_setup` |
| `randomization_platform` | Activo (mínimo real) | `randomization_platform` |
| `bips` | Activo | `common_bootstrap` + `bips` |
| `ng_siem` | Activo | `common_bootstrap` + `ng_siem` |
| `cicms` | Activo | `common_bootstrap` + `cicms` |
| `ng_soar` | Activo | `common_bootstrap` + `ng_soar` |
| `router` | No-op explícito | `router_noop` |
| `soc_server` | Legacy/deprecado | Fuera de flujo canónico |

## Alcance y límites

- Este repositorio **no** levanta Open edX, MISP, IRIS ni KYPO como servicios internos del playbook.
- La gestión de red del `router` (NAT/firewall/routing) queda **oficialmente fuera de alcance** en este repositorio; se conserva solo `router_noop` como marcador contractual.
- Estas integraciones dependen de variables/credenciales externas.
- Si falta material para un despliegue completo de un componente, se debe documentar como limitación real o usar un rol mínimo/no-op explícito.

## Política de mantenimiento

- Cambios funcionales: `provisioning/roles/**`.
- No introducir lógica de aprovisionamiento paralela en `sandboxes/**` ni `subcase_1b/ansible/**`.
- Política final para `subcase_1b/ansible/roles/**`: **retener snapshot legacy en modo solo lectura** para trazabilidad/compatibilidad, sin cambios funcionales ni uso como fuente canónica.
- Cualquier cambio de naming/topología/inventario/playbook debe actualizar este contrato y la documentación principal en la misma entrega.

# NG‑SOC Components Matrix (reference template)

> ⚠️ This file is a **documentation template only**.
> It is **not** consumed by canonical provisioning and does not define deployable values.
> Do not copy values from here directly into production/group vars without replacing them with environment-specific data.

Canonical provisioning source of truth:
- `provisioning/playbook.yml`
- `provisioning/inventory.ini`

| Tool | Version (example) | NG-SOC Component | Open Source | Partner | Documentation (example URL) |
|------|--------------------|------------------|-------------|---------|------------------------------|
| BIPS | Define in your environment | BIPS | Define in your environment | Define in your environment | https://example.com/bips |
| NG-SIEM | Define in your environment | NG-SIEM | Define in your environment | Define in your environment | https://example.com/ng-siem |
| NG-SOAR | Define in your environment | NG-SOAR Platform | Define in your environment | Define in your environment | https://example.com/ng-soar |
| CICMS | Define in your environment | CICMS | Define in your environment | Define in your environment | https://example.com/cicms |
| MISP | Define in your environment | CTI Component | Define in your environment | Define in your environment | https://example.com/misp |

> ℹ️ For executable configuration, use `provisioning/group_vars/*.example.yml` as the only supported starting point and replace every `__REQUIRED_*__` value before execution.

# SOC Analyst Playbook

This playbook guides analysts through NG-SOAR dashboards, typical search queries, and criteria for confirming alerts. It also highlights CACAO playbooks executed through Act.

## Dashboard Navigation

1. **Access Kibana** at `http://localhost:5602` and log in with analyst credentials.
2. Navigate to the **Security** app to view correlated alerts.
3. Use the **Discover** tab for raw event inspection and timeline analysis.
4. Open the **Dashboards** section for visual summaries of BIPS, NG‑SIEM, and CICMS data.

## Search Queries

- `BenignMalwareSim` – confirm logs from the simulator reach NG‑SIEM.
- `event.type:alert and host.name:win-*` – list alerts from Windows hosts.
- `source.ip:192.0.2.* and destination.port:9001` – trace beacon traffic to the C2 server.
- `process.executable:*powershell* and event.action:creation` – identify suspicious PowerShell usage.

## Confirming Alerts

An alert is considered confirmed when:

1. **Correlation** – Indicators match threat intelligence entries in MISP and align with simulator activity.
2. **Host Verification** – Host logs show associated processes, files, or registry changes.
3. **Network Evidence** – NG‑SIEM or packet captures show traffic consistent with the alert.
4. **No Benign Explanation** – Cross‑check with training scripts to rule out expected actions.
5. Record confirmation in CICMS/Act via the appropriate API calls.

## Automation References

| Artifact | Purpose | When to Use |
|---------|---------|-------------|
| [`subcase_1b/caldera_profiles/discovery.json`](../subcase_1b/caldera_profiles/discovery.json) | Documents the Caldera actions executed during lab runs. | Review when correlating trainee activity with NG‑SIEM alerts or validating lab_runner output. |
| `subcase_1b/scripts/lab_runner.sh` | Executes approved reconnaissance and exploitation steps against the KYPO lab. | Use as the canonical sequence when reconstructing expected alert patterns. |
| `subcase_1b/scripts/collect_artifacts.sh` | Packages logs for after-action analysis. | Run after evaluations to capture evidence referenced in incident timelines. |

Following this guide ensures analysts can navigate dashboards, perform targeted searches, confirm alerts, and tie findings back to the approved automation in the subcase 1b environment.

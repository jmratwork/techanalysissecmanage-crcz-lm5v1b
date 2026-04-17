# Training Materials and Workflows

This document outlines the theoretical training materials and the workflow expectations for both trainees and instructors operating within the KYPO cyber range environment. The primary scenario focuses on penetration testing and vulnerability assessment training using a Cyber Range environment that mirrors CYNET's network. Participants learn how to discover and document vulnerabilities while following organizational procedures. For operational alert triage in NG‑SOAR tools, refer to the [SOC Analyst Playbook](soc_analyst_playbook.md).

## Theoretical Background

Trainees should familiarize themselves with fundamental concepts in network security, incident response, and malware analysis prior to beginning exercises. Recommended topics include:

- Fundamentals of TCP/IP networking
- Common attack vectors and the kill chain methodology
- Basics of log analysis and threat intelligence
- Overview of vulnerability assessment and penetration testing methodologies

## Registration

Trainees are invited and registered through the training platform CLI in
`subcase_1b/training_platform/cli.py`. The script contacts the Open edX
service via `open_edx_client.py` to create course entries and confirm the
enrollment.

Canonical setup for the training platform must be executed via Ansible:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit training_platform
```

`subcase_1b/scripts/training_platform_start.sh` remains available as a
compatibility/lab helper and must not be treated as a second canonical
provisioning implementation.

## Lab run

Once enrolled, trainees launch the hands‑on lab in the KYPO cyber range.
Canonical provisioning for the lab hosts is executed with:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml --limit subcase_1b
```

Compatibility scripts (for local/demo orchestration) can still be used where
appropriate, for example `subcase_1b/scripts/cyber_range_start.sh` and
`subcase_1b/scripts/trainee_start.sh --target <ip>`.

Scenario specifics are described in `subcase_1b/scenario.yml` and the
corresponding topology file `sandboxes/topology_subcase_1b.yaml`.

## Evaluation

Exercise results are submitted to the new results module implemented in
`subcase_1b/training_platform/results_service.py`. The service appends
entries to `results.json` and relays progress back to Open edX using the
same `open_edx_client.py` helper so that learner dashboards reflect the
outcome of the lab.

## Trainee Workflow

1. **Scenario Preparation** – Review the scenario description and objectives. Ensure access to required accounts and tools within CyberRangeCZ.
2. **Hands-on Investigation** – Use the training platform (canonical access via nginx on `http://<training_platform_host>/`) to follow course instructions and run semi-automated penetration tests against the Cyber Range.
3. **Reporting** – Compile findings into an assessment report, highlighting discovered vulnerabilities, applicable policy references, and suggested mitigations.

## Instructor Workflow

1. **Monitoring** – Ensure the Cyber Range and training platform are functioning and collect trainee reports.
2. **Evaluation** – Review results, correlate findings where necessary, and provide feedback or remediation guidance.

### Evaluation Flow Integration

Both trainees and instructors can submit exercise outcomes through the
training platform's `POST /results` endpoint. The service stores metrics
such as completion time and quiz scores in `results.json`, updates local
course progress, and relays that progress to the Open edX
`/courseware/progress` API so that learner dashboards show the latest status.

### API Usage

#### Trainees

- `POST /register` – create a trainee account.
- `POST /login` – exchange credentials for an authentication token.
- `POST /progress` / `GET /progress` – submit or fetch course progress.
- `POST /results` – manually upload lab scores and timing data.

#### Instructors

- `POST /courses` – create a new course shell.
- `POST /invites` – generate invite codes for trainees.
- `GET /courses` – list existing courses and metadata.
- `POST /results` – record evaluation outcomes for a trainee.

## Subcase 1b: Penetration Testing Deep Dive

Trainees and instructors work entirely within the subcase 1b environment. The following checkpoints keep exercises aligned with the intended workflow:

### Trainee Activities

1. **Lab Deployment** – Launch the lab via the KYPO interface using the packaged topology from `sandboxes/topology_subcase_1b.yaml`. *Validation:* all machines report a **running** state. *Artifacts:* exported topology and a screenshot of the lab status.
2. **Execute Approved Tools** – Run the predefined scans with `subcase_1b/scripts/lab_runner.sh --target <ip>` or the Nmap/ZAP/Caldera actions exposed by the training platform’s `/launch_tool` endpoint. *Validation:* logs in `/var/log/trainee/lab_runner.log` show successful reconnaissance and operation triggers. *Artifacts:* saved command output and collected logs.
3. **Collect Findings** – Document discovered vulnerabilities and cross‑reference them with course objectives. *Validation:* findings match the expected services and ports outlined in `subcase_1b/scenario.yml`. *Artifacts:* trainee report draft and supporting screenshots.
4. **Submit Results** – Post scores through the platform’s `/results` endpoint or via the UI. *Validation:* entries appear in `results.json` and dashboards reflect completion. *Artifacts:* submission receipts or API responses.

### Instructor Activities

1. **Monitor Deployments** – Confirm KYPO orchestration completed without errors and that Docker services started via `subcase_1b/scripts/cyber_range_start.sh`. *Artifacts:* orchestrator logs and `/var/log/cyber_range/launch.log`.
2. **Validate Tool Runs** – Review `lab_runner.log` and the Caldera profile results in `subcase_1b/caldera_profiles/discovery.json` to verify expected actions were executed. *Artifacts:* log excerpts and any generated reports.
3. **Grade Submissions** – Use the training platform results service (`subcase_1b/training_platform/results_service.py`) to cross‑check submitted metrics and manually graded items. *Artifacts:* grading notes and updated `results.json` entries.

These workflows keep the scenario focused on penetration testing while providing instructors with clear checkpoints for validation and grading.

## Post-Incident Reporting and Iteration

Run `subcase_1b/scripts/collect_artifacts.sh` once evaluations are complete to gather NG‑SIEM extracts, lab runner logs, and training platform outputs. Review the resulting archive following the guidance in `docs/post_incident_process.md` and update course content before the next training cycle. When the IRIS case poller processes a closed case it also tags the related MISP event, executes `scripts/update_bips_model.sh` to trigger any available analytics refresh, and runs `scripts/commit_playbooks.sh` to version updated automation profiles (creating a Git commit when changes are present). Results of these actions are appended to `sequence.log` for auditing, and any missing helper scripts are noted without interrupting case processing.

## Log Retrieval and Analysis

Shell commands executed on trainee and target machines are stored in `/var/log/commands.log` and forwarded to the NG‑SIEM by Filebeat. To review activity:

1. Access the NG‑SIEM dashboard (Kibana) and search the `commands` index for specific hosts or time ranges.
2. Correlate command logs with other indexes such as alerts from BIPS or NG‑SOAR to trace trainee actions and resulting events.
3. For offline review, fetch `/var/log/commands.log` from the relevant machine and analyze it with standard tools like `less`, `grep` or timeline analysis utilities.

These logs provide detailed insight into trainee behavior and support both real‑time monitoring and post‑exercise assessments.

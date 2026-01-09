# TechAnalysisSecManage CRCZ

This repository provides complete, ready‑to‑deploy instructions for double CyberRangeCZ scenarios using only the NG‑SOC components from the activity diagram: BIPS, NG‑SIEM, NG‑SOAR, CICMS, etc. It includes file layouts, Ansible roles, and step‑by‑step workflows so instructors and trainees can complete the training without confusion. One scenario delivers penetration testing and vulnerability assessment training through a dedicated platform and Cyber Range simulation, while the other models malware simulation and CTI integration. This repository contains materials for deploying and managing security analysis exercises on CyberRangeCZ using this platform.

## Prerequisites

- Active account on [CyberRangeCZ](https://www.cyberrange.cz/) with permissions to deploy cyber range scenarios.
- SSH access to the range and ability to run privileged commands.
- Local tools: `git`, `kubectl`, `helm`, and a modern web browser.
- Recommended familiarity with the CyberRangeCZ interface and the training platform runner used in Subcase 1b.
- The provided startup scripts rely on `systemctl`. If your environment lacks systemd, set `DIRECT_START=1` to attempt starting services with legacy `service` commands or direct scripts.
- Prepare required environment variables such as `LTI_TOOL_PRIVATE_KEY` and `OPENEDX_URL` as described in [docs/env_variables.md](docs/env_variables.md).

## Deployment on CRCZ

See [deployment manual](docs/deployment_manual.md) for detailed steps including VM preparation, service orchestration, teardown, and environment reset.


1. **Clone the Repository**
   ```bash
   git clone https://github.com/example/techanalysissecmanage-crcz.git
   cd techanalysissecmanage-crcz
   ```
2. **Authenticate to CyberRangeCZ** – Ensure VPN or direct connectivity and log into the portal.
3. **Prepare the Scenario** – Upload the penetration testing helper scripts from `subcase_1b/scripts/` to the appropriate CRCZ repositories so they are accessible to the exercise.
4. **Launch the Cyber Range** – Use `subcase_1b/scripts/cyber_range_start.sh` to start the simulated environment for Subcase 1b and provision the trainee workstation.
5. **Start the Training Platform Runner** – Execute `subcase_1b/scripts/training_platform_start.sh` to launch the training platform services used in the penetration testing labs described in [`docs/subcase_1b_guide.md`](docs/subcase_1b_guide.md).

### Phishing Quiz Module

Running `subcase_1b/scripts/training_platform_start.sh` launches a training platform that now includes a phishing-awareness quiz. Set the `PASSWORD` environment variable to a strong value before starting the service. Once the service is up, the following endpoints can be used to interact with the quiz:

- `GET /quiz/start` – obtain questions.
- `POST /quiz/submit` – send answers and record the score.
- `GET /quiz/score` – retrieve stored scores per user and course.

See [`docs/subcase_1b_guide.md`](docs/subcase_1b_guide.md) for detailed examples.

### Tool Launch Endpoint

The training platform also provides a `POST /launch_tool` route to run
predefined **Nmap**, **ZAP**, or **Caldera** operations against the KYPO
subnet. Supply the authentication `token` and desired `tool` in the JSON
body to start a job. The response returns a `job_id` and initial
`status`. Poll `GET /launch_tool/<job_id>?token=...` to obtain the latest
status and command output, allowing the UI to show progress or completion
to the trainee.

### Importing Open edX Content

Sample lessons and a quiz are provided under `open_edx/course`. To load this material into Open edX Studio:

1. Archive the directory:
   ```bash
   zip -r phishing_course.zip open_edx/course
   ```
2. In Studio, open the target course and navigate to **Tools → Import**.
3. Upload `phishing_course.zip` to add the lessons and quiz.

### IRIS Case Closure Automation

The repository includes `scripts/iris_case_closed_poll.py`, a helper that
polls an IRIS case-management instance for cases marked as **closed**. When a
newly closed case is discovered it will:

1. Run `subcase_1b/scripts/collect_artifacts.sh` to gather
   post-incident evidence.
2. Tag the associated MISP event with `lessons learned` via the MISP API.

Configuration is handled through environment variables such as `IRIS_URL`,
`IRIS_API_KEY`, `MISP_URL`, and `MISP_API_KEY`. Execute the script with:

```bash
python scripts/iris_case_closed_poll.py
```

The script keeps track of processed case IDs in `scripts/.iris_processed_cases.json`
to avoid duplicate reports.

## Teardown

1. Stop the scenario from the CRCZ dashboard.
2. Remove any temporary resources or virtual machines associated with the exercise.
3. Archive logs and reports for after-action review.
4. Verify that no residual network configurations remain on CyberRangeCZ.

## Troubleshooting and Tool References

- **Connectivity Issues** – Confirm VPN status and that required ports (e.g., 22 for SSH) are open.
- **Scenario Fails to Start** – Ensure the Subcase 1b helper scripts are uploaded and that the repository path is correct.
- **Training Platform Logs** – Refer to the `subcase_1b/scripts` directory for runner logs and consult [`docs/subcase_1b_guide.md`](docs/subcase_1b_guide.md) for expected service behavior.

Additional theoretical background and workflow guidance can be found in [`docs/training_workflows.md`](docs/training_workflows.md). For day‑to‑day alert handling, analysts should review the [`SOC Analyst Playbook`](docs/soc_analyst_playbook.md).

## Scenario Resources

- [Subcase 1b resources](docs/subcase_1b_guide.md)

## CRCZ/KYPO Training Packaging

After adding or modifying sandbox definitions, you can validate and publish the training module using the `kypo` CLI:

1. **Validate** the training specification:
   ```bash
   kypo training validate training.yaml
   ```
2. **Pack** the training for distribution:
   ```bash
   kypo training pack training.yaml
   ```
3. **Publish** the package to a KYPO portal:
   ```bash
   kypo training publish training.yaml
   ```
   The publish command expects authentication details appropriate for your CRCZ/KYPO instance.

### Sandbox agenda definition

The sandbox agenda is defined in two forms. `sandboxes/sandbox_agenda.yaml`
contains the full sandbox definition (sandbox metadata plus the nested `agenda`).
For the KYPO UI, upload `sandboxes/sandbox_agenda_steps.yaml` in the **Sandbox
Agenda** field, because it starts directly with the agenda list (no wrapper
object or sandbox metadata). If you upload a file with the wrapper structure
instead of the direct list, KYPO raises the error “Expected a SequenceNode
start”, because it expects a YAML sequence as the top-level node. The agenda
steps sequence the topology import, provisioning playbook, and port checks as
explicit list items. The same topology and provisioning files referenced in
`training.yaml` are reused, so validation and packaging work identically while
providing clearer handoff notes for instructors.

> ℹ️ **Required topology**: when creating the topology in KYPO, use the exact name `subcase-1b-topology` (as shown in [`topology.yml`](topology.yml)) and select the file `sandboxes/topology_subcase_1b.yaml`. In the KYPO form, fill in the key fields with these values to avoid introducing variants such as `subcase_to_topology`:
>
> - **Topology name**: `subcase-1b-topology`
> - **Topology YAML**: `sandboxes/topology_subcase_1b.yaml`
> - **Description (optional)**: “Subcase 1b topology for NG‑SOC labs”
>
> This example matches the definition included in this repository and prevents discrepancies during packaging and publication.

#### CLI walkthrough

Use the KYPO CLI (or the equivalent KYPO UI steps) to reproduce the agenda-driven
workflow with the exact repository files. The examples below assume you are
already authenticated in the target KYPO instance.

> ✅ **Validate the agenda after every change**: any time you edit
> `sandboxes/sandbox_agenda.yaml`, run a YAML/sequence validation before
> publishing. For example:
> ```bash
> kypo sandbox validate sandboxes/sandbox_agenda.yaml
> ```
> This ensures the agenda remains a valid top-level sequence and catches syntax
> regressions before upload.

1. **Import the topology** with the expected name and YAML:
   ```bash
   kypo sandbox topology import \
     --name subcase-1b-topology \
     sandboxes/topology_subcase_1b.yaml
   ```
   *UI:* In **Sandboxes → Topologies**, choose **Import topology**, select the
   `sandboxes/topology_subcase_1b.yaml` file, and set the **Name** to
   `subcase-1b-topology`.

2. **Create the sandbox** from the agenda without adding wrapper keys. The YAML
   must start directly with the sequence to avoid `SequenceNode` parse errors:
   ```bash
   kypo sandbox create \
     --topology subcase-1b-topology \
     sandboxes/sandbox_agenda.yaml
   ```
   *UI:* In **Sandboxes → Create sandbox**, select the `subcase-1b-topology`
   topology and upload `sandboxes/sandbox_agenda.yaml` as-is. Do not insert
   extra root fields (for example, `version:` or a wrapper object), because the
   parser requires the top-level sequence.

3. **Verify the provisioning playbook association** so that machines are
   configured automatically during creation:
   ```bash
   kypo sandbox show subcase-1b-topology
   ```
   Confirm the listed provisioning playbook points to the agenda entry that
   references `provisioning/playbooks/ag-soc-base.yml`.

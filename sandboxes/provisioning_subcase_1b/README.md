# Provisioning Subcase 1b Packages

This sandbox directory provides packaging notes and helper scripts, but **does not define its own
provisioning logic**. The single operational provisioning flow uses the canonical root playbook:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

For compatibility, `site.yml` in this folder is only a wrapper (`import_playbook`) that delegates to
`../../provisioning/playbook.yml`.

> Operation rule: this tree is not a second provisioning entrypoint.
> Use for packaging/compatibility only; all functional logic lives in `provisioning/`.

## Scope of this directory (wrapper-only)

- `site.yml` must remain a wrapper (`import_playbook`) without its own provisioning tasks.
- Package catalogs, manual installation recipes or operational defaults should not be added here.
- Real deployment variables and artefacts are defined in `provisioning/group_vars/*.yml` and `provisioning/roles/**`.
- Any functional adjustments should be implemented in `provisioning/` only.

## Note on package documentation

To avoid competing flows or misleading placeholders, this tree does not maintain packet tables or
manual installation instructions. The only valid operational reference for provisioning is
`provisioning/README.md`.


> Los scripts `build_training_platform.sh`, `build_trainee_workstation.sh` y
> `download_offline_artifacts.sh` son utilidades de empaquetado/offline image prep.
> Do not replace the canonical provisioning flow with `provisioning/playbook.yml`.

## Trainee workstation tool versions

The `build_trainee_workstation.sh` script installs pre-downloaded packages for the trainee
workstation. The following versions are bundled and verified using SHA256 hashes:

| Tool | Version | Verification command |
|------|---------|---------------------|
| Nmap | 7.93+dfsg1-1 | `nmap --version` |
| GVM  | 25.04.0 | `gvmd --version` |
| OWASP ZAP | 2.16.1 | `zaproxy -version` |
| Caldera | 5.3.0 | `python3 /opt/caldera/server.py --help` |

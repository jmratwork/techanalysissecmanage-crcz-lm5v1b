# Provisioning Subcase 1b Packages

This sandbox directory provides packaging notes and helper scripts, but **does not define its own
provisioning logic**. The single operational provisioning flow uses the canonical root playbook:

```bash
ansible-playbook -i provisioning/inventory.ini provisioning/playbook.yml
```

For compatibility, `site.yml` in this folder is only a wrapper (`import_playbook`) that delegates to
`../../provisioning/playbook.yml`.

## Package locations

| Component | Deb package URL | Container image |
|-----------|-----------------|-----------------|
| BIPS | https://example.com/apt/pool/bips/bips-agent.deb | registry.example.com/bips:latest |
| NG-SIEM | https://example.com/apt/pool/ng-siem/ng-siem-server.deb | registry.example.com/ng-siem:latest |
| CICMS | https://example.com/apt/pool/cicms/cicms-server.deb | registry.example.com/cicms:latest |
| NG-SOAR | https://example.com/apt/pool/ng-soar/ng-soar-platform.deb | registry.example.com/ng-soar:latest |

## Adding the private APT repository (manual fallback)

Repository setup is handled by canonical provisioning roles/playbooks. If you need to prepare a host
manually for troubleshooting:

```bash
echo 'deb [trusted=yes] https://example.com/apt stable main' | \
  sudo tee /etc/apt/sources.list.d/ngsoc.list
sudo apt-get update
sudo apt-get install bips ng-siem cicms ng-soar
```

## Trainee workstation tool versions

The `build_trainee_workstation.sh` script installs pre-downloaded packages for the trainee
workstation. The following versions are bundled and verified using SHA256 hashes:

| Tool | Version | Verification command |
|------|---------|---------------------|
| Nmap | 7.93+dfsg1-1 | `nmap --version` |
| GVM  | 25.04.0 | `gvmd --version` |
| OWASP ZAP | 2.16.1 | `zaproxy -version` |
| Caldera | 5.3.0 | `python3 /opt/caldera/server.py --help` |

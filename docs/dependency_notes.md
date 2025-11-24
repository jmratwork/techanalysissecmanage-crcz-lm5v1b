# Dependency Notes

This repository replaces disallowed utilities with tools from the approved list.

- `nmap`: Used in `subcase_1b/scripts/trainee_start.sh` to perform port scans. Nmap is an approved scanning utility.
- `docker` and `docker compose`: Required by `subcase_1b/scripts/cyber_range_start.sh` to launch the containerized lab environment. The scripts fall back to direct service startup when `ALLOW_NO_DOCKER` is set.
- `zip`: Used by `subcase_1b/scripts/collect_artifacts.sh` to package logs for after-action review.

No additional network tools are necessary; standard systemd and Bash components remain.

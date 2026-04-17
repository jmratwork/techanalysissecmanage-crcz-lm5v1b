from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOPOLOGY_FILE = REPO_ROOT / "sandboxes" / "topology_subcase_1b.yaml"
INVENTORY_FILE = REPO_ROOT / "provisioning" / "inventory.ini"
PLAYBOOK_FILE = REPO_ROOT / "provisioning" / "playbook.yml"


GROUP_HEADER_RE = re.compile(r"^\[([^\]]+)\]\s*$")
HOST_PLAY_RE = re.compile(r"^-\s*hosts:\s*(\S+)\s*$")
KYPO_NODE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _extract_topology_nodes() -> set[str]:
    """Extract canonical node names from topology_subcase_1b.yaml.

    We intentionally use a tiny indentation-based parser to avoid external
    YAML dependencies in test runtime.
    """

    lines = TOPOLOGY_FILE.read_text(encoding="utf-8").splitlines()
    nodes: set[str] = set()
    invalid_nodes: list[tuple[str, str]] = []

    current_section: str | None = None
    for line in lines:
        if re.match(r"^hosts:\s*$", line):
            current_section = "hosts"
            continue
        if re.match(r"^routers:\s*$", line):
            current_section = "routers"
            continue
        # Any other top-level key ends the active section.
        if re.match(r"^[A-Za-z0-9_]+:\s*$", line):
            current_section = None
            continue

        if current_section in {"hosts", "routers"}:
            match = re.match(r"^\s{2}([A-Za-z0-9_-]+):\s*$", line)
            if match:
                node_name = match.group(1)
                nodes.add(node_name)
                if not KYPO_NODE_NAME_RE.fullmatch(node_name):
                    invalid_nodes.append((current_section, node_name))

    assert not invalid_nodes, (
        "Invalid KYPO host/router name(s) in "
        f"{TOPOLOGY_FILE.relative_to(REPO_ROOT)}. "
        "Names must match ^[a-z0-9]+(?:-[a-z0-9]+)*$ "
        "(no '_', '-' allowed). "
        "Offending entries: "
        + ", ".join(
            f"'{name}' (section: {section})"
            for section, name in sorted(invalid_nodes, key=lambda item: item[1])
        )
    )

    return nodes


def _extract_inventory_groups() -> tuple[set[str], dict[str, list[str]]]:
    lines = INVENTORY_FILE.read_text(encoding="utf-8").splitlines()
    groups: set[str] = set()
    group_members: dict[str, list[str]] = {}
    current_group: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        group_match = GROUP_HEADER_RE.match(line)
        if group_match:
            current_group = group_match.group(1)
            groups.add(current_group)
            group_members.setdefault(current_group, [])
            continue

        if current_group is not None:
            token = line.split()[0]
            group_members[current_group].append(token)

    return groups, group_members


def _extract_play_hosts() -> set[str]:
    hosts: set[str] = set()
    for raw_line in PLAYBOOK_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = HOST_PLAY_RE.match(line)
        if match:
            hosts.add(match.group(1))
    return hosts


def test_topology_nodes_match_canonical_inventory_groups() -> None:
    topology_nodes = _extract_topology_nodes()
    inventory_groups, _ = _extract_inventory_groups()

    canonical_inventory_groups = {
        g for g in inventory_groups if ":" not in g and g != "subcase_1b"
    }

    assert topology_nodes == canonical_inventory_groups


def test_each_canonical_inventory_group_has_a_playbook_host_block() -> None:
    inventory_groups, _ = _extract_inventory_groups()
    play_hosts = _extract_play_hosts()

    canonical_inventory_groups = {
        g for g in inventory_groups if ":" not in g and g != "subcase_1b"
    }

    missing_play_blocks = sorted(canonical_inventory_groups - play_hosts)
    assert not missing_play_blocks, (
        "Missing playbook host blocks for canonical groups: "
        f"{', '.join(missing_play_blocks)}"
    )


def test_subcase_1b_children_contains_only_canonical_groups() -> None:
    topology_nodes = _extract_topology_nodes()
    _, group_members = _extract_inventory_groups()

    children = set(group_members.get("subcase_1b:children", []))
    assert children == topology_nodes


def test_soc_server_not_present_in_canonical_inventory_or_playbook() -> None:
    inventory_groups, _ = _extract_inventory_groups()
    play_hosts = _extract_play_hosts()

    assert "soc_server" not in inventory_groups
    assert "soc_server" not in play_hosts

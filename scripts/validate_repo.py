#!/usr/bin/env python3
"""Validate repository metadata and cross-file references using the stdlib only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "mcu-dev-skill"
SKILLS_DIR = PLUGIN_DIR / "skills"
PLUGIN_MANIFEST = PLUGIN_DIR / ".zcode-plugin" / "plugin.json"
MARKETPLACE = ROOT / "marketplace.json"
README = ROOT / "README.md"
ACCEPTANCE = ROOT / "docs" / "acceptance-examples.md"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_skill_frontmatter(path: Path, errors: list[str]) -> str | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        fail(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter opener")
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        fail(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter closer")
        return None

    frontmatter = lines[1:end]
    names = [m.group(1).strip() for line in frontmatter if (m := re.match(r"^name:\s*(.+?)\s*$", line))]
    if len(names) != 1 or not names[0]:
        fail(errors, f"{path.relative_to(ROOT)}: expected one non-empty name field")
        return None
    if not any(re.match(r"^description:\s*(?:[|>][+-]?(?:\s+#.*)?|(?![|>])\S.*)$", line) for line in frontmatter):
        fail(errors, f"{path.relative_to(ROOT)}: missing description field")
    if names[0] != path.parent.name:
        fail(errors, f"{path.relative_to(ROOT)}: name '{names[0]}' must match directory '{path.parent.name}'")
    return names[0]


def validate_local_markdown_links(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for raw_target in re.findall(r"\[[^\]]*\]\(([^)]*)\)", text):
        target = raw_target.strip()
        if not target:
            fail(errors, f"{path.relative_to(ROOT)}: empty Markdown link destination")
            continue
        target = target.split(maxsplit=1)[0].strip("<>")
        if not target:
            fail(errors, f"{path.relative_to(ROOT)}: empty Markdown link destination")
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
            continue
        local = target.split("#", 1)[0]
        if not local:
            continue
        resolved = (path.parent / local).resolve()
        if not resolved.exists():
            fail(errors, f"{path.relative_to(ROOT)}: broken local link '{target}'")


def main() -> int:
    errors: list[str] = []
    plugin: dict[str, object] = {}
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if not skill_files:
        fail(errors, "no skills found under mcu-dev-skill/skills")

    skill_names = {name for path in skill_files if (name := validate_skill_frontmatter(path, errors))}
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" not in path.parts:
            validate_local_markdown_links(path, errors)

    for path in (PLUGIN_MANIFEST, MARKETPLACE):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"{path.relative_to(ROOT)}: invalid JSON ({exc})")

    try:
        plugin = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
        skills_path = (PLUGIN_DIR / plugin["skills"]).resolve()
        commands_path = (PLUGIN_DIR / plugin["commands"]).resolve()
        if not skills_path.is_dir():
            fail(errors, "plugin manifest skills path does not exist")
        if not commands_path.is_dir():
            fail(errors, "plugin manifest commands path does not exist")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        fail(errors, f"plugin manifest paths cannot be checked ({exc})")

    try:
        catalog = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        entries = catalog.get("plugins", [])
        if len(entries) != 1:
            fail(errors, "marketplace must contain exactly one plugin entry")
        for entry in entries:
            if not (ROOT / entry.get("source", "")).is_dir():
                fail(errors, f"marketplace source does not exist: {entry.get('source')}")
            if entry.get("version") != plugin.get("version"):
                fail(errors, "marketplace and plugin manifest versions differ")
    except (OSError, json.JSONDecodeError, AttributeError, TypeError) as exc:
        fail(errors, f"marketplace entry cannot be checked ({exc})")

    try:
        readme = README.read_text(encoding="utf-8")
        listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", readme, flags=re.MULTILINE))
        if listed != skill_names:
            fail(errors, f"README skill inventory differs (missing={sorted(skill_names - listed)}, stale={sorted(listed - skill_names)})")
    except OSError as exc:
        fail(errors, f"README cannot be checked ({exc})")

    try:
        acceptance = ACCEPTANCE.read_text(encoding="utf-8")
        ids = [int(value) for value in re.findall(r"^## A(\d+)\b", acceptance, flags=re.MULTILINE)]
        if len(ids) != len(set(ids)):
            fail(errors, "acceptance example IDs contain duplicates")
        if ids and sorted(ids) != list(range(1, max(ids) + 1)):
            fail(errors, "acceptance example IDs must be contiguous starting at A1")
    except OSError as exc:
        fail(errors, f"acceptance examples cannot be checked ({exc})")

    known_names = skill_names
    for path in sorted(ROOT.rglob("*.md")):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for reference in re.findall(r"`((?:review-[a-z0-9-]+)|embedded-workflow|board-profile)`", text):
            if reference not in known_names:
                fail(errors, f"{path.relative_to(ROOT)}: unknown skill reference '{reference}'")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"Validation failed: {len(errors)} issue(s).")
        return 1

    print(f"Validation passed: {len(skill_names)} skills, plugin metadata, README inventory, links, and acceptance IDs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
generate_quickstart_sheets.py

Runs all generate_* sheet scripts and writes their output to
/tmp/1kfa_quickstart/.

No arguments. Run from anywhere inside the repo.
"""

import os
import subprocess
import sys

OUTPUT_DIR = "/tmp/1kfa_quickstart"

# Resolve repo root relative to this script's location.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIN = os.path.join(REPO_ROOT, "bin")

SCRIPTS = [
    ("generate_character_html_sheet.py",  "mod_guide_player.md"),
    ("generate_combat_html_sheet.py",     "mod_guide_gm.md"),
    ("generate_hearth_html_sheet.py",     "mod_guide_gm.md"),
    ("generate_scene_html_sheets.py",     "mod_guide_gm.md"),
    ("generate_touchstones_html_sheet.py","mod_guide_table.md"),
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    failures = []

    for script_name, guide_name in SCRIPTS:
        script = os.path.join(BIN, script_name)
        guide  = os.path.join(REPO_ROOT, guide_name)

        if not os.path.exists(script):
            print(f"MISSING  {script_name}")
            failures.append(script_name)
            continue

        if not os.path.exists(guide):
            print(f"MISSING  {guide_name}  (needed by {script_name})")
            failures.append(script_name)
            continue

        result = subprocess.run(
            [sys.executable, script, guide, "--output-dir", OUTPUT_DIR],
            capture_output=True,
            text=True,
        )

        for line in result.stdout.splitlines():
            print(f"  {line}")

        if result.returncode != 0:
            print(f"FAILED   {script_name}")
            if result.stderr:
                print(result.stderr.rstrip())
            failures.append(script_name)

    print()
    sheets = sorted(f for f in os.listdir(OUTPUT_DIR) if f.endswith(".html"))
    print(f"{len(sheets)} sheets in {OUTPUT_DIR}:")
    for s in sheets:
        print(f"  {s}")

    if failures:
        print(f"\n{len(failures)} script(s) failed: {', '.join(failures)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

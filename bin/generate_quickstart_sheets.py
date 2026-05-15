#!/usr/bin/env python3
"""
generate_quickstart_sheets.py

Runs all generate_* sheet scripts and writes their output to
/tmp/1kfa_quickstart/.

Usage:
    python3 generate_quickstart_sheets.py [--export-pdf [OUTPUT.pdf]]

With --export-pdf, passes the flag to each subscript and then runs pdfunite
to join all PDFs into a single file (default: 1kfa_quickstart_sheets.pdf in
OUTPUT_DIR).
"""

import argparse
import os
import subprocess
import sys

OUTPUT_DIR = "/tmp/1kfa_quickstart"
DEFAULT_PDF = "1kfa_quickstart_sheets.pdf"

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
    parser = argparse.ArgumentParser(
        description="Generate all 1kFA quickstart sheets."
    )
    parser.add_argument(
        "--export-pdf", action="store_true",
        help="Render each sheet to PDF and unite them into a single file",
    )
    parser.add_argument(
        "--pdf-output", default=os.path.join(OUTPUT_DIR, DEFAULT_PDF),
        metavar="FILE",
        help=f"Destination for the united PDF (default: {DEFAULT_PDF} in output dir)",
    )
    args = parser.parse_args()

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

        cmd = [sys.executable, script, guide, "--output-dir", OUTPUT_DIR]
        if args.export_pdf:
            cmd.append("--export-pdf")

        result = subprocess.run(cmd, capture_output=True, text=True)

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
        raise Exception('failed')

    if args.export_pdf:
        # Explicit order for the united PDF — edit this list to reorder.
        PDF_ORDER = [
            os.path.join(OUTPUT_DIR, f) for f in [
                "sheet_table_guide_universe_creation.pdf",
                "sheet_player_guide_character_creation.pdf",
                "sheet_gm_guide_hearth.pdf",
                "sheet_oneshot_ch1.pdf",
                "sheet_oneshot_ch2.pdf",
                "sheet_oneshot_ch3.pdf",
                "sheet_oneshot_ch4.pdf",
                "sheet_9hr_ch1.pdf",
                "sheet_9hr_ch2.pdf",
                "sheet_9hr_ch3.pdf",
                "sheet_9hr_ch4.pdf",
                "sheet_9hr_ch5.pdf",
                "sheet_9hr_ch6.pdf",
                "sheet_9hr_ch7.pdf",
                "sheet_9hr_ch8.pdf",
                "sheet_combat_interlude.pdf",
            ]
        ]
        pdf_paths = [p for p in PDF_ORDER if os.path.exists(p)]
        if not pdf_paths:
            print("\nERROR: --export-pdf set but no PDFs found in output dir.")
            sys.exit(1)

        out_pdf = args.pdf_output
        print(f"\nUniting {len(pdf_paths)} PDFs → {out_pdf}")
        result = subprocess.run(
            ["pdfunite"] + pdf_paths + [out_pdf],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"FAILED   pdfunite")
            if result.stderr:
                print(result.stderr.rstrip())
            sys.exit(1)
        print(f"  done  ({os.path.getsize(out_pdf):,} bytes)")


if __name__ == "__main__":
    main()

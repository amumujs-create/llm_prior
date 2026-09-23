#!/usr/bin/env python3
"""R1 wrapper for the integrity-corrected E15-D v1.2 confirmatory corpus."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import run_e15d_confirmatory_v1_2 as base


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "experiments" / "E15D_CONFIRMATORY_MANIFEST_V1_2_R1.json"
DEFAULT_ROWS = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_CONFIRMATORY_ROWS_V1_2_R1.csv"
DEFAULT_INTEGRITY = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_CONFIRMATORY_INTEGRITY_V1_2_R1.json"
DEFAULT_SANITY = ROOT / "results" / "prior_utilization_e15d" / "confirmatory_v1_2_r1" / "E15D_CONFIRMATORY_SANITY_V1_2_R1.json"


def write_rows_lf(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["task_id", "prefix_exposure", "policy", "e_kappa", "e_lambda", "nrmse_clean_far"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--sanity", action="store_true")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--integrity", type=Path, default=DEFAULT_INTEGRITY)
    parser.add_argument("--sanity-out", type=Path, default=DEFAULT_SANITY)
    args = parser.parse_args()
    if args.sanity == args.run:
        parser.error("specify exactly one of --sanity or --run")
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "FROZEN":
        raise SystemExit("confirmatory run requires a frozen manifest")
    if args.sanity:
        result = base.sanity(manifest)
        args.sanity_out.parent.mkdir(parents=True, exist_ok=True)
        args.sanity_out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if result["final_status"] != "PASS":
            raise SystemExit("confirmatory R1 sanity failed")
        return
    rows: list[dict[str, Any]] = []
    audits: list[dict[str, bool]] = []
    for task_id in range(int(manifest["task_count"])):
        task_records, task_audits = base.task_rows(manifest, task_id)
        rows.extend(task_records)
        audits.append(task_audits)
    write_rows_lf(rows, args.rows)
    result = base.integrity(rows, manifest, audits, args.manifest, args.rows)
    result["integrity_correction"] = "R1_fresh_namespace_and_LF_writer"
    args.integrity.parent.mkdir(parents=True, exist_ok=True)
    args.integrity.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["final_status"] != "PASS":
        raise SystemExit("confirmatory R1 integrity failed")


if __name__ == "__main__":
    main()

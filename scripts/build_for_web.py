#!/usr/bin/env python3
"""Build full web dashboard bundle for Vercel/GitHub Pages static hosting."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], allow_fail: bool = False) -> None:
    print("$", " ".join(cmd))
    res = subprocess.run(cmd, cwd=ROOT)
    if res.returncode != 0 and not allow_fail:
        raise SystemExit(res.returncode)


def main() -> None:
    run(["python3", "scripts/build_live_cex_candidates.py"], allow_fail=True)
    run(["python3", "scripts/build_network_friction.py"], allow_fail=True)
    run(["python3", "scripts/build_live_cex_dex_candidates.py"], allow_fail=True)
    run(["python3", "scripts/build_live_funding_candidates.py"], allow_fail=True)
    run(["python3", "scripts/build_live_basis_candidates.py"], allow_fail=True)

    run(
        [
            "python3",
            "scripts/merge_candidate_files.py",
            "--inputs",
            "data/opportunity_candidates.live.json",
            "data/opportunity_candidates.cex_dex.live.json",
            "data/opportunity_candidates.funding.live.json",
            "data/opportunity_candidates.basis.live.json",
            "--output",
            "data/opportunity_candidates.combined.live.json",
        ]
    )

    merged = ROOT / "data/opportunity_candidates.combined.live.json"
    constraints = ROOT / "data/execution_constraints.latest.json"
    fee_table = ROOT / "data/execution_fee_table.latest.json"
    sample = ROOT / "data/opportunity_candidates.sample.json"

    try:
        payload = json.loads(merged.read_text()) if merged.exists() else []
    except Exception:
        payload = []

    if not isinstance(payload, list) or len(payload) == 0:
        merged.write_text(sample.read_text())
        print("Fallback applied: using sample candidates")
    else:
        print(f"Merged candidates: {len(payload)}")

    run(
        [
            "python3",
            "scripts/build_execution_constraints_template.py",
            "--input",
            "data/opportunity_candidates.combined.live.json",
            "--output",
            "data/execution_constraints.latest.json",
        ]
    )
    run(
        [
            "python3",
            "scripts/build_authenticated_constraints.py",
            "--constraints",
            "data/execution_constraints.latest.json",
            "--quotes",
            "data/normalized_quotes_cex_latest.json",
        ],
        allow_fail=True,
    )
    run(
        [
            "python3",
            "scripts/build_execution_fee_table_template.py",
            "--input",
            "data/opportunity_candidates.combined.live.json",
            "--output",
            "data/execution_fee_table.latest.json",
        ]
    )
    run(
        [
            "python3",
            "scripts/build_authenticated_fee_table.py",
            "--input-candidates",
            "data/opportunity_candidates.combined.live.json",
            "--fee-table",
            "data/execution_fee_table.latest.json",
        ],
        allow_fail=True,
    )

    if constraints.exists():
        print(f"Execution constraints: {constraints}")
    if fee_table.exists():
        print(f"Execution fee table: {fee_table}")

    run(
        [
            "python3",
            "scripts/scan_opportunities.py",
            "--input",
            "data/opportunity_candidates.combined.live.json",
            "--constraints",
            "data/execution_constraints.latest.json",
            "--fee-table",
            "data/execution_fee_table.latest.json",
            "--execution-profile",
            "taker_default",
            "--output-json",
            "opportunities/shortlist-latest.json",
            "--output-md",
            "opportunities/dashboard-latest.md",
        ]
    )

    run(
        [
            "python3",
            "scripts/build_pages_site.py",
            "--shortlist",
            "opportunities/shortlist-latest.json",
            "--dashboard",
            "opportunities/dashboard-latest.md",
            "--out-dir",
            "site",
        ]
    )


if __name__ == "__main__":
    main()

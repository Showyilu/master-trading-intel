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
    run(["python3", "scripts/build_live_cex_dex_candidates.py"], allow_fail=True)

    run(
        [
            "python3",
            "scripts/merge_candidate_files.py",
            "--inputs",
            "data/opportunity_candidates.live.json",
            "data/opportunity_candidates.cex_dex.live.json",
            "--output",
            "data/opportunity_candidates.combined.live.json",
        ]
    )

    merged = ROOT / "data/opportunity_candidates.combined.live.json"
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
            "scripts/scan_opportunities.py",
            "--input",
            "data/opportunity_candidates.combined.live.json",
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

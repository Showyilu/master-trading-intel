#!/usr/bin/env python3
"""Merge multiple candidate JSON arrays into one file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Merge candidate JSON array files.")
    p.add_argument("--inputs", nargs="+", type=Path, required=True, help="Input JSON files (array)")
    p.add_argument("--output", type=Path, required=True, help="Merged output JSON file")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    merged = []

    for path in args.inputs:
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        if isinstance(payload, list):
            merged.extend(payload)

    merged_sorted = sorted(merged, key=lambda x: x.get("gross_edge_bps", 0), reverse=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(merged_sorted, indent=2))

    print(f"Merged files: {len(args.inputs)}")
    print(f"Total candidates: {len(merged_sorted)}")
    print(f"Wrote: {args.output}")


if __name__ == "__main__":
    main()

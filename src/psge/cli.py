"""PSGE CLI."""

import argparse
from pathlib import Path

from psge.pipeline.runner import run, run_panel
from psge.utils.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(prog="psge", description="PSGE - PPOX mechanistic variant analysis")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run pipeline for variant(s)")
    run_parser.add_argument("--variant", type=str, help="Variant string (e.g. R59W)")
    run_parser.add_argument("--panel", type=Path, help="Panel YAML path (M2)")
    run_parser.add_argument("--config", type=Path, help="Config YAML path")
    run_parser.add_argument("--results-dir", type=str, help="Override results directory")
    run_parser.add_argument("--structure-source", type=str, choices=["pdb_first", "predict_first"],
        help="Structure source: pdb_first (3NKS for PPOX) or predict_first (ESMFold/mock)")

    args = parser.parse_args()

    if args.command == "run":
        overrides = {}
        if getattr(args, "results_dir", None):
            overrides["results_dir"] = args.results_dir
        if getattr(args, "structure_source", None):
            overrides["structure_source"] = args.structure_source
        config = load_config(
            getattr(args, "config", None),
            overrides,
        )
        if args.variant:
            run(args.variant, config)
            print(f"Wrote {config.results_dir}/summary.json, report.md")
        elif args.panel:
            run_panel(args.panel, config)
        else:
            run_parser.error("Either --variant or --panel required")


if __name__ == "__main__":
    main()

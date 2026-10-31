#!/usr/bin/env python3
"""Entry point script for running integrity checks."""

import argparse
import sys
from pathlib import Path
from checker.pipeline import pipeline_check
from checker.report import print_report


def main():
    parser = argparse.ArgumentParser(
        description="Run integrity checks on Python packages from PyPI."
    )
    parser.add_argument("package", help="Package name to check")
    parser.add_argument("version", help="Package version to check")
    parser.add_argument(
        "--workdir",
        type=Path,
        default=Path("checker_workdir"),
        help="Working directory for check outputs",
    )

    args = parser.parse_args()

    # Run the pipeline
    results = pipeline_check(args.package, args.version, args.workdir)

    # Print the report
    print_report(results, args.package, args.version)

    # Exit with appropriate code
    return 0 if results.get("risk_level") != "HIGH" else 1


if __name__ == "__main__":
    sys.exit(main())

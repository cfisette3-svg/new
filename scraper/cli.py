from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .core import Config, crawl, write


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scraper",
        description="Run a scraper from a YAML config and write CSV/JSON output.",
    )
    parser.add_argument("config", type=Path, help="path to YAML config")
    parser.add_argument("--out", type=Path, help="override output path")
    parser.add_argument("--format", choices=["csv", "json"], help="override output format")
    parser.add_argument("-v", "--verbose", action="store_true", help="log each request")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    cfg = Config.from_yaml(args.config)
    if args.out:
        cfg.output_path = str(args.out)
    if args.format:
        cfg.output_format = args.format

    n = write(crawl(cfg), cfg)
    print(f"wrote {n} records to {cfg.output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

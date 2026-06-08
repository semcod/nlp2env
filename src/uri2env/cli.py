"""CLI for env:// materialization."""

from __future__ import annotations

import argparse
import json
import sys

from uri2env.materialize import materialize_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Materialize env:// URI to .env")
    sub = parser.add_subparsers(dest="cmd", required=True)

    mat = sub.add_parser("materialize", help="Write env keys from env:// URI")
    mat.add_argument("--uri", required=True, help="env:// URI")
    mat.add_argument("--dest", default="", help="Override destination .env path")

    args = parser.parse_args(argv)
    if args.cmd == "materialize":
        result = materialize_uri(args.uri, dest=args.dest or None)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

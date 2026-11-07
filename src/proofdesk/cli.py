"""Command line interface for proofdesk."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .register import STATUSES, Register

DEFAULT_FILE = "proofdesk.json"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="proofdesk",
        description="Keep every claim in your video tied to a source, a date and a screenshot.",
    )
    p.add_argument("--file", "-f", default=DEFAULT_FILE, help=f"register file (default: {DEFAULT_FILE})")
    p.add_argument("--version", action="version", version=f"proofdesk {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add a claim")
    add.add_argument("text")
    add.add_argument("--url", default="")
    add.add_argument("--date", default="", help="date of the source (YYYY-MM-DD)")
    add.add_argument("--screenshot", default="")
    add.add_argument("--note", default="")

    sub.add_parser("list", help="list all claims")

    st = sub.add_parser("status", help="change the status of a claim")
    st.add_argument("id", type=int)
    st.add_argument("status", choices=STATUSES)

    rm = sub.add_parser("remove", help="delete a claim")
    rm.add_argument("id", type=int)

    sub.add_parser("check", help="validate the register (exit code 1 if weak claims are marked verified)")
    sub.add_parser("summary", help="count claims by status")

    ex = sub.add_parser("export", help="export the register")
    ex.add_argument("format", choices=["markdown", "csv"])
    ex.add_argument("--out", help="write to a file instead of stdout")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.file)
    reg = Register.load(path)

    try:
        if args.command == "add":
            claim = reg.add(args.text, args.url, args.date, args.screenshot, args.note)
            reg.save(path)
            print(f"added claim #{claim.id} (unverified)")
        elif args.command == "list":
            if not reg.claims:
                print("no claims yet")
            for c in reg.claims:
                print(f"#{c.id} [{c.status}] {c.text}")
        elif args.command == "status":
            claim = reg.set_status(args.id, args.status)
            reg.save(path)
            print(f"claim #{claim.id} is now {claim.status}")
        elif args.command == "remove":
            reg.remove(args.id)
            reg.save(path)
            print(f"removed claim #{args.id}")
        elif args.command == "summary":
            for status, n in reg.summary().items():
                print(f"{status:>10}: {n}")
        elif args.command == "check":
            issues = reg.validate()
            for issue in issues:
                print(issue)
            if issues:
                return 1
            print("ok: every verified claim has a source, a date and a screenshot")
        elif args.command == "export":
            out = reg.to_markdown() if args.format == "markdown" else reg.to_csv()
            if args.out:
                Path(args.out).write_text(out, encoding="utf-8")
                print(f"wrote {args.out}")
            else:
                sys.stdout.write(out)
    except (KeyError, ValueError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

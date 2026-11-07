"""Core data model: a register of claims, each tied to evidence and a status."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional

# Ordered from weakest to strongest evidence.
STATUSES = ("unverified", "reported", "verified", "false")


@dataclass
class Claim:
    id: int
    text: str
    source_url: str = ""
    source_date: str = ""
    screenshot: str = ""
    status: str = "unverified"
    note: str = ""
    added: str = field(default_factory=lambda: date.today().isoformat())


@dataclass
class ValidationIssue:
    claim_id: int
    message: str

    def __str__(self) -> str:
        return f"claim #{self.claim_id}: {self.message}"


class Register:
    """A list of claims that can be saved, validated and exported."""

    def __init__(self, claims: Optional[Iterable[Claim]] = None) -> None:
        self.claims: List[Claim] = list(claims or [])

    # -- editing ---------------------------------------------------------
    def add(self, text: str, source_url: str = "", source_date: str = "",
            screenshot: str = "", note: str = "") -> Claim:
        text = text.strip()
        if not text:
            raise ValueError("claim text must not be empty")
        claim = Claim(
            id=self._next_id(), text=text, source_url=source_url.strip(),
            source_date=source_date.strip(), screenshot=screenshot.strip(),
            note=note.strip(),
        )
        self.claims.append(claim)
        return claim

    def get(self, claim_id: int) -> Claim:
        for claim in self.claims:
            if claim.id == claim_id:
                return claim
        raise KeyError(f"no claim with id {claim_id}")

    def set_status(self, claim_id: int, status: str) -> Claim:
        if status not in STATUSES:
            raise ValueError(f"status must be one of {', '.join(STATUSES)}")
        claim = self.get(claim_id)
        claim.status = status
        return claim

    def remove(self, claim_id: int) -> None:
        self.claims.remove(self.get(claim_id))

    def _next_id(self) -> int:
        return max((c.id for c in self.claims), default=0) + 1

    # -- validation ------------------------------------------------------
    def validate(self) -> List[ValidationIssue]:
        """Rules that stop a weak claim from being presented as proven."""
        issues: List[ValidationIssue] = []
        for c in self.claims:
            if c.status not in STATUSES:
                issues.append(ValidationIssue(c.id, f"unknown status '{c.status}'"))
                continue
            if c.status == "verified":
                if not c.source_url:
                    issues.append(ValidationIssue(c.id, "verified claims need a source URL"))
                if not c.source_date:
                    issues.append(ValidationIssue(c.id, "verified claims need a source date"))
                if not c.screenshot:
                    issues.append(ValidationIssue(c.id, "verified claims need a screenshot path"))
            if c.status == "reported" and not c.source_url:
                issues.append(ValidationIssue(c.id, "reported claims need at least one source URL"))
        return issues

    def summary(self) -> dict:
        counts = {s: 0 for s in STATUSES}
        for c in self.claims:
            counts[c.status] = counts.get(c.status, 0) + 1
        return counts

    # -- persistence -----------------------------------------------------
    def to_json(self) -> str:
        return json.dumps([asdict(c) for c in self.claims], indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, text: str) -> "Register":
        data = json.loads(text) if text.strip() else []
        return cls(Claim(**item) for item in data)

    def save(self, path: Path) -> None:
        Path(path).write_text(self.to_json() + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Register":
        p = Path(path)
        return cls.from_json(p.read_text(encoding="utf-8")) if p.exists() else cls()

    # -- export ----------------------------------------------------------
    def to_markdown(self) -> str:
        rows = ["| # | Claim | Status | Source | Date | Screenshot |",
                "|---|-------|--------|--------|------|------------|"]
        for c in self.claims:
            text = c.text.replace("|", "\\|")
            rows.append(f"| {c.id} | {text} | {c.status} | {c.source_url or '-'} "
                        f"| {c.source_date or '-'} | {c.screenshot or '-'} |")
        return "\n".join(rows) + "\n"

    def to_csv(self) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "claim", "status", "source_url", "source_date", "screenshot", "note", "added"])
        for c in self.claims:
            writer.writerow([c.id, c.text, c.status, c.source_url, c.source_date,
                             c.screenshot, c.note, c.added])
        return buf.getvalue()

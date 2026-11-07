# proofdesk

A small command-line **claim-to-proof register** for creators who fact-check viral claims before they publish.

Every claim you make in a video should be tied to a source, a date and a screenshot. `proofdesk` keeps that list, refuses to let a weak claim pass as "verified", and exports it as Markdown or CSV for your edit notes.

## Why

"Free and unlimited" claims go viral faster than anyone checks them. Writing down *where* each claim comes from, *when* it was checked, and *what you saw* is the difference between a fact-check and another rumour. This tool makes that habit cheap.

## Install

```bash
pip install -e .
```

Requires Python 3.9+. No third-party dependencies.

## Use

```bash
proofdesk add "ChatGPT Pro is free for 6 months" \
    --url https://openai.com/form/codex-for-oss/ --date 2026-11-07 --screenshot shots/form.png
proofdesk status 1 verified
proofdesk add "Two prompts unlock Pro for free"
proofdesk status 2 false
proofdesk list
proofdesk check          # exit code 1 if a "verified" claim lacks source, date or screenshot
proofdesk summary
proofdesk export markdown --out claims.md
```

Statuses: `unverified`, `reported` (someone credible says so, you have not confirmed it), `verified` (you checked it and have proof), `false`.

The register is stored in `proofdesk.json` in the current folder (change it with `--file`).

## Rules the tool enforces

- `verified` needs a source URL, a source date and a screenshot path.
- `reported` needs at least a source URL.
- Claims are never deleted by a status change, so rejected rumours stay on the record.

## Develop

```bash
python -m unittest discover -s tests -v
```

## License

MIT

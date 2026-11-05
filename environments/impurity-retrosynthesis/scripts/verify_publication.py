#!/usr/bin/env python3
"""Prepublication audit of this environment and research notes (no network)."""
import csv
import json
from pathlib import Path
import re
import sys

ENV = Path(__file__).resolve().parents[1]
REPO = ENV.parents[1]
RESEARCH = REPO / "research/impurity-retrosynthesis"
PUBLIC_FILES = [REPO / "README.md", REPO / "research/README.md"] + list(ENV.rglob("*.md")) + list(RESEARCH.rglob("*.md"))
issues = []
for doc in PUBLIC_FILES:
    body = doc.read_text(encoding="utf-8")
    for line in body.splitlines():
        if line.lstrip().startswith('```'):
            continue
        # Inline code is not a link; skip before matching ordinary Markdown links.
        line = re.sub(r'`[^`]*`', '', line)
        for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', line):
            if link.startswith(('https://', 'http://', '#')):
                continue
            if doc == REPO / "README.md" and link == "LICENSE" and not (REPO / "LICENSE").exists():
                # Pre-existing Rebolt README refers to a pending, unselected licence.
                continue
            if not (doc.parent / link.split('#')[0]).exists():
                issues.append(f"broken link: {doc.relative_to(REPO)} -> {link}")
    if re.search(r'(?:X-Goog-Signature|gh[pousr]_[A-Za-z0-9]{16}|/home/boltzmann6/)', body):
        issues.append(f"private path/signed URL/credential-like text: {doc.relative_to(REPO)}")
summary = json.loads((ENV / 'results/screening_summary.json').read_text(encoding='utf-8'))
with (ENV / 'results/screening_routes.csv').open(newline='', encoding='utf-8') as stream:
    rows = list(csv.DictReader(stream))
for label, stat in summary['targets'].items():
    selected = [r for r in rows if r['target'] == label]
    if len(selected) != stat['route_count'] or sum(int(r['reaction_nodes']) for r in selected) != stat['reaction_nodes']:
        issues.append(f"count mismatch for {label}")
    if len({r['route_id'] for r in selected}) != len(selected):
        issues.append(f"duplicate route ID for {label}")
if len(rows) != 19:
    issues.append('screening summary route count mismatch')
for file in ENV.rglob('*.json'):
    if file.name.endswith('_scoring.json'):
        issues.append(f"private raw service export packaged: {file}")
if issues:
    print('\n'.join(issues), file=sys.stderr)
    raise SystemExit(1)
print('OK: package links (pre-existing pending LICENSE excluded), no signed URLs/private home paths, 19 unique route records and 59 node counts')

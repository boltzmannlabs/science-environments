#!/usr/bin/env python3
"""Check contribution files, local documentation links and recorded source hashes."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = ROOT.parents[1]
RESEARCH = REPOSITORY / "research" / ROOT.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    scopes = [ROOT.relative_to(REPOSITORY).as_posix(), RESEARCH.relative_to(REPOSITORY).as_posix(),
              "README.md", "research/README.md"]
    raw = subprocess.check_output(["git", "-C", str(REPOSITORY), "ls-files", "--cached", "--others",
                                   "--exclude-standard", "-z", "--", *scopes])
    files = sorted({REPOSITORY / name.decode() for name in raw.split(b"\0") if name})
    errors = []
    local_links = python_files = json_files = 0
    disallowed = {".sqlite", ".db", ".pt", ".pth", ".ckpt", ".zip", ".pdb", ".cif", ".csv", ".pdf", ".docx"}
    credential = re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")
    for path in files:
        name = path.relative_to(REPOSITORY).as_posix()
        if path.is_symlink() or path.stat().st_size > 1024 * 1024 or path.suffix in disallowed:
            errors.append(name + ": unexpected release artifact")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            errors.append(name + ": non-text contribution")
            continue
        if credential.search(text) or re.search(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s+[A-Za-z0-9+/]{24,}", text):
            errors.append(name + ": credential-like material")
        if re.search(r"/home/[A-Za-z0-9_.-]+/", text):
            errors.append(name + ": development-server path")
        if path.suffix == ".py":
            ast.parse(text, filename=name)
            python_files += 1
        elif path.suffix == ".json":
            json.loads(text)
            json_files += 1
        elif path.suffix == ".md":
            for target in re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", text):
                if target.startswith("#") or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
                    continue
                destination = (path.parent / target.split("#", 1)[0]).resolve()
                local_links += 1
                if not destination.exists():
                    errors.append(name + ": missing local link " + target)
    manifest = json.loads((ROOT / "SOURCE_PROVENANCE.json").read_text())
    for relative, record in manifest["files"].items():
        path = ROOT / relative
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            errors.append(relative + ": source snapshot hash mismatch")
    report = {"success": not errors, "contribution_files_checked": len(files), "python_files_parsed": python_files,
              "json_files_parsed": json_files, "local_documentation_links_checked": local_links,
              "source_snapshot_files_checked": len(manifest["files"]), "errors": errors,
              "scope": "Contribution file and packaging checks; not a complete security audit or scientific evaluation"}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

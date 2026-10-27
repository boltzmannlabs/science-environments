"""Bounded artifact inspection and conservative scientific handoff metadata."""

import csv
import gzip
import io
import json
import math
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

from .common import WorkflowError, file_hash, validate_data

MAX_FILE = 50 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
MAX_MEMBERS = 10000
QUALITY_METRICS = ["clashscore", "ramachandran_outlier_percent", "ramachandran_favored_percent",
                   "rotamer_outlier_percent", "cbeta_outliers", "cablam_outlier_percent",
                   "cablam_disfavored_percent", "bond_outliers", "angle_outliers",
                   "cis_nonproline", "twisted_peptides"]
STANDARD = set("ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split())
ONE_LETTER = dict(zip("ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(), "ARNDCQEGHILKMFPSTWYV"))
SIDECHAINS = dict(zip(
    "ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL".split(),
    ["CB", "CB CG CD NE CZ NH1 NH2", "CB CG OD1 ND2", "CB CG OD1 OD2", "CB SG",
     "CB CG CD OE1 NE2", "CB CG CD OE1 OE2", "", "CB CG ND1 CD2 CE1 NE2",
     "CB CG1 CG2 CD1", "CB CG CD1 CD2", "CB CG CD CE NZ", "CB CG SD CE", "CB CG CD1 CD2 CE1 CE2 CZ",
     "CB CG CD", "CB OG", "CB OG1 CG2", "CB CG CD1 CD2 NE1 CE2 CE3 CZ2 CZ3 CH2",
     "CB CG CD1 CD2 CE1 CE2 CZ OH", "CB CG1 CG2"]))


def _decompress(name, data):
    if name.lower().endswith(".gz"):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
                result = stream.read(MAX_FILE + 1)
        except (OSError, EOFError) as exc:
            raise WorkflowError("Invalid compressed structure") from exc
        if len(result) > MAX_FILE:
            raise WorkflowError("Decompressed file exceeds 50 MiB")
        return name[:-3], result
    return name, data


def read_members(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size == 0:
        raise WorkflowError("Artifact must be a nonempty regular file, not a symbolic link")
    if path.stat().st_size > MAX_TOTAL:
        raise WorkflowError("Artifact exceeds 512 MiB")
    if path.suffix.lower() != ".zip":
        if path.stat().st_size > MAX_FILE:
            raise WorkflowError("Individual artifact exceeds 50 MiB")
        name, content = _decompress(path.name, path.read_bytes())
        return {name: content}
    members, total = {}, 0
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not 1 <= len(infos) <= MAX_MEMBERS:
                raise WorkflowError("ZIP must contain 1–10000 members")
            for item in infos:
                name = item.filename
                parts = PurePosixPath(name)
                mode = item.external_attr >> 16
                if (parts.is_absolute() or ".." in parts.parts or "\\" in name or ":" in name
                        or not parts.parts or "\x00" in name or stat.S_ISLNK(mode)
                        or item.flag_bits & 1):
                    raise WorkflowError("Unsafe or encrypted ZIP member")
                if item.is_dir():
                    continue
                total += item.file_size
                if (item.file_size > MAX_FILE or total > MAX_TOTAL
                        or item.file_size / max(item.compress_size, 1) > 300):
                    raise WorkflowError("ZIP exceeds safety/decompression limits")
                key, content = _decompress(name, archive.read(item))
                if key in members:
                    raise WorkflowError("Duplicate ZIP member or compressed-name collision")
                members[key] = content
                total += len(content) - item.file_size
                if total > MAX_TOTAL:
                    raise WorkflowError("ZIP decompressed content exceeds 512 MiB")
    except (zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise WorkflowError("Unreadable ZIP archive") from exc
    if not members:
        raise WorkflowError("Empty ZIP archive")
    return members


def csv_rows(content, required=()):
    if len(content) > MAX_FILE:
        raise WorkflowError("CSV exceeds 50 MiB")
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), strict=True)
        fields = reader.fieldnames
        if not fields or len(fields) != len(set(fields)) or not set(required) <= set(fields):
            raise WorkflowError(f"CSV needs unique headers including {list(required)}")
        rows = []
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise WorkflowError("CSV contains a malformed row")
            if not any(value.strip() for value in row.values()):
                raise WorkflowError("CSV contains an empty row")
            rows.append(row)
            if len(rows) > 100000:
                raise WorkflowError("CSV exceeds 100000 rows")
    except (UnicodeError, csv.Error) as exc:
        raise WorkflowError("CSV must be valid UTF-8 comma-separated data") from exc
    if not rows:
        raise WorkflowError("CSV contains no data rows")
    return rows


def fasta_rows(content):
    rows, label, sequence = [], None, []
    try:
        lines = content.decode("utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise WorkflowError("Invalid FASTA encoding") from exc
    for line in [*lines, ">__end__"]:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if label is not None:
                rows.append({"label": label, "sequence": "".join(sequence)})
            label, sequence = line[1:].strip(), []
        else:
            if label is None:
                raise WorkflowError("FASTA sequence appears before header")
            sequence.append(line)
    if not rows:
        raise WorkflowError("FASTA has no sequences")
    for row in rows:
        validate_sequence(row["sequence"])
    if len({r["label"] for r in rows}) != len(rows):
        raise WorkflowError("Duplicate FASTA labels")
    return rows


def validate_sequence(sequence):
    if not sequence or any(c not in "ACDEFGHIKLMNPQRSTVWY:" for c in sequence) or any(not c for c in sequence.split(":")):
        raise WorkflowError("Sequence must contain nonempty chains of standard uppercase amino acids")


def cif_tokens(text):
    """CIF quoting differs from shell quoting (unquoted O5' is legal)."""
    lines = iter(text.splitlines())
    for line in lines:
        if line.startswith(";"):
            block = [line[1:]]
            for continuation in lines:
                if continuation.startswith(";"):
                    break
                block.append(continuation)
            else:
                raise WorkflowError("Unterminated mmCIF multiline value")
            yield "\n".join(block), True
            continue
        i = 0
        while i < len(line):
            if line[i].isspace():
                i += 1; continue
            if line[i] == "#":
                break
            quoted = line[i] in {"'", '"'}
            if quoted:
                quote = line[i]
                i += 1
                start = i
                while i < len(line) and not (line[i] == quote and (i + 1 == len(line) or line[i+1].isspace())):
                    i += 1
                if i == len(line):
                    raise WorkflowError("Unterminated mmCIF quoted value")
                yield line[start:i], True
                i += 1
            else:
                start = i
                while i < len(line) and not line[i].isspace():
                    i += 1
                yield line[start:i], False


def inspect_structure(name, content):
    try:
        text = content.decode("utf-8")
        atoms = []
        if name.lower().endswith(".pdb"):
            models = [line for line in text.splitlines() if line.startswith("MODEL ")]
            if len(models) > 1:
                raise WorkflowError("Multi-model structures need explicit model separation")
            for line in text.splitlines():
                if line.startswith(("ATOM  ", "HETATM")):
                    if line[16:17] not in {" ", ""}:
                        raise WorkflowError("Resolve alternate atom locations before workflow handoff")
                    atoms.append((line.startswith("ATOM"), line[21:22], line[22:27].strip(),
                                  line[17:20].strip(), line[12:16].strip(),
                                  [float(line[i:i+8]) for i in (30, 38, 46)]))
        else:
            # mmCIF atom_site table with quoted values, auth labels preferred.
            lexed = list(cif_tokens(text))
            tokens = [value for value, quoted in lexed]
            models = set()
            i = 0
            while i < len(tokens):
                if lexed[i][1] or tokens[i] != "loop_":
                    i += 1
                    continue
                i += 1
                fields = []
                while i < len(tokens) and not lexed[i][1] and tokens[i].startswith("_"):
                    fields.append(tokens[i]); i += 1
                values = []
                while i < len(tokens) and (lexed[i][1] or (not tokens[i].startswith(("_", "data_", "save_")) and tokens[i] not in {"loop_", "stop_"})):
                    values.append(tokens[i]); i += 1
                if not fields or not fields[0].startswith("_atom_site."):
                    continue
                if len(values) % len(fields):
                    raise WorkflowError("Malformed mmCIF atom_site table")
                for offset in range(0, len(values), len(fields)):
                    row = dict(zip([f.split(".", 1)[1] for f in fields], values[offset:offset+len(fields)]))
                    models.add(row.get("pdbx_PDB_model_num", "1"))
                    if len(models) > 1:
                        raise WorkflowError("Multi-model mmCIF is not supported")
                    if row.get("label_alt_id", ".") not in {".", "?"}:
                        raise WorkflowError("Resolve alternate atom locations")
                    def label(auth, fallback):
                        return row.get(auth) if row.get(auth) not in {None, ".", "?"} else row[fallback]
                    atoms.append((row["group_PDB"] == "ATOM", label("auth_asym_id", "label_asym_id"),
                                  label("auth_seq_id", "label_seq_id") + row.get("pdbx_PDB_ins_code", "").replace("?", "").replace(".", ""),
                                  label("auth_comp_id", "label_comp_id"), label("auth_atom_id", "label_atom_id"),
                                  [float(row[f"Cartn_{axis}"]) for axis in "xyz"]))
    except (ValueError, KeyError, IndexError, UnicodeError) as exc:
        if isinstance(exc, WorkflowError):
            raise
        raise WorkflowError(f"Invalid structure: {name}") from exc
    if not atoms or any(not math.isfinite(c) for atom in atoms for c in atom[5]):
        raise WorkflowError("Structure is empty or has nonfinite coordinates")
    residues, ligand = {}, False
    for protein, chain, number, residue, atom, xyz in atoms:
        if protein and residue not in STANDARD:
            raise WorkflowError("Nonstandard protein residue requires an audited chemistry/preparation contract")
        if protein and residue in STANDARD:
            key = (chain, number, residue)
            if atom in residues.setdefault(key, set()):
                raise WorkflowError("Duplicate atoms in a residue")
            residues[key].add(atom)
        elif not protein and residue not in {"HOH", "WAT", "DOD"}:
            ligand = True
    if not residues:
        raise WorkflowError("No standard protein residues in structure")
    all_atom = all({"N", "CA", "C", "O", *SIDECHAINS[r].split()} <= atom_names
                   for (_, _, r), atom_names in residues.items())
    capabilities = ["structure"] + (["all_atom"] if all_atom else ["backbone_or_incomplete"])
    if ligand:
        capabilities.append("ligand")
    chains = {}
    for chain, number, residue in residues:
        chains.setdefault(chain, []).append(ONE_LETTER[residue])
    return {"capabilities": capabilities, "residue_count": len(residues), "atom_count": len(atoms),
            "structural_sequence": ":".join("".join(v) for v in chains.values()),
            "residues": [f"{chain}{number}" for chain, number, _ in residues]}


def normalize_mapping(mapping, residues):
    """Convert verified tool mappings to the hosted geometry JSON contract."""
    result = {}
    if isinstance(mapping, list):
        for row in mapping:
            key = row.get("input_residue")
            if "input_chain" in row:
                key = row["input_chain"] + str(key)
            target = str(row.get("output_residue", ""))
            match = re.fullmatch(r"([A-Za-z]+)?[:_]?(-?\d+)([A-Za-z]?)", target)
            if not key or not match:
                raise WorkflowError("Unsupported upstream residue mapping schema")
            if key in result:
                raise WorkflowError("Duplicate upstream mapping key")
            result[key] = {"chain_id": match[1] or "A", "residue_number": int(match[2]), "insertion_code": match[3]}
    elif isinstance(mapping, dict):
        result = mapping
    else:
        raise WorkflowError("Residue mapping must be an explicit mapping-key object")
    for key, value in result.items():
        if not isinstance(key, str) or not key or not isinstance(value, dict) or set(value) - {"chain_id", "residue_number", "insertion_code"}:
            raise WorkflowError("Malformed residue mapping")
        if not isinstance(value.get("chain_id"), str) or type(value.get("residue_number")) is not int or not isinstance(value.get("insertion_code", ""), str):
            raise WorkflowError("Mapping location requires chain_id, integer residue_number and optional insertion_code")
        target = f"{value['chain_id']}{value['residue_number']}{value.get('insertion_code', '')}"
        if target not in residues:
            raise WorkflowError("Mapped target residue is absent from this structure")
    return result


def inspect_artifact(path, adapter):
    members = read_members(path)
    entries = []
    if adapter == "structures":
        structures = [(name, value) for name, value in members.items() if name.lower().endswith((".pdb", ".cif", ".mmcif"))]
        if not structures or len(structures) > 1000:
            raise WorkflowError("Expected 1–1000 structures")
        mapping_name = next((n for n in members if n == "residue_mapping.csv"), None)
        mappings = csv_rows(members[mapping_name]) if mapping_name else []
        for name, value in structures:
            label = Path(name).stem
            result = inspect_structure(name, value)
            matches = [r for r in mappings if r.get("sample", label) == label]
            if matches:
                result["mapping"] = normalize_mapping(matches, result["residues"])
                result["capabilities"].append("mapping")
            entries.append({"label": label, "member": name, **result})
    elif adapter == "sequences":
        for name, value in members.items():
            if name.lower().endswith((".fa", ".fasta", ".faa")):
                entries.extend({**r, "member": name, "capabilities": ["sequence"]} for r in fasta_rows(value))
            elif name.lower().endswith(".csv"):
                rows = csv_rows(value)
                sequence_column = next((k for k in rows[0] if k.lower() in {"sequence", "sequences"}), None)
                if sequence_column:
                    for i, row in enumerate(rows):
                        validate_sequence(row[sequence_column])
                        label = row.get("file_name") or row.get("seq_id") or row.get("Sequence_ID") or row.get("id")
                        if not label:
                            raise WorkflowError("Sequence rows need explicit labels; row-order pairing is forbidden")
                        entries.append({"label": label, "sequence": row[sequence_column], "member": name,
                                        "capabilities": ["sequence"]})
        # Archives may contain both FASTA and its CSV projection. A caller must
        # select a single authoritative member rather than deduplicate by guess.
        if len({e["label"] for e in entries}) != len(entries):
            raise WorkflowError("Multiple sequence representations; ingest one authoritative FASTA/CSV member")
    elif adapter == "pockets":
        tables = [(n, v) for n, v in members.items() if n.lower().endswith(".csv")]
        if len(tables) != 1:
            raise WorkflowError("DeepAllo requires one authoritative pocket CSV")
        rows = csv_rows(tables[0][1], ["pocket_id", "probability"])
        for row in rows:
            try:
                probability = float(row["probability"])
                if not math.isfinite(probability) or not 0 <= probability <= 1:
                    raise ValueError()
            except ValueError as exc:
                raise WorkflowError("Invalid DeepAllo pocket probability") from exc
        entries.append({"label": "pockets", "metrics": {"pockets": rows}})
    elif adapter in {"quality", "geometry"}:
        if "candidate_summary.csv" not in members:
            raise WorkflowError("Result ZIP is missing candidate_summary.csv")
        rows = csv_rows(members["candidate_summary.csv"], ["candidate_id", "status"])
        counts = ["checks_total", "checks_passed", "checks_rejected", "checks_invalid", "checks_measured"]
        required_metrics = QUALITY_METRICS if adapter == "quality" else counts
        for row in rows:
            if row["status"] not in {"measured", "passed", "rejected", "invalid"}:
                raise WorkflowError("Unknown candidate quality status")
            if row["status"] != "invalid" and any(row.get(k) in {None, ""} for k in required_metrics):
                raise WorkflowError("Result summary is missing required scientific metrics")
            for key, value in row.items():
                if key in {"candidate_id", "source_name", "status", "error", "failed_thresholds"} or not value:
                    continue
                try:
                    if not math.isfinite(float(value)):
                        raise WorkflowError("Result has nonfinite scientific metrics")
                except ValueError as exc:
                    if isinstance(exc, WorkflowError):
                        raise
                    raise WorkflowError("Result has malformed scientific metrics") from exc
            entries.append({"label": row["candidate_id"], "status": row["status"], "metrics": row})
        if adapter == "geometry":
            if "geometry_measurements.csv" not in members:
                raise WorkflowError("Geometry result is missing geometry_measurements.csv")
            measurements = csv_rows(members["geometry_measurements.csv"], ["candidate_id", "check_id", "status", "value"])
            expected_labels = {r["candidate_id"] for r in rows}
            if any(m["candidate_id"] not in expected_labels for m in measurements):
                raise WorkflowError("Geometry measurements refer to an unknown candidate")
            for row in rows:
                if row["status"] == "invalid":
                    continue
                current = [m for m in measurements if m["candidate_id"] == row["candidate_id"]]
                try:
                    numbers = {k: int(row[k]) for k in counts}
                    if any(n < 0 for n in numbers.values()) or numbers["checks_total"] != sum(numbers[k] for k in counts[1:]) or numbers["checks_total"] != len(current):
                        raise ValueError()
                except ValueError as exc:
                    raise WorkflowError("Geometry summary counts are inconsistent") from exc
                if len({m["check_id"] for m in current}) != len(current):
                    raise WorkflowError("Geometry check IDs are duplicated")
                for status in ("passed", "rejected", "invalid", "measured"):
                    if numbers["checks_" + status] != sum(m["status"] == status for m in current):
                        raise WorkflowError("Geometry check statuses do not match summary counts")
                for measurement in current:
                    if measurement["status"] in {"passed", "measured", "rejected"}:
                        try:
                            value = json.loads(measurement["value"])
                            validate_data(value)
                            if value is None or isinstance(value, (str, bool)):
                                raise ValueError()
                        except (ValueError, TypeError) as exc:
                            raise WorkflowError("Geometry result contains missing or invalid measurements") from exc
        if all(e["status"] == "invalid" for e in entries):
            raise WorkflowError("Every candidate is invalid; result cannot complete the stage")
    elif adapter == "report":
        for name, value in members.items():
            if name.lower().endswith(".csv"):
                for row in csv_rows(value):
                    label = next((row[k] for k in ("candidate_id", "seq_id", "Seq_id", "sequence_id", "Sequence_ID", "file_name") if row.get(k)), None)
                    if not label:
                        raise WorkflowError("Prediction report lacks a candidate join key; explicit preprocessing is needed")
                    status = row.get("status", "").lower()
                    if status in {"failed", "error", "invalid"}:
                        entries.append({"label": label, "metrics": row, "member": name, "status": "invalid"})
                    else:
                        for key, value in row.items():
                            if value.strip().lower() in {"nan", "inf", "-inf", "infinity", "-infinity"}:
                                raise WorkflowError("Prediction report contains nonfinite values")
                        identity = {"candidate_id", "seq_id", "Seq_id", "sequence_id", "Sequence_ID", "file_name",
                                    "sequence", "sequences", "Sequence", "SMILES", "smiles", "status", "error_message"}
                        numeric = []
                        for key, value in row.items():
                            if key not in identity:
                                try:
                                    numeric.append(float(value))
                                except ValueError:
                                    pass
                        if not numeric or any(not math.isfinite(v) for v in numeric):
                            raise WorkflowError("Prediction row has no finite scientific values")
                        entries.append({"label": label, "metrics": row, "member": name})
        if entries and all(e.get("status") == "invalid" for e in entries):
            raise WorkflowError("Every prediction failed")
    else:
        raise WorkflowError("Unsupported artifact adapter")
    if not entries:
        raise WorkflowError("No usable candidates in output artifact")
    if len({e["label"] for e in entries}) != len(entries):
        raise WorkflowError("Output candidate labels are not unique")
    validate_data(entries)
    return {"sha256": file_hash(path), "entries": entries, "members": members}

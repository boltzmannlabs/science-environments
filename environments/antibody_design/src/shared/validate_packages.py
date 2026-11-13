#!/usr/bin/env python3
"""Validate the five retained task packages without running scientific tools."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import re
import sys
from urllib.parse import unquote

ENV = Path(__file__).resolve().parents[2]
SHARED = ENV / 'src/shared'
TASKS = sorted(p.name for p in (ENV/'src').glob('task_00[1-5]*') if p.is_dir())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def table(path):
    with path.open(newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) != len(set(header)) or any(not x for x in header):
            raise ValueError('empty or duplicate CSV header')
        rows = list(reader)
        if any(len(row) != len(header) for row in rows):
            raise ValueError('CSV row width differs from header')
        return [dict(zip(header,row)) for row in rows]


def json_records(path):
    content=path.read_text()
    def reject_nonfinite(value):
        raise ValueError(f'nonfinite JSON value: {value}')
    try:
        return json.loads(content,parse_constant=reject_nonfinite), 1
    except json.JSONDecodeError:
        # Existing RAbD test and output summary files use JSONL with .json names.
        lines=[x for x in content.splitlines() if x.strip()]
        if len(lines) < 2: raise
        return [json.loads(x,parse_constant=reject_nonfinite) for x in lines], len(lines)


def fasta(path):
    records={}; current=None
    for line in path.read_text().splitlines():
        if line.startswith('>'):
            current=line[1:].split()[0]
            if current in records: raise ValueError('duplicate FASTA header')
            records[current]=''
        elif line.strip():
            if current is None: raise ValueError('sequence before FASTA header')
            records[current]+=line.strip()
    if any(not seq or not re.fullmatch('[A-Z*.-]+',seq) for seq in records.values()):
        raise ValueError('empty or malformed FASTA sequence')
    return records


def candidate_from_header(header):
    return re.sub(r'_(heavy|light)$','',header.split('|')[0])


def main():
    errors=[]; checks={}; run_records=[]; raw_table_notes=[]
    checked_at=datetime.now(timezone.utc).isoformat()
    files=[]
    for group in ('src','results'):
        for task in TASKS:
            files.extend(x for x in (ENV/group/task).rglob('*') if x.is_file())
    files.extend(x for x in SHARED.rglob('*') if x.is_file())
    counts={'json_files':0,'jsonl_records':0,'csv_files':0,'markdown_links':0,
            'table_artifact_paths':0,'imported_originals':0,'protected_definitions':0}
    for path in files:
        # An archived malformed export is preserved as evidence, not promoted
        # into a valid active artifact. Its bytes are checked by the manifest.
        if any(x in path.parts for x in ['import_history','packaging_history']):
            continue
        try:
            if path.suffix=='.json':
                _,n=json_records(path);counts['json_files']+=1
                if n>1:counts['jsonl_records']+=n
            elif path.suffix=='.csv':
                if 'released_archive' in path.parts:
                    with path.open(newline='') as f:
                        raw_rows=list(csv.reader(f))
                    if not raw_rows or any(len(row)!=len(raw_rows[0]) for row in raw_rows):
                        raise ValueError('raw upstream CSV row width mismatch')
                    if len(raw_rows[0])!=len(set(raw_rows[0])) or any(not x for x in raw_rows[0]):
                        raw_table_notes.append(str(path.relative_to(ENV)))
                else: table(path)
                counts['csv_files']+=1
        except (ValueError,StopIteration,UnicodeError) as e:
            errors.append(f'{path.relative_to(ENV)}: {e}')
    for row in table(SHARED/'import_manifest.csv'):
        p=ENV/row['current_path']
        if not p.is_file() or digest(p)!=row['original_sha256']:
            errors.append(f'Imported original missing/changed: {row["original_path"]}')
        counts['imported_originals']+=1
    for row in json.loads((SHARED/'protected_definitions.json').read_text()):
        path=ENV/row['path']
        if not path.is_file() or digest(path)!=row['sha256']:
            errors.append(f'Protected task/benchmark changed: {row["path"]}')
        counts['protected_definitions']+=1

    for task in TASKS:
        src=ENV/'src'/task
        for name in ['README.md','tool_catalog.json','approaches.md','workflow.md','runs.csv']:
            if not (src/name).is_file():errors.append(f'{task}: missing source {name}')
        register=table(src/'runs.csv')
        for row in register:
            run=row['run_id'];s=src/'runs'/run;r=ENV/'results'/task/run
            run_errors=[]
            for name in ['execution.md','provenance.json','configs/workflow_snapshot.md']:
                if not (s/name).is_file():run_errors.append(f'missing source {name}')
            provenance=json.loads((s/'provenance.json').read_text())
            if provenance.get('task_id')!=task or provenance.get('run_id')!=run:
                run_errors.append('source provenance identity mismatch')
            if not row['result_run']:
                if r.exists() or provenance.get('results_directory') is not None:
                    run_errors.append('unsubmitted run claims a results directory')
                errors.extend(f'{task}/{run}: {x}' for x in run_errors)
                continue
            for name in ['report.md','candidates.csv','metrics.json','benchmark_comparison.csv','benchmark_report.md']:
                if not (r/name).is_file():run_errors.append(f'missing result {name}')
            candidates=table(r/'candidates.csv');ids=[x['candidate_id'] for x in candidates]
            if len(ids)!=len(set(ids)):run_errors.append('duplicate candidate IDs')
            shortlist=table(r/'shortlist.csv') if (r/'shortlist.csv').exists() else []
            selected={x['candidate_id'] for x in shortlist}
            if not selected.issubset(set(ids)):run_errors.append('shortlist not contained in candidate inventory')
            seqpath=r/('designed_sequences.fasta' if (r/'designed_sequences.fasta').exists() else 'sequences.fasta')
            sequences=fasta(seqpath)
            sequence_ids={candidate_from_header(h) for h in sequences}
            if not selected.issubset(sequence_ids):run_errors.append('shortlist lacks exported sequences')
            if not sequence_ids.issubset(set(ids)):run_errors.append('exported sequence IDs absent from inventory')
            for name in ['candidates.csv','shortlist.csv','predictions.csv']:
                if not (r/name).exists():continue
                for item in table(r/name):
                    for key in ['structure_file','structure_path','sequence_path','evidence_path','abodybuilder2_structure']:
                        value=item.get(key,'')
                        if value:
                            counts['table_artifact_paths']+=1
                            if not (r/value).is_file():run_errors.append(f'{name}: missing {key}={value}')
            controls=sum(x.get('selection_status')=='reference_control' for x in candidates)
            record={'task_id':task,'run_id':run,'validation_scope':'packaging',
                    'checked_at_utc':checked_at,'packaging_status':'passed' if not run_errors else 'failed',
                    'scientific_coverage':row['scientific_coverage'],
                    'candidate_rows_including_controls':len(candidates),'reference_rows':controls,
                    'selected_rows':len(shortlist),'assessment_rows':len(table(r/'predictions.csv')) if (r/'predictions.csv').exists() else 0,
                    'exported_fasta_records':len(sequences),
                    'exported_candidate_or_control_ids':sorted(sequence_ids),
                    'structure_files':sum(x.is_file() for x in (r/'structures').rglob('*')),
                    'checks':['required files','task/run identity','unique candidate IDs','shortlist membership','FASTA ID coverage','canonical artifact paths'],
                    'scientific_reexecution_performed':False,'issues':run_errors}
            run_records.append(record)
            errors.extend(f'{task}/{run}: {x}' for x in run_errors)

    # Check active Markdown links. Source snapshots, imported vendor documents
    # and historical archives retain their original context and are not active navigation.
    documents=[ENV/'ENVIRONMENT_SPEC.md',ENV/'README.md',ENV/'status.md',ENV/'src/readme.md',ENV/'results/README.md']
    documents.extend(p for p in files if p.suffix=='.md' and not any(x in p.parts for x in ['import_history','packaging_history','released_archive','benchmark_sources','code_snapshot','inputs']))
    for doc in sorted(set(documents)):
        if not doc.exists():errors.append(f'Missing document: {doc.relative_to(ENV)}');continue
        content=re.sub(r'```.*?```','',doc.read_text(),flags=re.S)
        for match in re.finditer(r'(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)',content):
            target=match.group(1).strip().strip('<>')
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            target=unquote(target.split('#',1)[0])
            counts['markdown_links']+=1
            if target and not (doc.parent/target).exists():
                errors.append(f'{doc.relative_to(ENV)}: broken link {target}')

    checks['counts']=counts
    checks['raw_upstream_tables_with_noncanonical_headers']=raw_table_notes
    report={'checked_at_utc':checked_at,'validation_scope':'packaging',
            'status':'passed' if not errors else 'failed','task_packages':len(TASKS),
            'source_runs':sum(len(table(ENV/'src'/t/'runs.csv')) for t in TASKS),
            'result_runs':len(run_records),'checks':checks,'runs':run_records,'issues':errors,
            'limits':['No scientific tool execution or fresh benchmark reproduction',
                      'No independent molecular geometry, binding or sequence/model scientific validation',
                      'External dependency restoration and historical absolute paths are documented separately',
                      'Archived original metadata is checked by preservation hashes, not required to satisfy current syntax rules',
                      'Archived checksum records are historical; current file hashes are in package_inventory.csv']}
    print(json.dumps({'status':report['status'],'tasks':len(TASKS),'result_runs':len(run_records),'counts':counts,'issues':errors},indent=2))
    for record in run_records:
        p=ENV/'results'/record['task_id']/record['run_id']/'evidence/validation.json'
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(record,indent=2)+'\n')
    evidence=SHARED/'validation';evidence.mkdir(parents=True,exist_ok=True)
    (evidence/'layout_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (evidence/'packaging_validation.md').write_text(f'''# Five-Task Packaging Validation

Checked: {checked_at}. Status: **{report['status']}**.

Validated {len(TASKS)} task packages, {report['source_runs']} source runs and {len(run_records)} result runs. Checked {counts['imported_originals']} preserved imported files, {counts['protected_definitions']} unchanged task/benchmark definitions, {counts['csv_files']} CSV files, {counts['json_files']} JSON/JSONL files, {counts['markdown_links']} local Markdown links and {counts['table_artifact_paths']} canonical table artifact paths.

Checks cover required files, task/run identities, unique IDs, shortlist membership, exported FASTA ID coverage, file syntax, links and preservation hashes. {len(raw_table_notes)} raw upstream CSV tables retain original duplicate/unnamed headers and were checked as rectangular raw tables, rather than canonical named-column results. The [machine-readable report](layout_validation.json) records per-run counts and any issues. The [fresh package inventory](../package_inventory.csv) records current hashes.

Scientific coverage remains as reported in each task. No scientific tools ran, no fresh benchmark was reproduced, and molecular identity/geometry was not independently revalidated. External dependencies and historical absolute paths require restoration/configuration before reruns. Historical metadata/checksums remain archived; they do not replace this validation.
''')
    # Build a non-self-referential final inventory after writing validation.
    candidates=[ENV/'ENVIRONMENT_SPEC.md',ENV/'README.md',ENV/'status.md',ENV/'.gitignore',ENV/'src/readme.md',ENV/'results/README.md']
    for group in ('src','results'):
        for task in TASKS:candidates.extend(p for p in (ENV/group/task).rglob('*') if p.is_file())
    candidates.extend(p for p in SHARED.rglob('*') if p.is_file())
    omitted={SHARED/'package_inventory.csv'}
    with (SHARED/'package_inventory.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);writer.writeheader()
        for p in sorted(set(candidates)-omitted):
            writer.writerow({'path':str(p.relative_to(ENV)),'bytes':p.stat().st_size,'sha256':digest(p)})
    return 1 if errors else 0


if __name__=='__main__':
    sys.exit(main())

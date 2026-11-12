"""Validate task structure and supplied file integrity, not scientific outcomes."""
import csv
import hashlib
import json
import re
from pathlib import Path
from gen_config import build_config

ROOT=Path(__file__).resolve().parents[1]
SECTIONS=['Objective','Target','Inputs','Constraints','Expected Output','Important Instructions']

def validate(root=ROOT):
    errors=[]
    paths=sorted((root/'tasks').glob('task_*.md'))
    if not paths:return ['No task documents found']
    for i,path in enumerate(paths,1):
        text=path.read_text()
        if not re.match(rf'^task_{i:03d}_[a-z0-9_]+\.md$',path.name):errors.append('Noncanonical task name: '+path.name)
        if re.findall(r'^## (.+)$',text,re.M)!=SECTIONS:errors.append('Incorrect task section structure')
        if re.search(r'(?i)doi\.org|PMC\d+|AutoDock|Swiss.?Model|SwissADME|GROMACS|OpenMM|Diffdock|Property_Prediction|molecular dynamics|simulation',text):
            errors.append('Task exposes source outcomes, software or a prescribed simulation')
        for name in re.findall(r'`(inputs/[^`]+)`',text):
            if not (root/name).is_file():errors.append('Missing task input: '+name)
        if '**top 8 library candidates**' not in text or '**2 final priority candidates**' not in text:
            errors.append('Missing requested candidate counts')
        if 'detailed scientific report' not in text.lower():errors.append('Missing detailed report')
        if not (root/'benchmark'/path.name).is_file():errors.append('Missing owner metadata')
    manifest=root/'inputs/manifest.csv'
    if not manifest.is_file():errors.append('Missing input manifest')
    else:
        with manifest.open() as f:
            for row in csv.DictReader(f):
                p=root/row['file']
                if not p.resolve().is_relative_to(root.resolve()):errors.append('Input path escapes environment');continue
                if not p.is_file():errors.append('Missing manifest input: '+row['file']);continue
                if hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']:errors.append('Input checksum mismatch: '+row['file'])
    library=root/'inputs/library/compounds_400.csv'
    if library.is_file():
        with library.open() as f:rows=list(csv.DictReader(f))
        if len(rows)!=400 or [x['compound_id'] for x in rows]!=[str(i) for i in range(1,401)]:
            errors.append('Source library must retain 400 sequential records')
        sdf=root/'inputs/library/compounds_400.sdf'
        if sdf.is_file():
            records=[x for x in sdf.read_text().split('$$$$') if x.strip()]
            if len(records)!=400:errors.append('SDF record count mismatch')
            else:
                for row,record in zip(rows,records):
                    props=dict(re.findall(r'>\s*<([^>]+)>[^\n]*\n([^\n]*)',record))
                    if any(props.get(k)!=row[v] for k,v in [('compound_id','compound_id'),('zinc_id','zinc_id'),('source_smiles','smiles'),('inchikey','inchikey')]):
                        errors.append('CSV/SDF identity metadata mismatch: '+row['compound_id'])
    for name,columns in [('targets/target_registry.csv',['source_cif','selected_raw_pdb','bound_control']),
                         ('controls/control_registry.csv',['file'])]:
        path=root/'inputs'/name
        if not path.is_file():errors.append('Missing input registry: '+name);continue
        with path.open() as f:
            for row in csv.DictReader(f):
                for col in columns:
                    if not (root/row[col]).is_file():errors.append('Missing registered input: '+row[col])
    config=root/'config/environment.json'
    if not config.is_file() or json.loads(config.read_text())!=build_config(root):errors.append('Config differs from task documents')
    readme=(root/'README.md').read_text()
    for task in paths:
        if 'tasks/'+task.name not in readme:errors.append('README missing task link')
    return errors

if __name__=='__main__':
    issues=validate()
    print('\n'.join(issues) if issues else 'PASS: task structure, library metadata, registered inputs, checksums and config')
    raise SystemExit(bool(issues))

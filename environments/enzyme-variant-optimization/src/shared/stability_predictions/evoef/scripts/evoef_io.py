"""Strict source-bound protein view and native EvoEF energy parsing; no science model."""
import re,math,hashlib
AA3=dict(zip('ALA ARG ASN ASP CYS GLN GLU GLY HIS ILE LEU LYS MET PHE PRO SER THR TRP TYR VAL'.split(),'ARNDCQEGHILKMFPSTWYV'))
AA3.update({'HSD':'H','HSE':'H','HSP':'H'})
def protein_view(text,expected,chain='A'):
 records=[];residues={};seen=set();excluded={};models=0
 for line in text.splitlines(keepends=True):
  if line.startswith('MODEL'):models+=1
  if line.startswith('ENDMDL'):break
  if not line.startswith('ATOM') or line[21]!=chain:
   key=line[:6].strip();excluded[key]=excluded.get(key,0)+1;continue
  if line[16]!=' ' or line[26]!=' ':raise ValueError('Alternate/insertion identity unsupported')
  num=int(line[22:26]);name=line[12:16].strip();rn=line[17:20]
  if rn not in AA3:raise ValueError('Nonstandard protein residue '+rn)
  key=(num,name)
  if key in seen:raise ValueError('Duplicate atom')
  seen.add(key)
  if num not in residues:residues[num]={'aa':AA3[rn],'atoms':set()}
  if residues[num]['aa']!=AA3[rn]:raise ValueError('Inconsistent residue type')
  residues[num]['atoms'].add(name)
  for v in [line[30:38],line[38:46],line[46:54]]:
   if not math.isfinite(float(v)):raise ValueError('Nonfinite coordinate')
  records.append(line if line.endswith('\n') else line+'\n')
 if list(residues)!=list(range(1,len(expected)+1)):raise ValueError('Full frozen numbering/coverage mismatch')
 seq=''.join(v['aa'] for v in residues.values())
 if seq!=expected:raise ValueError('Frozen sequence mismatch')
 for n,r in residues.items():
  if not {'N','CA','C','O'}.issubset(r['atoms']):raise ValueError('Missing backbone at '+str(n))
 view=''.join(records)+'TER\nEND\n'
 return view,{'sequence':seq,'sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),'residues':len(residues),'atoms':len(records),'chain':chain,'policy':'first native model; exact chain; protein ATOM records unchanged; all ligand/water/other-chain records excluded for intrinsic protein folding DDG, not reactive-scene qualification','excluded_record_counts':excluded,'view_sha256':hashlib.sha256(view.encode()).hexdigest()}
def parse_total(text):
 vals=re.findall(r'^Total\s*=\s*(\S+)\s*$',text,re.M)
 if len(vals)!=1:raise ValueError('Expected exactly one native Total')
 value=float(vals[0])
 if not math.isfinite(value):raise ValueError('Nonfinite native Total')
 return value

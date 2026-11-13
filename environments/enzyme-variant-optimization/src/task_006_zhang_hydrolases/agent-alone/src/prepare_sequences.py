"""Extract exact primary sequences/tables and verify retrospective stage inputs."""
import csv
import hashlib
import json
import pathlib
import re
import xml.etree.ElementTree as ET
import zipfile

ARM = pathlib.Path(__file__).resolve().parents[1]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main', 'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'}
AA = set('ACDEFGHIKLMNPQRSTVWY')

def text(element):
    return ''.join(e.text or '' for e in element.iter() if e.tag in {f"{{{NS['w']}}}t", f"{{{NS['m']}}}t"})

def mutate(seq, mutations):
    s = list(seq)
    for mutation in mutations:
        match = re.fullmatch(r'([A-Z])(\d+)([A-Z])', mutation)
        if not match:
            raise ValueError(mutation)
        wt, pos, mt = match.groups()
        index = int(pos) - 1
        if s[index] != wt or mt not in AA:
            raise ValueError(f'Invalid mutation {mutation}: observed {s[index]}')
        s[index] = mt
    return ''.join(s)

if __name__ == '__main__':
    with zipfile.ZipFile(ARM/'sources/supplement_probe.docx') as z:
        root = ET.fromstring(z.read('word/document.xml'))
    paragraphs = [text(p).strip() for p in root.findall('.//w:body/w:p', NS)]
    seqs = {}
    labels = {'cellulase-WT': 'cellulase_WT', 'cellulase-M5': 'cellulase_M5', 'β-glucanase-WT': 'beta_glucanase_WT', 'β-glucanase-M7': 'beta_glucanase_M7'}
    for i, p in enumerate(paragraphs):
        if p.startswith('>'):
            label = p[1:].strip()
            if label in labels:
                seq = next(q for q in paragraphs[i+1:] if q)
                if not set(seq) <= AA:
                    raise ValueError('Unexpected sequence alphabet: ' + label)
                seqs[labels[label]] = {'sequence': seq, 'provenance': 'Original supporting information section 3.3, verbatim extraction'}
    if len(seqs) != 4:
        raise ValueError('Not all four original sequences were recovered')
    intermediates = {'cellulase_M2': ('cellulase_WT', ['G177P','L302R'], 'Original Table S2, explicit G177P/L302R (M2) row'), 'beta_glucanase_M5': ('beta_glucanase_WT', ['A142S','S196K','N65I','L45E','N38S'], 'Original Table S6 M1 through M5 selected accumulation path')}
    for name,(parent, mutations, provenance) in intermediates.items():
        seqs[name] = {'sequence': mutate(seqs[parent]['sequence'], mutations), 'parent': parent, 'mutations': mutations, 'provenance': provenance, 'retrospective_experimental_background': True}
    for final, base, mutations in [('cellulase_M5','cellulase_M2',['I34M','Y252F','L287E']),('beta_glucanase_M7','beta_glucanase_M5',['H206Y','Y25W'])]:
        if mutate(seqs[base]['sequence'], mutations) != seqs[final]['sequence']:
            raise ValueError('Documented final transition disagrees with supplied sequence: '+final)
    dest = ARM/'inputs'
    dest.mkdir(exist_ok=True)
    for name, record in seqs.items():
        seq = record['sequence']
        record.update(length=len(seq), sequence_sha256=hashlib.sha256(seq.encode()).hexdigest())
        path = dest/(name+'.fasta')
        path.write_text('>'+name+'\n'+seq+'\n')
        record['fasta'] = str(path)
        record['fasta_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if '_WT' not in name:
            parent = seqs[name.split('_M')[0]+'_WT']['sequence']
            record['differences_from_WT'] = [f'{a}{i}{b}' for i,(a,b) in enumerate(zip(parent,seq),1) if a!=b]
    (dest/'sequences.json').write_text(json.dumps(seqs,indent=2)+'\n')
    refs = ARM/'paper_reference'
    refs.mkdir(exist_ok=True)
    for i, table in enumerate(root.findall('.//w:body/w:tbl', NS), 1):
        rows = [[text(c).strip() for c in row.findall('w:tc',NS)] for row in table.findall('w:tr',NS)]
        with (refs/f'Table_S{i}.csv').open('w',newline='') as f:
            csv.writer(f).writerows(rows)
    (refs/'supplement_text.txt').write_text('\n\n'.join(paragraphs)+'\n')
    math = [''.join(e.itertext()) for e in root.findall('.//m:oMath',NS)]
    (refs/'original_equations.txt').write_text('\n'.join(math)+'\n')
    print(json.dumps({name:{k:v for k,v in record.items() if k!='sequence'} for name,record in seqs.items()},indent=2))
    print('Extracted tables:',len(root.findall('.//w:body/w:tbl',NS)))

"""Read-only source discovery and primary transcript verification for the approved campaign."""
import json, pathlib, urllib.request, urllib.parse, hashlib, datetime, gzip
ROOT=pathlib.Path(__file__).resolve().parents[1]
RUN='Run-3_2026-11-11'
OUT=ROOT/'benchmark/011_Campaign-reproduction'/RUN
OUT.mkdir(parents=True,exist_ok=True)
if (OUT/'transcript_verification.json').exists():
    raise RuntimeError('Primary-source snapshot already exists; preserve it and choose a fresh run for retrieval.')
SOURCE=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/siRNA-Design-Task-Specific')
items=[('HK2','NM_000189.5','11_app_benchmarks/hk2_NM_000189.5.fa'),('MYC','NM_002467.6','11_app_benchmarks/myc_NM_002467.6.fa'),('PCSK9','NM_174936.4',None),('TNF','NM_000594.4',None),('HIF1A','NM_001530.4','07_case_study/HIF1AN_NM_001530.4_RNA.fa')]
records=[]
for gene,acc,local in items:
    url='https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'+urllib.parse.urlencode({'db':'nuccore','id':acc,'rettype':'fasta','retmode':'text'})
    rec={'gene':gene,'requested_accession':acc,'url':url,'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        text=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GeneSilencingBenchmark/1.0'}),timeout=90).read().decode()
        assert text.startswith('>'+acc+' '), text[:200]
        assert '('+gene+')' in text.splitlines()[0], text.splitlines()[0]
        seq=''.join(text.splitlines()[1:]).upper()
        assert set(seq)<=set('ACGT')
        (OUT/(gene+'_primary.fasta')).write_text(text)
        rec.update(status='VERIFIED_PRIMARY',length=len(seq),header=text.splitlines()[0],sha256=hashlib.sha256(text.encode()).hexdigest())
        if local:
            src=SOURCE/local
            lseq=''.join(src.read_text().splitlines()[1:]).replace('U','T')
            rec.update(local_source=str(src),local_sequence_identical=lseq==seq,local_sha256=hashlib.sha256(src.read_bytes()).hexdigest())
        (OUT/(gene+'_RNA.fa')).write_text('>'+acc+' '+gene+'; NCBI RefSeq; RNA conversion T->U\n'+seq.replace('T','U')+'\n')
    except Exception as e:
        rec.update(status='BLOCKED_PRIMARY_LOOKUP',error=str(e))
    records.append(rec)
# Verify original Ensembl target against the installed GENCODE reference; do not alter it.
p=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/references/gencode.v50.transcripts.fa.gz')
with gzip.open(p,'rt') as f:
    header=None;buf=[]
    for line in f:
        if line.startswith('>'):
            if header and header.split('|')[0]=='>ENST00000237014.8': break
            header=line.strip();buf=[]
        else: buf.append(line.strip())
    seq=''.join(buf)
local=SOURCE/'04_benchmark_run/inputs/TTR_transcript.fa'
lseq=''.join(local.read_text().splitlines()[1:]).replace('U','T')
assert header is not None and header.split('|')[0]=='>ENST00000237014.8' and '|TTR|' in header and seq==lseq
records.append({'gene':'TTR','status':'VERIFIED_LOCAL_GENCODE','accession':'ENST00000237014.8','header':header,'length':len(seq),'reference':str(p),'sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),'local_sequence_identical':True})
(OUT/'transcript_verification.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))

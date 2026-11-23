from pathlib import Path
import io,json,csv,zipfile,hashlib
import numpy as np
import Bio
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
from Bio.SVDSuperimposer import SVDSuperimposer
B=Path('/home/boltzmann4/.sci/profiles/monoclonal_antibodies1/cache/scratch/vhh_run')
p=PDBParser(QUIET=True)
def residues(ch): return [r for r in ch if r.id[0]==' ' and 'CA' in r]
def sequence(rs): return ''.join(seq1(r.resname) for r in rs)
def coords(rs): return np.array([r['CA'].coord for r in rs],dtype=float)
def fit(ref,mob):
    s=SVDSuperimposer();s.set(ref,mob);s.run();R,t=s.get_rotran();return R,t,s.get_rms()
def rms(a,b): return float(np.sqrt(np.mean(np.sum((a-b)**2,axis=1))))
# Verify rigid-transform recovery, not a hand-coded alignment convention.
rng=np.random.default_rng(7);x=rng.normal(size=(30,3));q,_=np.linalg.qr(rng.normal(size=(3,3)));q[:,0]*=np.linalg.det(q)
y=x@q+np.array([3.,7.,-2.]);R,t,e=fit(x,y);assert e<1e-10 and rms(x,y@R+t)<1e-10
props=json.loads((B/'ppiflow50_props.json').read_text());prop=next(r for r in props if r['id']=='ppiflow_HA_nanobody_run_2_s1')
des=p.get_structure('design',B/'ppiflow_HA/extracted/nanobody_run_2.pdb')[0]
dv=residues(des['A']);da=residues(des['B']);assert len(dv)==121 and len(da)==170
metrics=next(r for r in csv.DictReader((B/'ppiflow_HA/raw_out/sample_metrics.csv').open()) if r['pdb_name']=='nanobody_run_2')
cdr={k:json.loads(metrics[k]) for k in ['cdr_H1','cdr_H2','cdr_H3']};cdrpos=set(sum(cdr.values(),[]));fw=[i for i in range(121) if i+1 not in cdrpos]
parent=residues(p.get_structure('parent',B/'raw/3EAK.pdb')[0]['A']);ps=sequence(parent);expected_fw=ps[:25]+ps[35:54]+ps[60:101]+ps[117:127]
actual_fw=''.join(prop['seq'][i] for i in fw)
out={'versions':{'biopython':Bio.__version__,'numpy':np.__version__},'candidate':prop,'design':{'cdr_positions':cdr,'cdr_sequences':{k:''.join(prop['seq'][i-1] for i in v) for k,v in cdr.items()},'framework_count':len(fw),'framework_matches_parent':actual_fw==expected_fw,'framework_sequence':actual_fw,'parent_framework_sequence':expected_fw,'service_metrics':metrics},'structures':{},'hashes':{}}
for label,path in [('old_HA',B/'boltz2/run2s1/boltz_pdb/1_model_0.pdb'),('old_RSV',B/'boltz2/run2s1_rsv/boltz_pdb/1_model_0.pdb')]:
    m=p.get_structure(label,path)[0];v=residues(m['A']);a=residues(m['B']);out['structures'][label]={'vhh_matches_sequence':sequence(v)==prop['seq'],'antigen_sequence':sequence(a)}
zpath=B/'boltz2_run2s1_ha_full.zip'
with zipfile.ZipFile(zpath) as z:
    names=z.namelist();pn=next(n for n in names if n.endswith('/1_model_0.pdb'))
    m=p.get_structure('new',io.StringIO(z.read(pn).decode()))[0];pv=residues(m['A']);pa=residues(m['B'])
    pae=np.load(io.BytesIO(z.read(next(n for n in names if n.endswith('/pae_1_model_0.npz')))))['pae']
    pl=np.load(io.BytesIO(z.read(next(n for n in names if n.endswith('/plddt_1_model_0.npz')))))['plddt']
    conf=json.loads(z.read(next(n for n in names if n.endswith('/confidence_1_model_0.json'))))
assert len(pv)==121 and len(pa)==170 and pae.shape==(291,291)
R,t,fold=fit(coords(dv),coords(pv));Ra,ta,ant=fit(coords(da),coords(pa))
fwR,fwt,fwRms=fit(coords(dv)[fw],coords(pv)[fw])
oldseq=out['structures']['old_HA']['antigen_sequence'];newseq=sequence(pa)
out['structures']['new_HA']={'vhh_matches_sequence':sequence(pv)==prop['seq'],'antigen_sequence':newseq,'antigen_changes_vs_old':[{'position':i+1,'old':a,'new':b} for i,(a,b) in enumerate(zip(oldseq,newseq)) if a!=b], 'vhh_CA_self_aligned_RMSD_A':fold,'framework_CA_self_aligned_RMSD_A':fwRms,'antigen_CA_self_aligned_RMSD_A':ant,'target_aligned_vhh_CA_RMSD_A':rms(coords(dv),coords(pv)@Ra+ta),'PAE_VHH_to_HA_A':float(pae[:121,121:].mean()),'PAE_HA_to_VHH_A':float(pae[121:,:121].mean()),'PAE_symmetric_cross_chain_mean_A':float((pae[:121,121:].mean()+pae[121:,:121].mean())/2),'mean_VHH_pLDDT_0to100':float(pl[:121].mean()*100),'confidence':conf}
for path in [zpath,B/'ppiflow50_props.json',B/'prodigy_4complexes.csv',B/'surf_agg.py',B/'props50.py',B/'ppiflow_HA/extracted/nanobody_run_2.pdb',B/'boltz2/run2s1/boltz_pdb/1_model_0.pdb',B/'boltz2/run2s1_rsv/boltz_pdb/1_model_0.pdb']:
    out['hashes'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
output=Path(__file__).with_name('documentation_audit.json');output.write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))

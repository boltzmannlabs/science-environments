import json, hashlib, os, csv
from datetime import datetime, timezone

WS='/home/boltzmann4/.sci/profiles/ab_task_10/workspace'
OUT=os.path.join(WS,'acvr2b_results')
os.makedirs(OUT,exist_ok=True)

cands=json.load(open(os.path.join(WS,'igdesign_repo/top_candidates.json')))
rmsd=json.load(open(os.path.join(WS,'scrmsd_preds/candidate_rmsd.json')))
NATIVE={'hcdr1':'GYTFTSSY','hcdr2':'INPVSGST','hcdr3':'ARGGWFDY'}
REF_RMSD={'HCDR1':0.2347,'HCDR2':0.6304,'HCDR3':0.3705,'HCDR123':0.4434,'Fv_whole':1.2140}

def sha(s): return hashlib.sha256(s.encode()).hexdigest()[:16]

# --- rank within each scope by HCDR123 scRMSD (lower=better); exclude unknown structure
def build(scope):
    rows=[]
    for c in cands[scope]:
        key=scope.lower().replace('hcdr','hcdr') + '_' + str(c['rank']).zfill(2)
        name={'HCDR3':'hcdr3','HCDR123':'hcdr123'}[scope]+'_'+str(c['rank']).zfill(2)
        r=rmsd.get(name)
        changes={}
        for k in ['hcdr1','hcdr2','hcdr3']:
            if c['cdrs'][k]!=NATIVE[k]:
                changes[k]=f"{NATIVE[k]}->{c['cdrs'][k]}"
        rows.append({'id':c['id'],'scope':scope,'seqrank':c['rank'],'ce_loss':c['score'],
            'HCDR1':c['cdrs']['hcdr1'],'HCDR2':c['cdrs']['hcdr2'],'HCDR3':c['cdrs']['hcdr3'],
            'vh':c['vh'],'vl':c['vl'],'changes':changes,
            'rmsd':r,'vh_sha256_16':sha(c['vh'])})
    have=[x for x in rows if x['rmsd'] is not None]
    have.sort(key=lambda x:x['rmsd']['HCDR123'])
    for i,x in enumerate(have,1): x['structrank']=i
    return rows

built={s:build(s) for s in ['HCDR3','HCDR123']}

# --- designed_sequences.fasta
with open(os.path.join(OUT,'designed_sequences.fasta'),'w') as f:
    f.write(">reference_VH Bimagrumab native VH (5NGV chain H, 113aa) | target=human ACVR2B (Q13705 mature 25-117) | reference=PDB 5NGV\n")
    f.write("VQLVQSGAEVKKPGASVKVSCKASGYTFTSSYINWVRQAPGQGLEWMGTINPVSGSTSYAQKFQGRVTMTRDTSISTAYMELSRLRSDDTAVYYCARGGWFDYWGQGTLVTVS\n")
    f.write(">reference_VL Bimagrumab native VL (5NGV chain L, 111aa) | preserved unchanged in all candidates\n")
    f.write(cands['HCDR3'][0]['vl']+'\n')
    for scope in ['HCDR3','HCDR123']:
        for x in built[scope]:
            if x['rmsd'] is None:
                tag='STRUCTURE_PREDICTION_INCOMPLETE'
            else:
                tag=f"structrank{x['structrank']} hcdr123_scRMSD={x['rmsd']['HCDR123']:.4f}A"
            f.write(f">{x['id']} scope={scope} ce_loss={x['ce_loss']:.4f} | {tag} | target=human ACVR2B (Q13705) | reference=PDB 5NGV | VH[1-113]\n")
            f.write(x['vh']+'\n')
            f.write(f">{x['id']}_VL scope={scope} | VL preserved (111aa)\n")
            f.write(x['vl']+'\n')

# --- shortlist.csv
with open(os.path.join(OUT,'shortlist.csv'),'w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['structrank','scope','candidate_id','seqrank_ce_loss','ce_loss_sum','HCDR1','HCDR2','HCDR3',
                'changes_from_reference','vh_sha256_16','hcdr1_scRMSD_A','hcdr2_scRMSD_A','hcdr3_scRMSD_A',
                'hcdr123_scRMSD_A','fv_scRMSD_A','delta_hcdr123_vs_reference_A','exclusion_reason'])
    for scope in ['HCDR3','HCDR123']:
        for x in built[scope]:
            if x['rmsd'] is None:
                w.writerow([x['seqrank'],scope,x['id'],x['seqrank'],f"{x['ce_loss']:.4f}",x['HCDR1'],x['HCDR2'],x['HCDR3'],
                    '; '.join(x['changes'].values()) or 'none',x['vh_sha256_16'],'','','','','',
                    'EXCLUDED: Boltzmann multimer submission timed out with unknown state; not retried per connector policy'])
                continue
            r=x['rmsd']
            w.writerow([x['structrank'],scope,x['id'],x['seqrank'],f"{x['ce_loss']:.4f}",x['HCDR1'],x['HCDR2'],x['HCDR3'],
                '; '.join(x['changes'].values()) or 'none',x['vh_sha256_16'],
                f"{r['HCDR1']:.4f}",f"{r['HCDR2']:.4f}",f"{r['HCDR3']:.4f}",f"{r['HCDR123']:.4f}",f"{r['Fv_whole']:.4f}",
                f"{r['HCDR123']-REF_RMSD['HCDR123']:+.4f}",''])

# --- metrics.json
metrics={
 'generated_utc':datetime.now(timezone.utc).isoformat(),
 'target':'Human ACVR2B (UniProt Q13705), exact supplied reference construct = 5NGV chain A fragment, mature residues 25-117 (93 aa)',
 'reference_antibody':'Bimagrumab (PDB 5NGV)',
 'reference_structure':'/home/boltzmann4/.sci/profiles/ab_task_10/workspace/igdesign_repo/examples/5ngv.pdb (chains A=antigen, H=VH, L=VL)',
 'native_sequences':{'VH':cands['HCDR3'][0]['vh'],'VL':cands['HCDR3'][0]['vl'],
   'HCDR1':'GYTFTSSY','HCDR2':'INPVSGST','HCDR3':'ARGGWFDY'},
 'cdr_positions_0indexed':{'HCDR1':'24:32','HCDR2':'49:57','HCDR3':'95:103'},
 'design_engine':'IgDesign (AbSciBio/igdesign @ 70431ee), checkpoint igdesign_acvr2b_holdout.ckpt, seed 0, temperature 0.5, 100 samples/scope (10 decoding orders x 10 ProteinMPNN seqs x 1 LM seq), condition on VL and ACVR2B, light chain not predicted, VL and framework preserved',
 'structure_predictor':'Boltzmann platform Multimer_Structure_Prediction (AlphaFold2-Multimer v3 / ColabFold), top-ranked (rank_001) model per job, VH+VL multimer',
 'scRMSD_protocol':'C-alpha atoms; whole-Fv (VH+VL, 224 CA) Kabsch superposition of predicted onto reference 5NGV (chain H VH with duplicate-resseq-10 GLU artifact excluded, chain L VL); regional C-alpha RMSD for HCDR1/2/3/123 (VH) and Fv_whole (all VH+VL). Units: angstrom. Same predictor, reference, atoms, alignment and regions for reference and all candidates.',
 'metric_definitions':{'AAR':'per-position identity vs native CDR over generated samples (1-shot = first sample; best-of-100 = max over 100)','scRMSD':'C-alpha RMSD in angstrom after whole-Fv Kabsch alignment'},
 'AAR':{'HCDR3_only':{'native':'ARGGWFDY','one_shot':0.875,'best_of_100':0.875,'mean':0.750,'one_shot_seq':'ARGSWFDY'},
        'HCDR123':{'HCDR1':{'native':'GYTFTSSY','one_shot':0.750,'best_of_100':1.0,'mean':0.897},
                   'HCDR2':{'native':'INPVSGST','one_shot':0.750,'best_of_100':0.875,'mean':0.703},
                   'HCDR3':{'native':'ARGGWFDY','one_shot':0.750,'best_of_100':1.0,'mean':0.757}}},
 'reference_rmsd_executed':REF_RMSD,
 'candidate_rmsd_executed':{x['id']:(x['rmsd'] if x['rmsd'] else None) for s in ['HCDR3','HCDR123'] for x in built[s]},
 'candidate_hashes_vh_sha256_16':{x['id']:x['vh_sha256_16'] for s in ['HCDR3','HCDR123'] for x in built[s]},
 'selection_criteria':'Top 10 per scope by summed independent IgDesign ce_loss from 100 samples (distinct CDR combos); shortlist ranked by executed HCDR123 scRMSD (lower=better)',
 'candidate_counts':{'samples_per_scope':100,'unique_hcdr3_combos':44,'unique_hcdr123_combos':89,'shortlist_per_scope':10,'structures_predicted':19,'structures_missing':1},
 'provenance':{'source_csv':'Bimagrumab-ACVR2B.csv (SHA-256 5775fdfa2b23802aa4a295e7b98d3bbd52f4bd83440e33a3c9a0fca723dfcae9)',
   'igdesign_commit':'70431eef0afaf0496d7d84e22dfdc1980ec9e70e',
   'boltzmann_jobs':'see scrmsd_preds/job_ledger.json (21 submissions: 1 reference + 20 candidates, 19 completed, 1 unknown-state)'}}
with open(os.path.join(OUT,'metrics.json'),'w') as f: json.dump(metrics,f,indent=1)

# --- benchmark_comparison.csv
with open(os.path.join(OUT,'benchmark_comparison.csv'),'w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['source','predictor','scope','HCDR1_scRMSD_A','HCDR2_scRMSD_A','HCDR3_scRMSD_A','HCDR123_scRMSD_A','Fv_scRMSD_A','note'])
    for pred,row in [('ABB2',(0.3593,0.3204,0.2988,0.3271,0.4350)),('ABB3',(0.3690,0.6996,0.8772,0.6819,0.7242)),
                     ('ABB3-LM',(0.4611,0.6991,0.6228,0.6026,0.9211)),('ESMFold',(0.4362,0.7643,0.5768,0.6075,1.1243))]:
        w.writerow(['published (Bimagrumab-ACVR2B.csv, native reference)',pred,'native']+list(row)+['released positive-control values, retained separately'])
    w.writerow(['executed (this run)', 'AlphaFold2-Multimer v3 (Boltzmann ColabFold)', 'native reference']+[f'{REF_RMSD[k]:.4f}' for k in ['HCDR1','HCDR2','HCDR3','HCDR123','Fv_whole']]+['same predictor/alignment/regions as all executed candidates'])
    for scope in ['HCDR3','HCDR123']:
        for x in built[scope]:
            if x['rmsd'] is None:
                w.writerow(['executed (this run)','AlphaFold2-Multimer v3',f'{scope} candidate {x["id"]}','']*4+['','structure prediction incomplete (submission unknown-state)'])
                continue
            r=x['rmsd']
            w.writerow(['executed (this run)','AlphaFold2-Multimer v3',f'{scope} candidate {x["id"]}']+[f"{r[k]:.4f}" for k in ['HCDR1','HCDR2','HCDR3','HCDR123','Fv_whole']]+[f'structrank {x["structrank"]}'])

print("bundle files written to",OUT)
for fn in sorted(os.listdir(OUT)): print(" ",fn)

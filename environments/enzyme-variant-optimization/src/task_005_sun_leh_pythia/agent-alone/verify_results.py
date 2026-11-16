"""Artifact-only independent numerical and exhaustive-grid QA; never runs a model."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import csv, hashlib, json, math, sys
import numpy as np
from selection import select

ARM=Path(__file__).resolve().parent
ALPHABET='ACDEFGHIKLMNPQRSTVWY'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(p,v):
    p.write_text(json.dumps(v,indent=2)+'\n')

def table(p,rows,fields=None):
    if fields is None:
        fields=list(rows[0])
    with p.open('w') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(rows)

def check(condition,message):
    if not condition:
        raise ValueError(message)

def main():
    m=json.loads((ARM/'INPUT_MANIFEST.json').read_text())
    native=m['identity']['sequence']
    modelmaps={v['context']:v['rows'] for v in json.loads((ARM/'inputs/upstream_model_map.json').read_text())}
    for rec in json.loads((ARM/'EXECUTION_FREEZE.json').read_text())['files']+m['immutable_files']+m['checkpoints']+m['structure']['contexts']:
        check(sha(rec['path'])==rec['sha256'],'Frozen input/code hash mismatch '+rec['path'])
    jobs=json.loads((ARM/'jobs.json').read_text())
    check(len(jobs['scientific_attempts'])>=1,'Missing scientific-attempt record')
    job=jobs['scientific_attempts'][-1]
    check(all(v['status']=='failed' and not v['model_forward_passes'] for v in jobs['scientific_attempts'][:-1]),'Unreconciled prior scientific attempt')
    check(job['status'] in ['completed_inference_pending_independent_QA','completed_and_QA_verified'],'Inference is not completed')
    check(len(job['model_forward_passes'])==4,'Expected full two-model passes in two frozen contexts')
    identities=json.loads((ARM/'results/model_identity.json').read_text())
    check(len(identities['models'])==2,'Missing model identity')
    for record in identities['models']:
        check(not record['training_mode'] and record['parameter_device']=='cpu' and record['strict_state_dict_load'],'Model not verified eval/CPU/strict')
    summaries=[]
    total=0
    for ctx in m['structure']['contexts']:
        dest=ARM/'results'/ctx['id']
        with (dest/'all_scores.csv').open() as f:
            rawrows=list(csv.DictReader(f))
        rows=[]
        for r in rawrows:
            for key in ['position','model_index_1based']:
                r[key]=int(r[key])
            for key in ['score_C','score_P','log_ratio_C','log_ratio_P','score_sum','score_mean']:
                r[key]=float(r[key])
                check(math.isfinite(r[key]),'Nonfinite score')
            check(r['wildtype']==native[r['position']-1],'Native sequence mismatch')
            check(r['mutant']!=r['wildtype'] and r['mutant'] in ALPHABET,'Illegal or self mutation in eligible table')
            rows.append(r)
        expected={(v['chain'],v['position'],a) for v in modelmaps[ctx['id']] for a in ALPHABET if a!=v['wildtype']}
        keys=[(r['chain'],r['position'],r['mutant']) for r in rows]
        check(len(keys)==len(set(keys)) and set(keys)==expected,'Incomplete, duplicate or excess substitution grid')
        check(len(rows)==ctx['eligible_nonself_substitutions'],'Row count mismatch')
        counts=Counter((r['chain'],r['position']) for r in rows)
        check(set(counts.values())=={19} and len(counts)==ctx['residues'],'Not exactly19 nonself mutations per position')
        data=np.load(dest/'raw_inference.npz',allow_pickle=False)
        wt=data['wt_indices']
        check(len(wt)==ctx['residues'],'Raw tensor length mismatch')
        check(np.isfinite(data['node']).all() and np.isfinite(data['edge']).all(),'Nonfinite inputs')
        errors={}
        for label in ['C','P']:
            logits=data['logits_'+label].astype(np.float64)
            prob=data['probabilities_'+label]
            energy=data['negative_logratio_'+label]
            check(logits.shape==(ctx['residues'],21),'Wrong full model output shape')
            check(np.isfinite(logits).all() and np.isfinite(prob).all() and np.isfinite(energy).all(),'Nonfinite raw model output')
            check(np.all(prob>0) and np.all(prob<=1),'Invalid model probability')
            check(np.allclose(prob.sum(-1),1,atol=1e-6,rtol=0),'Probability normalization failure')
            oracle=logits[np.arange(len(wt)),wt,None]-logits
            max_error=float(np.max(np.abs(oracle-energy)))
            check(max_error<2e-5,'Native energy does not agree with independent logit-difference formula')
            check(np.all(energy[np.arange(len(wt)),wt]==0),'Self substitution not exactlyzero')
            errors['max_abs_logit_difference_vs_native_score_'+label]=max_error
        recomputed=data['negative_logratio_C'].astype(np.float64)+data['negative_logratio_P'].astype(np.float64)
        check(np.array_equal(data['score_sum'],recomputed),'Raw ensemble not exact component sum')
        check(np.array_equal(data['score_mean'],recomputed/2),'Raw mean not exact half-sum')
        for row in rows:
            i=row['model_index_1based']-1
            j=ALPHABET.index(row['mutant'])
            source=modelmaps[ctx['id']][i]
            check((source['chain'],source['position'],source['wildtype'])==(row['chain'],row['position'],row['wildtype']),'Index mapping mismatch')
            for label in ['C','P']:
                check(row['score_'+label]==float(data['negative_logratio_'+label][i,j]),'Component CSV mismatch')
                check(row['log_ratio_'+label]==-row['score_'+label],'SI-sign audit mismatch')
            check(row['score_sum']==float(recomputed[i,j]) and row['score_mean']==float(recomputed[i,j]/2),'Ensemble CSV mismatch')
        upstream=(dest/'upstream_equivalent_pred_mask.txt').read_text().splitlines()
        check(len(upstream)==ctx['residues']*20,'Native-format output coverage mismatch')
        for k,line in enumerate(upstream):
            token,score=line.split()
            i,j=divmod(k,20)
            source=modelmaps[ctx['id']][i]
            check(token==f"{source['wildtype']}{i+1}{ALPHABET[j]}" and float(score)==float(recomputed[i,j]),'Native-format mapping/score mismatch')
        ranked=sorted(rows,key=lambda r:(r['score_sum'],r['chain'],r['position'],r['mutant']))
        table(dest/'all_scores_ranked.csv',[{'rank':i+1,**r} for i,r in enumerate(ranked)])
        best,_=select(rows,'score_sum',-2)
        table(dest/'best_per_position.csv',[{'rank':i+1,**r} for i,r in enumerate(best)])
        selections={}
        seqrows=[]
        for scale in ['sum','mean']:
            for cutoff in [-2,-3]:
                _,selected=select(rows,'score_'+scale,cutoff)
                name=f'selected_{scale}_lt_minus{-cutoff}'
                selectedrows=[{'rank':i+1,**r} for i,r in enumerate(selected)]
                table(dest/(name+'.csv'),selectedrows,fields=['rank']+list(rows[0]))
                selections[name]={'rows':len(selected),'by_chain':dict(Counter(r['chain'] for r in selected))}
                for i,r in enumerate(selected):
                    pos=r['position']
                    seq=native[:pos-1]+r['mutant']+native[pos:]
                    check(len(seq)==149 and sum(a!=b for a,b in zip(seq,native))==1,'Full mutant sequence reconstruction mismatch')
                    seqrows.append({'selection_rule':name,'rank':i+1,'context':ctx['id'],'chain':r['chain'],
                                    'mutation':r['mutation'],'score_sum':r['score_sum'],'score_mean':r['score_mean'],
                                    'native_parent_length':149,'mutant_sequence':seq,
                                    'interpretation':'computational point mutant; not a measured thermostability result'})
        table(dest/'selected_mutant_sequences.csv',seqrows,fields=['selection_rule','rank','context','chain','mutation','score_sum','score_mean','native_parent_length','mutant_sequence','interpretation'])
        p57=[]
        for r in rows:
            if r['mutation']=='P57A':
                chainbest=sorted([v for v in best if v['chain']==r['chain']],key=lambda v:(v['score_sum'],v['position'],v['mutant']))
                p57.append({'chain':r['chain'],'score_C':r['score_C'],'score_P':r['score_P'],
                            'score_sum':r['score_sum'],'score_mean':r['score_mean'],
                            'best_substitution_at_57':next(v['mutant'] for v in best if v['chain']==r['chain'] and v['position']==57),
                            'rank_among_best_per_position':next((i+1 for i,v in enumerate(chainbest) if v['mutation']=='P57A'),None),
                            'selected_native_sum_lt_minus2':r['score_sum']< -2 and any(v['mutation']=='P57A' and v['chain']==r['chain'] for v in best),
                            'selected_paper_mean_lt_minus2':r['score_mean']< -2 and any(v['mutation']=='P57A' and v['chain']==r['chain'] for v in best),
                            'paper_deltaTm_reference_C':8.8,'paper_reference_not_new_measurement':True})
        summaries.append({'context':ctx['id'],'eligible_positions':ctx['residues'],'nonself_rows':len(rows),
                          'full_grid_verified':True,'numerical_errors':errors,'selection_counts':selections,'P57A':p57})
        total+=len(rows)
    with (ARM/'results/all_contexts_all_scores.csv').open() as f:
        combined=list(csv.DictReader(f))
    check(len(combined)==total,'Combined table count mismatch')
    combined_keys={(r['context'],r['chain'],int(r['position']),r['mutant']) for r in combined}
    check(len(combined_keys)==total,'Combined table not one-to-one')
    reference=[{'metric':'Pythia selected point mutations','value':35,'units':'mutants','kind':'Sun published reference'},
        {'metric':'Solubly expressed mutants','value':31,'units':'mutants','kind':'Sun published reference'},
        {'metric':'Mutants with positive deltaTm','value':17,'units':'mutants','kind':'Sun published reference'},
        {'metric':'Median deltaTm of expressed Pythia library','value':0.80,'units':'Celsius degrees','kind':'Sun published reference'},
        {'metric':'P57A deltaTm','value':8.8,'units':'Celsius degrees','kind':'Sun published reference'},
        {'metric':'Pythia LEH Spearman rho all data','value':0.320,'units':'dimensionless','kind':'Sun SI TableS5 reference, not reproduced'},
        {'metric':'Pythia LEH Spearman rho self-predicted removed','value':0.470,'units':'dimensionless','kind':'Sun SI TableS5 reference, not reproduced'}]
    table(ARM/'results/paper_reference_measurements.csv',reference)
    qa={'verified_utc':datetime.now(timezone.utc).isoformat(),'all_passed':True,
        'verification_scope':'Independent artifact/coverage/numerical consistency QA, NOT independent biological validation',
        'native_sequence_length':149,'total_nonself_context_specific_rows':total,'contexts':summaries,
        'new_model_calls_by_verifier':0,'accuracy':{'measured':False,'reason':'Exact Sun mutation-linked numeric reference table unavailable; no inferred bar-height measurements'},
        'exact_Sun_numerical_reproduction':False,'exact_Sun_structure_input':'unpublished/unknown',
        'unsupported_claims_not_made':['new experimental deltaTm','independently validated improvement','AlphaFold rerun','blind discovery','predictor score is kcal/mol']}
    dump(ARM/'verification.json',qa)
    job['status']='completed_and_QA_verified'
    job['artifact_QA_utc']=qa['verified_utc']
    dump(ARM/'jobs.json',jobs)
    state=json.loads((ARM/'stage_evidence.json').read_text())
    state.update(status='computational_method_reproduction_completed',artifact_QA='passed',
                 full_scan='completed_actual_model_inference_and_full_grid_verified',
                 exact_numerical_reproduction=False,paper_structure_identity='unknown_original; supplied matched native WT reference',
                 results=summaries)
    dump(ARM/'stage_evidence.json',state)
    inventory=[]
    for p in sorted((ARM/'results').rglob('*')):
        if p.is_file():
            inventory.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
    dump(ARM/'result_artifact_inventory.json',inventory)
    print(json.dumps({'QA':'passed','context_specific_nonself_rows':total,'contexts':summaries},indent=2))

if __name__=='__main__':
    main()

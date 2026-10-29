#!/usr/bin/env python3
"""Import a small, hash-verified recorded KRAS assessment; no scientific execution.

Both source roots must be explicitly supplied and remain read-only. No checkpoints,
transcriptome indices, raw papers, credentials or third-party implementation copied.
"""
from pathlib import Path
import argparse,csv,json,shutil
from technical_reporting import sha,load,read_csv,keyed


def csvout(path, rows):
    if not rows: raise ValueError('Cannot import an empty evidence cohort')
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--assessment-root',type=Path,required=True);p.add_argument('--prior-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    current=a.assessment_root.resolve();prior=a.prior_root.resolve();out=a.out.resolve()
    if out.exists() or out.is_relative_to(current) or out.is_relative_to(prior):raise ValueError('Use a new destination outside original sources')
    current_seal=load(current/'final_assessment_manifest.json');prior_seal=load(prior/'final_execution_manifest.json');sources=[]
    def checked(root,seal,name):
        f=root/name;expected=seal['files'][name]['sha256']
        if sha(f)!=expected:raise ValueError('Source hash mismatch: '+str(f))
        sources.append({'original_path':str(f),'sha256':expected,'bytes':f.stat().st_size});return f
    candidate_path=checked(current,current_seal,'candidates.csv');candidates=read_csv(candidate_path);ids=set(keyed(candidates))
    native_path=checked(current,current_seal,'native_outputs/final_ranked_candidates.csv');native=keyed(read_csv(native_path))
    gates_path=checked(current,current_seal,'native_outputs/09_filter_decisions.csv')
    ann_path=checked(prior,prior_seal,'final_filtered_sequences.csv');annotations=keyed(read_csv(ann_path))
    previous_path=checked(prior,prior_seal,'bench_batches/batch_1/outputs/final_ranked_candidates.csv');previous=keyed(read_csv(previous_path))
    if len(ids)!=14 or ids!=set(native) or not ids<=set(previous) or ids!=set(annotations):raise ValueError('Expected exact recorded14-candidate cohort')
    specs=load(checked(prior,prior_seal,'reference_specifications.json'));refs=[]
    for spec in specs:
        accession=spec['accession_version'];f=checked(prior,prior_seal,'references/'+accession+'.fasta');lines=f.read_text().splitlines()
        if not lines or not lines[0].startswith('>'+accession+' '):raise ValueError('Exact source FASTA accession required')
        sequence=''.join(lines[1:])
        if not sequence or set(sequence)-set('ACGT'):raise ValueError('Source DNA alphabet invalid')
        refs.append({'transcript_id':accession,'gene':'KRAS','organism':spec['organism'],'orientation':'transcript_sense_5to3','alphabet':'DNA','sequence':sequence,'original_header':lines[0][1:],'original_fasta_sha256':sha(f),'source_URL':spec['source_URL'],'source_retrieved_utc':spec['retrieved_utc'],'CDS_start_1based':spec['CDS_start_1based'],'CDS_end_1based_inclusive':spec['CDS_end_1based_inclusive']})
    provenance=load(checked(current,current_seal,'native_outputs/provenance.json'));previous_request=load(checked(prior,prior_seal,'bench_batches/batch_1/request.json'))
    source_job=provenance['job_id'];earlier_job=Path(previous_request['job']).name
    if source_job==earlier_job:raise ValueError('Cannot use same job as its own reproducibility evidence')
    out.mkdir(parents=True);(out/'inputs').mkdir();(out/'native').mkdir()
    shutil.copy2(candidate_path,out/'inputs/candidates.csv');shutil.copy2(native_path,out/'native/final_ranked_candidates.csv');shutil.copy2(gates_path,out/'native/09_filter_decisions.csv')
    shutil.copy2(current/'native_outputs/provenance.json',out/'native/provenance.json')
    csvout(out/'inputs/earlier_results_selected14.csv',[previous[r['candidate_id']] for r in candidates])
    csvout(out/'inputs/supplemental_annotations.csv',[annotations[r['candidate_id']] for r in candidates])
    (out/'inputs/references.json').write_text(json.dumps(refs,indent=2)+'\n')
    mapping={'references':'inputs/references.json','candidates':'inputs/candidates.csv','bench_results':'native/final_ranked_candidates.csv','bench_gates':'native/09_filter_decisions.csv','reproducibility_results':'inputs/earlier_results_selected14.csv','supplemental_annotations':'inputs/supplemental_annotations.csv'}
    bundle={'schema_version':1,'experiment_id':'KRAS_shared_comparative_case_study','target_gene':'KRAS','evidence_origin':'RECORDED_LOCAL_SIRNA_BENCH_RUN','source_job':source_job,'reproducibility_source_job':earlier_job,'primary_reference':'NM_004985.5','coverage_references':[r['transcript_id'] for r in refs],'strand_orientation':'guide_and_passenger_5to3','allow_DNA_reference_comparison':True,'inputs':{k:{'path':name,'sha256':sha(out/name)} for k,name in mapping.items()},'reference_scope':'Four exact human RefSeq transcript versions; no full GENCODE transcriptome copied','known_limitations':['Native POTS percentile-direction limitation retained','Native raw passed booleans with missing evidence are preserved','Passenger annotations are recorded supporting evidence, not a fresh Bench passenger model','No measured endpoint or biological acceptance inferred']}
    (out/'bundle.json').write_text(json.dumps(bundle,indent=2)+'\n')
    origins={'source_files':sources,'source_assessment_manifest_sha256':sha(current/'final_assessment_manifest.json'),'source_prior_manifest_sha256':sha(prior/'final_execution_manifest.json'),'copies':'candidates and native outputs copied byte-identically; reference JSON and earlier/supplemental selected14 CSVs are explicit derived views','derivations':{'references':'Original DNA-letter sequences and accession/source metadata preserved from the four original single-record FASTAs; explicit RNA comparison only during reporting','earlier_results':'Rows selected by exact14 candidate IDs from earlier100-candidate output; field values unchanged','supplemental_annotations':'Exact14 rows from prior filtered panel; values unchanged'},'new_generation_inference_folding_screening_runs':0}
    (out/'source_provenance.json').write_text(json.dumps(origins,indent=2)+'\n')
    for item in sources:
        if sha(Path(item['original_path']))!=item['sha256']:raise ValueError('Original source changed during import')
    manifest={'schema_version':1,'scope':'Small recorded technical-assessment snapshot; not a scientific-backend installation','files':[{'path':x.relative_to(out).as_posix(),'sha256':sha(x),'bytes':x.stat().st_size} for x in sorted(out.rglob('*')) if x.is_file()]}
    (out/'snapshot_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'IMPORTED_VERIFIED_RECORDED_EVIDENCE','candidate_count':len(ids),'source_files_rechecked':len(sources),'files_in_snapshot':len(manifest['files']),'output':str(out),'new_scientific_jobs':0},indent=2))

if __name__=='__main__':main()

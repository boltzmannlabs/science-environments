"""Freeze retrieved native LEH inputs and the complete CPU scientific protocol."""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, shutil, sys
from datetime import datetime, timezone
from Bio.Data.IUPACData import protein_letters_3to1

ARM = Path(__file__).resolve().parent
ROOT = ARM.parents[1]
SRC = ROOT/'shared_sources/Pythia-e1943402092295ae96cde0c93073ddc933ffc433'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(p, value):
    p.write_text(json.dumps(value, indent=2)+'\n')

def main():
    if (ARM/'INPUT_MANIFEST.json').exists():
        raise RuntimeError('Inputs already frozen; do not overwrite')
    inp = ARM/'inputs'
    inp.mkdir()
    vendor = ARM/'vendor/pythia'
    vendor.mkdir(parents=True)
    for p in (SRC/'pythia').glob('*.py'):
        shutil.copyfile(p, vendor/p.name)
    shutil.copyfile(SRC/'LICENSE', ARM/'vendor/LICENSE')
    seq = ''.join((ARM/'sources/Q9ZAG3.fasta').read_text().splitlines()[1:])
    raw = (ARM/'sources/1NWW.pdb').read_text().splitlines(keepends=True)
    seqres = defaultdict(list)
    residues = defaultdict(list)
    for line in raw:
        if line.startswith('SEQRES'):
            seqres[line[11]].extend(line[19:70].split())
        if line.startswith('ATOM'):
            residues[(line[21], int(line[22:26]), line[26])].append(line)
    aa = lambda res: protein_letters_3to1[res.title()]
    for chain in ['A','B']:
        deposited = ''.join(aa(x) for x in seqres[chain])
        if deposited != seq or len(seq) != 149:
            raise ValueError('Native UniProt and deposited full sequence disagree')
    if seq[56] != 'P':
        raise ValueError('Paper P57 wildtype identity mismatch')
    maps, chosen, alt_decisions = [], {}, []
    for key, lines in residues.items():
        chain, pos, icode = key
        if icode.strip() or aa(lines[0][17:20]) != seq[pos-1]:
            raise ValueError(f'Unexpected coordinate mapping {key}')
        alt_ids = sorted(set(l[16] for l in lines) - {' '})
        alt = None
        if alt_ids:
            scores = {a: sum(float(l[54:60]) for l in lines if l[16] == a) for a in alt_ids}
            alt = sorted(alt_ids, key=lambda a: (-scores[a], a))[0]
            alt_decisions.append({'chain':chain,'position':pos,'occupancy_sums':scores,'selected':alt,
                                  'rule':'maximum summed residue-conformer occupancy; alphabetic tie break; shared blank atoms retained'})
        retained = [l for l in lines if l[16] == ' ' or l[16] == alt]
        if alt:
            retained = [l[:16]+' '+l[17:] for l in retained]
        names = [l[12:16].strip() for l in retained]
        if len(names) != len(set(names)) or not set(['N','CA','C','O']) <= set(names):
            raise ValueError(f'Duplicate atoms or incomplete backbone {key}')
        chosen[key] = retained
    for chain in ['A','B']:
        model_index = 0
        for pos in range(1,len(seq)+1):
            present = (chain,pos,' ') in chosen
            if present:
                model_index += 1
            maps.append({'chain':chain,'position':pos,'insertion_code':'','wildtype':seq[pos-1],
                         'model_index_mononer_1based':model_index if present else '',
                         'eligible':present,'exclusion':'' if present else 'no_coordinates_unresolved_N_terminus'})
    fields = list(maps[0])
    with (inp/'residue_map.csv').open('w') as f:
        w=csv.DictWriter(f,fields);w.writeheader();w.writerows(maps)
    (inp/'LEH_native_149.fasta').write_text('>LEH_Rhodococcus_erythropolis_DCL14_native_Q9ZAG3_149_no_added_tags\n'+seq+'\n')
    contexts = []
    for name, chains, role in [('1NWW_A',['A'],'primary_matched_monomer'),
                               ('1NWW_AB',['A','B'],'secondary_complete_dimer_context_sensitivity')]:
        body = []
        for chain in chains:
            for key in sorted(chosen):
                if key[0] == chain:
                    body.extend(chosen[key])
            body.append('TER\n')
        body.append('END\n')
        path=inp/(name+'.pdb')
        path.write_text(''.join(body))
        eligible=[m for m in maps if m['chain'] in chains and m['eligible']]
        contexts.append({'id':name,'path':str(path),'sha256':sha(path),'role':role,
                         'chains':chains,'residues':len(eligible),'eligible_nonself_substitutions':19*len(eligible),
                         'chain_specific_predictions_not_simultaneous_homodimer_mutations':True})
    checkpoint_records=[]
    for name in ['pythia-c.pt','pythia-p.pt']:
        p=SRC/'pythia'/name
        checkpoint_records.append({'name':name,'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
    immutable = [ARM/'sources/1NWW.pdb',ARM/'sources/Q9ZAG3.fasta',ARM/'sources/leh_fresco_primary.xml',
        ROOT/'shared_sources/sun_xml.xml',ROOT/'shared_sources/mmc1.pdf',ROOT/'shared_sources/sun_si.txt',
        ROOT/'shared_sources/Pythia-e1943402092295ae96cde0c93073ddc933ffc433.tar.gz',
        inp/'LEH_native_149.fasta',inp/'residue_map.csv',ARM/'selection.py']
    immutable.extend(vendor.glob('*.py'))
    dump(ARM/'INPUT_MANIFEST.json',{
        'frozen_utc':datetime.now(timezone.utc).isoformat(),
        'identity':{'enzyme':'limonene-1,2-epoxide hydrolase','organism':'Rhodococcus erythropolis DCL14',
                    'UniProt':'Q9ZAG3','gene':'limA','background':'native wildtype; no stabilizing mutations supplied or invented',
                    'sequence':seq,'length':len(seq),'sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),
                    'construct':'149-residue native modeling target; not a reconstructed tagged expression construct',
                    'evidence':'Sun names WT LEH and organism; 1NWW SOURCE DCL14, SEQRES equals UniProt native target; Sun-cited Wijma 2014 explicitly uses 1NWW',
                    'expression_tag_sequence':'not reported in Sun; not appended, inferred or modeled'},
        'structure':{'source':'RCSB deposited experimental 1NWW, unmutated, 1.20 Angstrom',
                     'stage_status':'supplied experimentally determined structure, no new folding',
                     'original_Sun_coordinate_identity':'unpublished/unknown; matched method reproduction, NOT exact numerical reproduction',
                     'primary_choice':'chain A monomer, deterministic chain choice frozen before inference, not selected to match paper outcomes',
                     'secondary_choice':'same deposited A+B structure to quantify unspecified oligomer context; no primary switch based on results',
                     'missing_positions':{'A':[1,2,3,4],'B':[1,2,3]},
                     'processing':'protein ATOM only, coherent occupancy-max residue conformer, retain coordinates/residue numbers; no optimization, relaxation or terminal rebuilding',
                     'alternate_conformers':alt_decisions,'CB_policy':'upstream uses observed CB or its own virtual-CB formula when absent',
                     'pLDDT_filter':None,'B_factors':'crystallographic displacement parameters, not pLDDT',
                     'contexts':contexts},
        'code':{'commit':'e1943402092295ae96cde0c93073ddc933ffc433','upstream':str(SRC),
                'execution_copy':str(vendor),'copy_policy':'exact unchanged Python source bytes; shared source remains read-only'},
        'checkpoints':checkpoint_records,
        'scoring':{'model_component':'S_m = -ln(p_m(mutant | masked local structure)/p_m(WT | same structure))',
                   'code_native_sum':'S_C + S_P; dimensionless, negative is putatively stabilizing',
                   'paper_wording_mean':'(S_C + S_P)/2; explicit scale sensitivity, not outcome-fit',
                   'SI_equation_sign':'SI M&M section 2 prints log(mutant)-log(WT), opposite sign to current scanner; retain log_ratio per model as -S_m',
                   'selection':'best (lowest) nonself substitution per eligible position, then strict score < -2; no visual/MD filtering or arbitrary library cap',
                   'primary_selection':'code_native_sum < -2; separate paper_wording_mean < -2 table',
                   'sensitivity_cutoffs':[-2,-3], 'tie_break':'mutant alphabetic, then chain and native position for rank ties',
                   'physical_units':None,'temperature_or_energy_conversion':False},
        'eligible_policy':'all 19 canonical non-WT amino acids at every complete-backbone resolved position; no catalytic/ligand-distance exclusions imported from FRESCO',
        'outcome_exposure':'Retrospective: primary/SI outcomes were read before inference. Not blind discovery.',
        'benchmark_protocol':{'paper_references':'35 selected, 31 soluble, 17 positive deltaTm, median deltaTm 0.80 C, P57A +8.8 C; reference measurements only',
                              'raw_reference_table':'No machine-readable Sun LEH score/deltaTm table located in pinned repository, article, SI or listed Zenodo files; do not invent values or estimate bar heights as exact measurements',
                              'applicable_comparisons':'selection counts per frozen scale/context; P57A identity, rank and selection; direct paper mutation-set overlap only if sourced set obtained; correlation not measured without exact mutation-linked numeric measurements'},
        'immutable_files':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in immutable]
    })
    interpreter=ARM/'.venv/bin/python'
    dump(ARM/'RUN_PLAN.json',{
        'frozen_utc':datetime.now(timezone.utc).isoformat(),'task':'task_001_sun_leh','approach':'agent-alone',
        'status_at_freeze':'inputs_frozen_inference_not_started','scientific_pilot_runs':False,
        'input_manifest_sha256':sha(ARM/'INPUT_MANIFEST.json'),
        'execution':'native SCI terminal, unchanged upstream feature/model implementation with audit wrapper; no delegation',
        'dependency_command':'uv venv --python ${PYTHON311_EXECUTABLE:-python3.11} .venv; uv pip install --python .venv/bin/python -r requirements-arm.txt',
        'commands':[str(interpreter)+' freeze_check.py',str(interpreter)+' run_full_scan.py',str(interpreter)+' verify_results.py'],
        'stages':['resolve native WT and supplied coordinates','freeze all input/code/model/scoring provenance',
                  'arm-only Python3.11 environment and CPU torch dependencies, capture resolved package versions',
                  'verify frozen hashes and upstream parser mapping, unit test selection without model inference',
                  'acquire shared flock; set CUDA_VISIBLE_DEVICES empty, max4 threads and 12GiB RLIMIT_AS',
                  'one local scientific process, load both published state dicts strictly, eval and no_grad; full residue batch in both predeclared contexts',
                  'retain each model logits/probabilities, component negative log ratios, native sum, explicit mean and native 20AA scanner-equivalent txt',
                  'verify complete 19AA nonself grid, self zeros, native numbering and finite values; independently recompute scores from raw logits',
                  'derive ranked full scan, 1 best per position and strict -2/-3 libraries for each frozen scale/context; emit full mutant sequences',
                  'paper reference comparison, artifact hashes, usage/runtime/errors/permissions/stage evidence and final report'],
        'resource_limits':{'threads':4,'CUDA_VISIBLE_DEVICES':'','RLIMIT_AS_bytes':12884901888,
                            'lock':str(ROOT/'shared_sources/CPU_MODEL_SLOT.lock'),
                            'lock_policy':'open existing shared flock for coordination only; do not change shared source bytes'},
        'architecture':{'embed_dim':128,'edge_dim':27,'node_dim':28,'dropout':0.2,'layer_nums':3,'token_num':21,'n_heads':8,'neighbor_num':32},
        'inference':{'device':'cpu','dtype':'float32','eval':True,'no_grad':True,'noise_level':0.0,'seed':0,'batch':'all resolved residues; no crops/subsampling'},
        'contexts':contexts,'model_forward_passes_planned':2*len(contexts),
        'output_tables':['all_scores.csv','all_scores_ranked.csv','best_per_position.csv','selected_sum_lt_minus2.csv',
                         'selected_mean_lt_minus2.csv','selected_sum_lt_minus3.csv','selected_mean_lt_minus3.csv','selected_mutant_sequences.csv'],
        'stop_and_recovery':'Preserve exact errors/attempt IDs. No missing model or sequence truncation. Correct diagnostics-grounded compatibility problems only; do not duplicate a running attempt. If identity mismatch, halt before inference.',
        'completion_boundary':'Exhaustive computational method reproduction under frozen supplied structure; exact Sun numerical and experimental replication not established.'
    })
    with (ARM/'decisions.md').open('a') as f:
        f.write('\n- Native 149-aa WT is established by mutually identical UniProt and 1NWW SEQRES plus Sun organism/WT identity; tags are not reconstructed.\n- Sun coordinate file/chain and exact numeric ensemble convention are not published in inspected material. Freeze 1NWW_A primary and 1NWW_AB context sensitivity, native summed and explicit mean scales. Do not choose based on 35 reported winners.\n- Native numbering is retained: upstream positional output would otherwise label first resolved A residue I5 as I1; wrapper exports explicit author-position mapping. Missing A1-4/B1-3 remain excluded, not truncated parent sequence.\n')
    print(json.dumps({'inputs_frozen':True,'native_sequence_length':len(seq),'contexts':contexts,
                      'manifest_sha256':sha(ARM/'INPUT_MANIFEST.json'),'plan_sha256':sha(ARM/'RUN_PLAN.json')},indent=2))

if __name__=='__main__':
    main()

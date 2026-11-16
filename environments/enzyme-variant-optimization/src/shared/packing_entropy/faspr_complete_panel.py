"""Bounded FASPR replacement preparation + unchanged native PACKMAN quantity.
Original failed producer/claim/protocol remain closed and untouched.
"""
import os, pathlib
W=pathlib.Path(__file__).resolve().parent
os.environ.update(TMPDIR=str(W/'.tmp'),XDG_CACHE_HOME=str(W/'.cache'),MPLCONFIGDIR=str(W/'.cache/matplotlib'),OPENMM_CPU_THREADS='2',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='',OPENCL_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1')
import datetime, hashlib, io, json, logging, math, resource, subprocess, sys, time, traceback, warnings
from assessment_helpers import AA1, BB, backbone_view, validate_entropy_rows
from faspr_helpers import unique_pdb_serial_view
from native_warning_policy import is_known_resource_warning
P=W/'private/faspr_completion'; P.mkdir(exist_ok=True); P.chmod(0o700)
M=W/'models_faspr_completion'; M.mkdir(exist_ok=True)
START=time.monotonic()
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def dump(p,x): pathlib.Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def event(stage,**kw):
    x={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_s':time.monotonic()-START,'stage':stage,**kw}
    with (P/'events.jsonl').open('a') as f: f.write(json.dumps(x)+'\n'); f.flush()
    print(stage,kw,flush=True)

def main():
    with (P/'DISPATCH_CLAIM.json').open('x') as f: json.dump({'worker_sha256':sha(__file__),'protocol_sha256':sha(W/'PROTOCOL_FASPR.json'),'purpose':'Distinct same-quantity FASPR preparation after closed failed PDBFixer WT','utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},f,indent=2)
    import numpy as np, openmm as mm, pdbfixer
    from openmm import app, unit
    from pdbfixer import PDBFixer
    from scipy.spatial import cKDTree, ConvexHull
    from packman.entropy import PackingEntropy
    from packman.molecule import load_structure
    logging.basicConfig(filename=P/'native.log',level=logging.INFO,force=True)
    class Capture(logging.Handler):
        def __init__(self): super().__init__(logging.WARNING); self.records=[]
        def emit(self,record): self.records.append(record.getMessage())
    capture=Capture(); logging.getLogger().addHandler(capture)
    protocol=json.loads((W/'PROTOCOL_FASPR.json').read_text())
    seqver=json.loads((W/'evidence/SEQUENCE_VERIFICATION.json').read_text())
    entries={x['candidate']:x for x in seqver['panel']}; parent=next(x for x in entries.values() if x['origin']=='parent')
    template=pathlib.Path(protocol['template'])
    if sha(template)!=protocol['template_sha256'] or not seqver['all_verified']: raise ValueError('source preflight failed')
    if sha(seqver['manifest']['path'])!=seqver['manifest']['sha256']: raise ValueError('frozen manifest changed')
    executable=W/'upstream/FASPR-master/FASPR'; rotlib=executable.parent/'dun2010bbdep.bin'
    pins={'worker':{'path':str(pathlib.Path(__file__)),'sha256':sha(__file__)},'protocol':{'path':str(W/'PROTOCOL_FASPR.json'),'sha256':sha(W/'PROTOCOL_FASPR.json')},'faspr_executable':{'path':str(executable),'sha256':sha(executable)},'faspr_library':{'path':str(rotlib),'sha256':sha(rotlib)},'helper_sha256':sha(W/'assessment_helpers.py'),'serial_helper_sha256':sha(W/'faspr_helpers.py'),'python':sys.executable,'affinity':sorted(os.sched_getaffinity(0)),'PACKMAN_source_sha256':sha(sys.modules[PackingEntropy.__module__].__file__)}
    dump(P/'RUNTIME_PINS.json',{**pins,'recovery_policy_sha256':sha(W/'RECOVERY_FASPR.json'),'warning_policy_sha256':sha(W/'native_warning_policy.py')})
    recovery=json.loads((W/'RECOVERY_FASPR.json').read_text())
    if sha(W/'PROTOCOL_FASPR.json')!=recovery['base_protocol_sha256']: raise ValueError('recovery base protocol changed')
    for path,digest in json.loads((W/'private/FASPR_RECOVERY_INPUT_HASHES.json').read_text()).items():
        if sha(W/path)!=digest: raise ValueError('recovery predecessor changed')
    def check_warnings(caught,path):
        objects=[{'category':w.category.__name__,'message':str(w.message),'filename':w.filename,'lineno':w.lineno} for w in caught]
        dump(path,objects)
        if any(not is_known_resource_warning(w) for w in objects): raise ValueError('unapproved scientific/unknown Python warning; inspect retained warning objects')
    backbone,proof=backbone_view(template.read_text(),parent['sequence'],parent['sequence'],parent['sequence_sha256'])
    common=M/'common_backbone.pdb'; common.write_text(backbone); dump(M/'common_backbone_projection.json',proof)
    platform=mm.Platform.getPlatformByName('CPU'); results=[]
    for name in protocol['panel_order']:
        s=entries[name]; out=M/name; out.mkdir(exist_ok=False)
        private=P/name; private.mkdir(exist_ok=False); private.chmod(0o700)
        before=time.monotonic(); usage0=resource.getrusage(resource.RUSAGE_SELF); children0=resource.getrusage(resource.RUSAGE_CHILDREN)
        rec={'candidate':name,'sequence_sha256':s['sequence_sha256'],'status':'started','source_backbone_sha256':sha(common)}
        event('candidate_started',candidate=name)
        try:
            with warnings.catch_warnings(record=True) as ww:
                warnings.simplefilter('always'); warning_start=len(capture.records)
                if name==parent['candidate']:
                    prepared=W/recovery['reuse_WT']['path']
                    if sha(prepared)!=recovery['reuse_WT']['sha256']: raise ValueError('WT retained model changed')
                    oldobs=json.loads((W/'private/faspr'/name/'observations.json').read_text())
                    snapshot=json.loads((W/'private/faspr'/name/'prepared_native_snapshot.json').read_text())
                    if oldobs['nonbonded_heavy_pairs_below_1_angstrom'] or oldobs['existing_FASPR_atom_max_delta_angstrom']!=0: raise ValueError('WT predecessor geometry not usable')
                    model=load_structure(str(prepared),ftype='pdb')[0]; rr=list(model.get_residues())
                    if len(rr)!=483 or ''.join(AA1.get(r.get_name(),'?') for r in rr)!=s['sequence']: raise ValueError('WT recovered sequence mismatch')
                    nativeatoms=list(model.get_atoms()); registry={(a['residue'],a['name']):(a,pos) for a,pos in zip(snapshot['atoms'],snapshot['xyz_angstrom'])}
                    if len(nativeatoms)!=len(registry): raise ValueError('WT readback atom coverage mismatch')
                    maxround=0.0
                    for a in nativeatoms:
                        k=(a.get_parent().get_id(),a.get_name()); orig,position=registry[k]
                        if a.get_element()!=orig['element']: raise ValueError('WT readback element mismatch')
                        maxround=max(maxround,float(np.max(np.abs(np.asarray(a.get_location())-np.asarray(position)))))
                        if a.get_name() in BB and not np.array_equal(np.asarray(a.get_location()),np.asarray(proof['backbone_xyz'][f'{k[0]}:{k[1]}'])): raise ValueError('WT readback common backbone mismatch')
                    if maxround>0.0005000001: raise ValueError('WT PDB serialization bound exceeded')
                    check_warnings(ww,private/'loader_warning_objects.json')
                    if len(capture.records)>warning_start: raise ValueError('native logger warning')
                    event('native_PACKMAN_started',candidate=name,heavy_atoms=len(nativeatoms),reused_preparation=True)
                    packing=PackingEntropy(model.get_atoms(),chains='A',probe_size=1.4,onspherepoints=30)
                    rows=[{'position':r.get_id(),'aa':AA1[r.get_name()],'resname':r.get_name(),'entropy':float(r.get_entropy('PackingEntropy')),'packing_fraction':float(r.get_property('PackingFraction'))} for r in rr]
                    native_total=float(packing.get_total_entropy()); dump(out/'native_residue_results.json',rows)
                    total=validate_entropy_rows(rows,s['sequence'])
                    if not math.isfinite(native_total) or abs(total-native_total)>1e-8: raise ValueError('WT native total reconciliation failure')
                    check_warnings(ww,private/'all_warning_objects.json')
                    if len(capture.records)>warning_start: raise ValueError('native logger warning')
                    usage1=resource.getrusage(resource.RUSAGE_SELF)
                    summary={'candidate':name,'status':'completed','sequence_sha256':s['sequence_sha256'],'model_sha256':sha(prepared),'native_FASPR_sha256':oldobs['native_FASPR_sha256'],'native_total_entropy':native_total,'independent_sum_entropy':total,'heavy_atoms':len(nativeatoms),'residue_count':len(rows),'surface_points':len(packing.get_surafacepoints()),'elapsed_s':time.monotonic()-before,'cpu_user_s':usage1.ru_utime-usage0.ru_utime,'cpu_system_s':usage1.ru_stime-usage0.ru_stime,'peak_rss_kib':usage1.ru_maxrss,'model_path':str(prepared.relative_to(W)),'preparation_reused_not_repeated':True}
                    dump(out/'MODEL_QA.json',{**oldobs,'status':'accepted_after_exact_readback','model_sha256':sha(prepared),'readback_max_rounding_angstrom':maxround})
                    dump(private/'completed.json',summary); results.append(summary); dump(W/'PANEL_RESULTS_FASPR.partial.json',results)
                    event('candidate_completed',candidate=name,entropy=native_total,elapsed_s=summary['elapsed_s']); continue
                target=out/'target_sequence.txt'; target.write_text(s['sequence']+'\n')
                native=out/'native_FASPR.pdb'; argv=[str(executable),'-i',str(common),'-o',str(native),'-s',str(target)]
                event('FASPR_started',candidate=name)
                run=subprocess.run(argv,capture_output=True,text=True,timeout=120,cwd=W,env=os.environ.copy())
                (private/'FASPR.stdout').write_text(run.stdout); (private/'FASPR.stderr').write_text(run.stderr)
                dump(private/'FASPR_command.json',{'argv':argv,'returncode':run.returncode})
                if run.returncode!=0 or run.stderr.strip() or 'error' in run.stdout.lower() or not native.exists(): raise ValueError('native FASPR failure or absent output')
                raw=native.read_text(); serial_view,mapping=unique_pdb_serial_view(raw)
                serialized_key={(int(l[22:26]),l[12:16].strip()):np.asarray([float(l[j:j+8]) for j in (30,38,46)]) for l in serial_view.splitlines() if l.startswith('ATOM  ')}
                for key,xyz in serialized_key.items():
                    if key[1] in BB and not np.array_equal(xyz,np.asarray(proof['backbone_xyz'][f'{key[0]}:{key[1]}'])): raise ValueError('native serialized FASPR moved backbone')
                consumer=out/'unique_serial_consumer.pdb'; consumer.write_text(serial_view); dump(out/'serial_map.json',mapping)
                fixer=PDBFixer(filename=str(consumer),platform=platform)
                residues=list(fixer.topology.residues())
                if len(residues)!=483 or ''.join(AA1.get(r.name,'?') for r in residues)!=s['sequence']: raise ValueError('native FASPR sequence coverage failure')
                initial=np.asarray(fixer.positions.value_in_unit(unit.angstrom))
                initial_key={(int(a.residue.id),a.name):initial[a.index].copy() for a in fixer.topology.atoms()}
                for key,xyz in initial_key.items():
                    if float(np.max(np.abs(xyz-serialized_key[key])))>1e-10: raise ValueError('FASPR reader changed coordinates beyond unit roundoff')
                fixer.findMissingResidues(); fixer.findMissingAtoms()
                if fixer.missingResidues or any(fixer.missingAtoms.values()): raise ValueError('FASPR missing canonical nonterminal heavy atoms')
                terminal={int(r.id):v for r,v in fixer.missingTerminals.items()}
                if terminal!={483:['OXT']}: raise ValueError('unexpected terminal completion request '+repr(terminal))
                event('OXT_only_completion_started',candidate=name)
                fixer.addMissingAtoms(seed=20261113)
                xyz=np.asarray(fixer.positions.value_in_unit(unit.angstrom)); atoms=list(fixer.topology.atoms())
                if not np.isfinite(xyz).all(): raise ValueError('nonfinite prepared model')
                delta=max(float(np.max(np.abs(xyz[a.index]-initial_key[(int(a.residue.id),a.name)]))) for a in atoms if a.name!='OXT')
                if delta>1e-10: raise ValueError('OXT builder moved original FASPR atom')
                # Retain native model/graph before acceptance and before PDB serialization.
                bonds=[[a.index,b.index] for a,b in fixer.topology.bonds()]
                dump(private/'prepared_native_snapshot.json',{'atoms':[{'index':a.index,'residue':int(a.residue.id),'resname':a.residue.name,'name':a.name,'element':a.element.symbol} for a in atoms],'xyz_angstrom':xyz.tolist(),'bonds':bonds})
                adj={a.index:set() for a in atoms}
                for a,b in bonds: adj[a].add(b); adj[b].add(a)
                overlaps=[]
                for a,b in cKDTree(xyz).query_pairs(1.0):
                    near=adj[a]|{k for x in adj[a] for k in adj[x]}
                    if b not in near: overlaps.append({'a':a,'b':b,'distance_angstrom':float(np.linalg.norm(xyz[a]-xyz[b]))})
                rec.update({'native_FASPR_sha256':sha(native),'unique_serial_consumer_sha256':sha(consumer),'serial_inverse_exact':True,'existing_FASPR_atom_max_delta_angstrom':delta,'atoms':len(atoms),'nonbonded_heavy_pairs_below_1_angstrom':overlaps})
                dump(private/'observations.json',rec)
                if overlaps: raise ValueError('FASPR model has gross heavy overlap')
                expected={}
                for r in fixer.topology.residues():
                    names={a.name for a in fixer.templates[r.name].topology.atoms() if a.element.symbol!='H'}
                    if int(r.id)==483: names.add('OXT')
                    if {a.name for a in r.atoms()}!=names: raise ValueError('heavy completeness mismatch')
                    expected[int(r.id)]=names
                buf=io.StringIO(); app.PDBFile.writeFile(fixer.topology,fixer.positions,buf,keepIds=True)
                prepared=out/'packman_heavy_atoms.pdb'; prepared.write_text(buf.getvalue())
                model=load_structure(str(prepared),ftype='pdb')[0]; rr=list(model.get_residues())
                if len(rr)!=483 or ''.join(AA1.get(r.get_name(),'?') for r in rr)!=s['sequence']: raise ValueError('PACKMAN input identity mismatch')
                bbd=0.0
                for r in rr:
                    if {a.get_name() for a in r.get_atoms()}!=expected[r.get_id()]: raise ValueError('serialized atom coverage mismatch')
                    for a in r.get_atoms():
                        namea=a.get_name(); k=(r.get_id(),namea)
                        if namea in BB:
                            d=float(np.max(np.abs(np.asarray(a.get_location())-np.asarray(proof['backbone_xyz'][f'{k[0]}:{k[1]}'])))); bbd=max(bbd,d)
                        if namea!='OXT' and not np.array_equal(np.asarray(a.get_location()),serialized_key[k]): raise ValueError('serialized FASPR coordinates changed')
                    if ConvexHull([a.get_location() for a in r.get_atoms()]).volume<=0: raise ValueError('nonpositive occupied hull')
                if bbd!=0: raise ValueError('serialized common backbone changed')
                check_warnings(ww,private/'preparation_warning_objects.json')
                if len(capture.records)>warning_start: raise ValueError('preparation native logger warning')
                rec.update({'model_sha256':sha(prepared),'backbone_serialized_max_delta_angstrom':bbd,'preparation_status':'accepted'})
                dump(out/'MODEL_QA.json',rec)
                event('native_PACKMAN_started',candidate=name,heavy_atoms=len(atoms))
                packing=PackingEntropy(model.get_atoms(),chains='A',probe_size=1.4,onspherepoints=30)
                rows=[{'position':r.get_id(),'aa':AA1[r.get_name()],'resname':r.get_name(),'entropy':float(r.get_entropy('PackingEntropy')),'packing_fraction':float(r.get_property('PackingFraction'))} for r in rr]
                native_total=float(packing.get_total_entropy()); rec['native_total_entropy']=native_total
                dump(out/'native_residue_results.json',rows); dump(private/'observations.json',rec)
                total=validate_entropy_rows(rows,s['sequence'])
                if not math.isfinite(native_total) or abs(total-native_total)>1e-8: raise ValueError('native total reconciliation failure')
                check_warnings(ww,private/'all_warning_objects.json')
                if len(capture.records)>warning_start: raise ValueError('PACKMAN native logger warning')
                usage1=resource.getrusage(resource.RUSAGE_SELF); children1=resource.getrusage(resource.RUSAGE_CHILDREN)
                summary={'candidate':name,'status':'completed','sequence_sha256':s['sequence_sha256'],'model_sha256':sha(prepared),'native_FASPR_sha256':sha(native),'native_total_entropy':native_total,'independent_sum_entropy':total,'heavy_atoms':len(atoms),'residue_count':len(rows),'surface_points':len(packing.get_surafacepoints()),'elapsed_s':time.monotonic()-before,'cpu_user_s':usage1.ru_utime-usage0.ru_utime+children1.ru_utime-children0.ru_utime,'cpu_system_s':usage1.ru_stime-usage0.ru_stime+children1.ru_stime-children0.ru_stime,'peak_rss_kib':max(usage1.ru_maxrss,children1.ru_maxrss),'model_path':str(prepared.relative_to(W))}
                dump(private/'completed.json',summary); results.append(summary); dump(W/'PANEL_RESULTS_FASPR.partial.json',results)
                event('candidate_completed',candidate=name,entropy=native_total,elapsed_s=summary['elapsed_s'])
        except BaseException as exc:
            dump(private/'FAILED.json',{'candidate':name,'error':repr(exc),'traceback':traceback.format_exc(),'observations':rec,'elapsed_s':time.monotonic()-before}); event('candidate_failed',candidate=name,error=repr(exc)); raise
    for x in json.loads((W/'evidence/SOURCE_INVENTORY.json').read_text()):
        if sha(x['path'])!=x['sha256']: raise ValueError('scientific source master changed')
    final={'status':'COMPLETED','panel_count':len(results),'results':results,'protocol_sha256':sha(W/'PROTOCOL_FASPR.json'),'runtime_pins_sha256':sha(P/'RUNTIME_PINS.json'),'elapsed_s':time.monotonic()-START,'remote_scientific_jobs':0}
    dump(W/'PANEL_RESULTS_FASPR.json',final); event('panel_completed',count=len(results))

if __name__=='__main__':
    try: main()
    except BaseException as e: event('panel_failed',error=repr(e),traceback=traceback.format_exc()); raise

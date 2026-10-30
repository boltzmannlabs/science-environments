"""Executable history-first investigation CLI (run from the repository root)."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen
from tools.dissolution_history import FDA_URL, inventory, write_history
from tools.dissolution_runner import submit, poll, ingest
from evaluation.sequential_replay import benchmark as replay_benchmark

OUT=Path('data/processed')

def config(path):
    """Configuration is JSON syntax, also a valid subset of YAML."""
    return json.loads(Path(path).read_text())


def recall_fetch():
    """Fetch exact FDA recall; fail closed if API is unavailable or mismatched."""
    with urlopen(FDA_URL,timeout=12) as response:
        raw=response.read()
    obj=json.loads(raw)
    matches=obj.get('results',[])
    if len(matches)!=1: raise ValueError('ambiguous FDA recall response')
    r=matches[0]
    if r.get('recall_number')!='D-0010-2027' or r.get('event_id')!='99893' or 'DJ25134' not in r.get('code_info','') or '27241-126-02' not in r.get('product_description',''):
        raise ValueError('FDA product/lot identity mismatch')
    digest=hashlib.sha256(raw).hexdigest()
    target=Path('data/raw')/('fda-res-D-0010-2027-'+digest+'.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists(): target.write_bytes(raw)
    elif target.read_bytes()!=raw: raise ValueError('raw snapshot hash collision')
    return {'status':'verified_public_record','recall_number':r['recall_number'],'product_description':r['product_description'],
            'code_info':r['code_info'],'reason_for_recall':r['reason_for_recall'],
            'source_locator':FDA_URL,'source_path':str(target),'sha256':digest,
            'api_last_updated':obj.get('meta',{}).get('last_updated')}


def dispatch(args):
    """Return status plus artifacts and gaps, never invent experimental outcomes."""
    OUT.mkdir(parents=True,exist_ok=True)
    if args.command in ('inventory-history','import-history','solve'):
        cfg=config(args.config)
        hist=cfg['history']; kwargs={'legacy_root':hist.get('legacy_root'),'prior_gym_root':hist.get('prior_gym_root'),
                                      'additional_sources':hist.get('additional_sources',[]),'transcription_source':hist.get('transcription_source')}
        if args.command=='inventory-history':
            entries=inventory(**kwargs)
            return {'status':'success','searched':len(entries),'found':sum(e['checksum'] is not None for e in entries),
                    'unresolved':[e['path_source_id'] for e in entries if not e['checksum']],
                    'artifacts':[],'budget_usage':{'tool_calls':0}}
        if args.command=='import-history':
            result=write_history(OUT,**kwargs)
            try: result['recall']=recall_fetch()
            except (OSError,ValueError,KeyError,TimeoutError) as exc:
                result['recall']={'status':'tool_unavailable','reason':type(exc).__name__}
            if result['recall']['status']=='verified_public_record':
                with (OUT/'history_manifest.csv').open('a',newline='') as stream:
                    writer=csv.writer(stream)
                    writer.writerow([result['recall']['source_path'],result['recall']['sha256'],FDA_URL,
                        'ranolazine','Ajanta ER 1000 mg','DJ25134',None,1,'literature_reported',None,
                        'public_official_API','recall_only','no individual-unit release data or criteria'])
            result['artifacts']=[result['manifest'],result['profiles']]
            result['budget_usage']={'tool_calls':1 if result['recall']['status']=='verified_public_record' else 0}
            return result
        if args.mode=='analyze_history':
            if not (OUT/'literature_profiles.json').exists():
                write_history(OUT,**kwargs)
            rows=json.loads((OUT/'literature_profiles.json').read_text())
            result=submit('analyze_history',OUT,rows=rows)
            result['status']='insufficient_data'  # descriptive history completed; product failure not resolved
            result['missing_data']=['affected lot DJ25134 individual-unit dissolution results','approved lot-specific method and specification',
               'batch formula/process and storage records','prespecified improvement rule and budget']
            result['next_action']='request controlled historical and OOS QC records; compare units after method validation'
            result['budget_usage']={'tool_calls':0,'experiments':0}
            result['artifacts']=[str(OUT/'literature_profiles.json'),str(OUT/'history_manifest.csv')]
            (OUT/'analysis_report.json').write_text(json.dumps(result,indent=2))
            result['artifacts'].append(str(OUT/'analysis_report.json'))
            return result
        if args.mode=='predict':
            return {**submit('predict',OUT),'missing_data':['verified candidate composition','applicable validated model and method',
                    'configured numerical bounds'],'budget_usage':{'tool_calls':0},'artifacts':[]}
        return {'status':'invalid_mode','artifacts':[],'budget_usage':{}}
    if args.command=='benchmark':
        cfg=config(args.config)
        if args.track=='published':
            from evaluation.published_benchmark import run
            path=OUT/'literature_profiles.json'
            if not path.is_file():
                return {'status':'not_evaluated','reason':'import-history must be run first','artifacts':[],'budget_usage':{'tool_calls':0}}
            result=run(path,OUT/'published_benchmark')
            result['budget_usage']={'tool_calls':0,'experiments':0}
            return result
        if args.track=='replay': result=replay_benchmark()
        elif args.track=='holdout':
            result={'status':'not_evaluated','track':'holdout','reason':'no independent eligible source-linked measured ranolazine formulation groups or frozen splits'}
        else:
            from tools.dissolution_history import profile_rows, normalize
            rows=profile_rows()
            result={'status':'success','track':'fixtures','checks':{'rows_normalize':all(normalize(r)['derived_time_min']>=0 for r in rows),
                'missing_values_preserved':any(r['release_value'] is None for r in rows),
                'over_100_preserved':any(r['release_value']>100 for r in rows if r['release_value'] is not None)},
                'scientific_validation':'not_evaluated'}
        result['budget_usage']={'tool_calls':0,'experiments':0}
        target=OUT/('benchmark_'+args.track+'.json');target.write_text(json.dumps(result,indent=2))
        result['artifacts']=[str(target)]
        return result
    if args.command=='submit-dissolution':
        plan=json.loads(Path(args.plan).read_text())
        return submit('laboratory',OUT,plan=plan,authorization=args.authorization,backend=args.backend,dry_run=args.dry_run)
    if args.command=='poll-dissolution': return poll(OUT,args.run_id)
    if args.command=='ingest-dissolution': return ingest(OUT,args.run_id)
    raise ValueError('unknown command')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('inventory-history','import-history','solve'):
        p=sub.add_parser(name);p.add_argument('--config',default='configs/task.yaml')
        if name=='solve':p.add_argument('--mode',choices=['analyze_history','predict'],required=True)
    b=sub.add_parser('benchmark');b.add_argument('--config',default='configs/benchmark.yaml');b.add_argument('--track',choices=['fixtures','holdout','replay','published'],required=True)
    s=sub.add_parser('submit-dissolution');s.add_argument('--plan',required=True);s.add_argument('--authorization');s.add_argument('--backend');s.add_argument('--dry-run',action='store_true')
    for name in ('poll-dissolution','ingest-dissolution'):
        sub.add_parser(name).add_argument('--run-id',required=True)
    args=parser.parse_args()
    result=dispatch(args)
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()

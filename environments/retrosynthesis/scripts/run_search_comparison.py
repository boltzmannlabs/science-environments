#!/usr/bin/env python3
"""Run the local SRG-05 development comparison; no LLM or private labels."""
import argparse
import json
from pathlib import Path
from synthesis_route_gym.adapters import LocalRetroAdapter
from synthesis_route_gym.search_benchmark import (
    pin_localretro_assets, run_comparison, select_development_tasks,
)


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--public-bundle',type=Path,default=root/'artifacts/benchmarks/srg02-v1')
    parser.add_argument('--public-manifest-sha256',default=None)
    parser.add_argument('--repo-root',type=Path,default=root.parent)
    parser.add_argument('--chemistry-python',type=Path,default=Path(
        '/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python'))
    parser.add_argument('--groups',type=int,default=4)
    args = parser.parse_args()
    digest = args.public_manifest_sha256
    if digest is None:
        receipt = json.loads((root/'artifacts/steps/srg-02/acceptance.json').read_text())
        digest = receipt['integrity']['public_manifest_sha256']
    tasks,cohort = select_development_tasks(args.public_bundle,digest,group_count=args.groups)
    identity = pin_localretro_assets(args.repo_root,args.chemistry_python)
    report = run_comparison(args.output,tasks,backend_factory=lambda:LocalRetroAdapter(
        repo_root=args.repo_root,python_executable=args.chemistry_python,timeout_seconds=40).expand,
        backend_identity=identity,cohort=cohort)
    print(json.dumps({'output':str(args.output),'aggregate':report['aggregate'],
                      'precomputation':report['precomputation']},indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())

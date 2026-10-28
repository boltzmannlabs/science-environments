#!/usr/bin/env python3
"""Run the bounded local source-scoped experiment in a new output directory."""
import argparse
import json
from synthesis_route_gym.cn_training import train_cn_model


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',required=True)
    parser.add_argument('--dataset-sha256',required=True)
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    report = train_cn_model(args.dataset,args.output,expected_sha256=args.dataset_sha256)
    print(json.dumps({key:report[key] for key in ('scope','candidate_selected','baseline_selected',
        'development_candidate_gate_passed','disposition','final_run_authorized','runtime_seconds')},indent=2))


if __name__ == '__main__':
    main()

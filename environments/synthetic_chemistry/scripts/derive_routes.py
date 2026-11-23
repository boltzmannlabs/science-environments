#!/usr/bin/env python3
"""Derive portable route summaries from an authorized retrosynthesis JSON export.

The source stays local. The derived summary omits backend IDs, links and account
metadata. Hypothetical products of model step yields are not synthetic yields.
"""
import argparse
import json
import math
from pathlib import Path

TARGET = 'CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O'


def collect(node, output):
    for child in node.get('children', []):
        if child.get('reaction_name'):
            collect(child, output)
            output.append({
                'reaction_name': child['reaction_name'],
                'reactants': [n.get('smile') for n in child.get('children', [])],
                'product': child.get('smile'),
                'model_reaction_yield_pct': child.get('reaction_yield'),
            })
        else:
            collect(child, output)


def derive(data):
    if not isinstance(data, dict) or not data:
        raise ValueError('Expected a nonempty mapping of topN routes')
    result = {'schema_version': 1, 'target_smiles': TARGET,
              'provenance': 'Derived from an authorized Boltzmann model result; no experimental observations.',
              'routes': []}
    for key, record in sorted(data.items(), key=lambda item: int(item[0][3:])):
        if not key.startswith('top') or not key[3:].isdigit():
            raise ValueError(f'Invalid route key: {key}')
        path = record.get('path')
        if not isinstance(path, dict):
            raise ValueError(f'Missing path in {key}')
        steps = []
        collect(path, steps)
        yields = [s['model_reaction_yield_pct'] for s in steps]
        if any(not isinstance(y, (int, float)) or isinstance(y, bool) or not 0 <= y <= 100 for y in yields):
            raise ValueError(f'Invalid model reaction yield in {key}')
        result['routes'].append({
            'route': key,
            'starting_materials': record.get('starting_materials', []),
            'model_ranking_score': record.get('pathway_ranking_score'),
            'reported_num_steps': record.get('num_steps'),
            'explicit_tree_steps': len(steps),
            'steps': steps,
            'illustrative_sequential_product_pct': round(100 * math.prod(y / 100 for y in yields), 2) if steps else None,
            'experimental_validation': 'not established',
        })
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Authorized local scored-paths JSON')
    parser.add_argument('--output', required=True, type=Path, help='Derived public summary JSON')
    args = parser.parse_args()
    derived = derive(json.loads(args.input.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(derived, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"Derived {len(derived['routes'])} model routes into {args.output}")


if __name__ == '__main__':
    main()

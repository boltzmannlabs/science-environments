#!/usr/bin/env python3
"""Generate traceable comparison tables; never infer experimental superiority."""
import csv
import io
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def render():
    data = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json').read_text())
    audit = json.loads((BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/top0_validation.json').read_text())
    papers = json.loads((BASE / 'benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.json').read_text())['references']
    routes = data['routes']
    steps = audit['steps']
    total = sum(r['explicit_tree_steps'] for r in routes)
    rank1 = sum(s['forward_product_rank'] == 1 for s in steps)
    best = max(routes, key=lambda r: r['illustrative_sequential_product_pct'])
    metrics = {
        'scope': 'One target, 16 model routes; not a calibrated benchmark dataset',
        'routes_generated': len(routes),
        'reaction_node_occurrences_across_routes': total,
        'distinct_route_reaction_count_note': 'Occurrences, not deduplicated chemistry across routes',
        'routes_with_separate_stepwise_checks': 1,
        'steps_with_separate_stepwise_checks': len(steps),
        'selected_route_expected_product_rank1_count': rank1,
        'selected_route_expected_product_rank1_denominator': len(steps),
        'selected_route_expected_product_rank1_pct': round(100 * rank1 / len(steps), 2),
        'rank1_interpretation': 'Descriptive within-top0 model agreement, not accuracy or experimental success rate',
        'exact_target_literature_routes_established': 0,
        'experimental_target_syntheses_performed': 0,
        'measured_target_yield_pct': None,
        'measured_target_selectivity_pct': None,
        'matched_literature_yield_error': None,
        'best_illustrative_model_product_route': best['route'],
        'best_illustrative_model_product_pct': best['illustrative_sequential_product_pct'],
        'top0_illustrative_model_product_pct': routes[0]['illustrative_sequential_product_pct'],
        'references_in_catalog': len(papers),
        'literature_yield_for_different_substrate_pct': 32,
        'literature_superiority_demonstrated': False,
        'limitations': 'No matched experimental target results, calibrated uncertainty, measured purity/selectivity or exact-route precedent; no yield improvement or yield error can be computed.'
    }
    (BASE / 'benchmark/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    rows = [['route', 'explicit_tree_steps', 'reported_num_steps', 'model_ranking_score', 'model_step_yields_pct', 'illustrative_product_pct_NOT_observed_yield', 'measured_target_yield_pct', 'exact_target_literature_match']]
    for r in routes:
        rows.append([r['route'], r['explicit_tree_steps'], r['reported_num_steps'], r['model_ranking_score'], '; '.join(f"{s['model_reaction_yield_pct']:.2f}" for s in r['steps']), r['illustrative_sequential_product_pct'], 'not measured', 'not established'])
    stream = io.StringIO()
    csv.writer(stream, lineterminator='\n').writerows(rows)
    (BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/route_yield_comparison.csv').write_text(stream.getvalue())
    text = ['# Achieved outputs and literature comparison', '',
            'Generated from the checked-in route summary, selected-route audit and reference catalog. No new platform or laboratory runs were performed.', '',
            '## What we achieved', '',
            '| Metric | Observed/derived value | Interpretation |', '|---|---|---|',
            f'| Generated routes | {len(routes)} | Model candidates, not validated syntheses |',
            f'| Reaction-node occurrences across all routes | {total} | Includes chemistry repeated in different routes |',
            f'| Separately checked routes / steps | 1 / {len(steps)} | Only top0 |',
            f'| Expected product ranked first in top0 | {rank1}/{len(steps)} ({metrics["selected_route_expected_product_rank1_pct"]}%) | Model agreement only, not experimental accuracy |',
            '| Exact target experimental preparations performed | 0 | No laboratory result |',
            '| Exact target literature routes established | 0 | Search limitation; not proof of absence |',
            '| Measured target yield, selectivity; literature yield error | Not available | No matched comparison possible |', '',
            '## All-route numerical comparison', '',
            'The percentage product below multiplies step model yields under an illustrative sequential assumption. Branch topology, stoichiometry, purification losses and calibration are not captured. It must not be called an achieved synthetic yield.', '',
            '| Route | Explicit steps | Predicted step yields (%) | Illustrative product (%) |', '|---|---:|---|---:|']
    for r in routes:
        yy=', '.join(f"{s['model_reaction_yield_pct']:.2f}" for s in r['steps'])
        text.append(f"| {r['route']} | {r['explicit_tree_steps']} | {yy} | {r['illustrative_sequential_product_pct']:.2f} |")
    text += ['', '## Tool versus literature: selected route', '',
             '| Step | Tool output (model-only) | Literature comparator | Conclusion |', '|---|---|---|---|',
             '| 1: TBS protection | Forward score 0.999999812; mapping confidence 0.27964; condition-tool yield 81.26%; TBAF/THF, 20–30 °C | [L1](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md): protection class only; no same-substrate yield extracted | Reject fluoride condition for forming/retaining TBS ether. High score did not establish compatible conditions. |',
             '| 2: aryl ether formation | Protected product ranked last, forward score 0; mapping confidence 0.21971; condition-tool yield 77.94%; pyridine/THF, no coupling catalyst | [L2](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md): Ullmann-type diaryl-ether class only; exact pairing not established | Unresolved central step; model yield not credible evidence of feasible coupling. |',
             '| 3: deprotection | Forward score 0.999999837; mapping confidence 0.66765; condition-tool yield 62.02%; TBAF/THF, 20–30 °C | [L3](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md): TBAF/THF, 0 °C to room temperature, 45 min; 32% isolated yield for a DIFFERENT compound | Plausible class analogy only; 62.02% versus 32% is NOT a matched yield improvement. |', '',
             'The condition-tool yields above are a different prediction output from the retrosynthesis step-yield fields in the all-route table; they are not substituted into one another.', '',
             '## What was not achieved', '',
             'No matched experimental accuracy, yield improvement, selectivity improvement, purity improvement, cost advantage or calibrated uncertainty was established. Literature sources support reaction-family context rather than an exact complete route. Starting-material availability and target-route practicality remain unverified.', '',
             '## Source files', '',
             '- [All routes](route_summary.json)', '- [Selected-route tool audit](top0_validation.json)', '- [Numeric CSV](route_yield_comparison.csv)', '- [Metric definitions and values](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json)', '- [Literature catalog](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md)', '- [Existing DOCX structure report](retro_benchmark_report.docx)', '']
    rendered='\n'.join(text)
    (BASE / 'results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md').write_text(rendered)
    lines=['# Papers and public references used in the comparison', '', 'This catalog links to papers rather than redistributing publisher PDFs. Evidence access and substrate match are explicit; no complete exact-target route was established.', '', '| ID | Reference / source | Compared step | Numeric experimental evidence | Access and evidence limit |', '|---|---|---|---|---|']
    for p in papers:
        yy = str(p['experimental_yield_pct']) + '% for different substrate' if p['experimental_yield_pct'] is not None else 'Not extracted / not applicable'
        lines.append(f"| {p['id']} | [{p['title']}]({p['url']}) | {p['comparison_step']} | {yy} | {p['access']}; {p['claim_supported']} |")
    lines += ['', '## Search scope', '', 'Existing research used Crossref/OpenAlex bibliographic queries, Europe PMC and Google Patents text queries. Publisher access limits, incomplete patent screening and lack of chemical-structure search prevent exhaustive absence/novelty conclusions. P1/P2 are negative screening records, not validated route precedents.', '', 'See [machine-readable catalog](papers.json) and [results comparison](../../results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md).', '']
    (BASE / 'benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md').write_text('\n'.join(lines))
    print(f'Generated comparison tables: {len(routes)} routes, {total} reaction occurrences, {rank1}/{len(steps)} rank-1 agreements; no experimental superiority claim.')


if __name__ == '__main__':
    render()

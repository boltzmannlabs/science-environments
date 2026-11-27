"""Build GitHub-readable benchmark pages and figures from saved predictions only."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_paths import historical_result, resolve_artifact
from markdown_report import MarkdownReport


def rows(path):
    path = resolve_artifact(path)
    with path.open() as stream:
        return list(csv.DictReader(stream))


def number(value, digits=4):
    return '—' if value in (None, '') else f'{float(value):.{digits}f}'


def add_electrostatics(doc, folder, image, plt):
    path = resolve_artifact(folder / 'steps/10_reaction_electrostatics/predictions.csv')
    if not path.exists():
        return
    data = rows(path)
    labels = [('parent', 'Evaluated parent'), ('reference', 'Reference V140T'),
              ('retained_candidate', 'Our ATH_R2_09')]
    measures = [('projected_protein_field_core216', 'Projected protein field', 'MV/cm'),
                ('geometric_I_to_C_field_angle', 'Geometric I→C/field angle', 'degrees'),
                ('pre_reaction_explicit_CI_LMO_coupling_core216', 'C–I LMO/field interaction', 'kcal/mol')]
    doc.add_heading('Matched 30 ns reaction-site assessment', 1)
    doc.add_paragraph('Each sequence has one 30 ns trajectory; the first 5 ns are excluded. Field and angle summaries use 250 snapshots; explicit C–I LMO calculations use 25 snapshots per sequence. Values are mean ± sample SD.')
    lookup = {(r['display_label'], r['endpoint']): r for r in data}
    doc.table(['Observable', 'Parent', 'Reference V140T', 'Our ATH_R2_09'],
              [[f'{name} ({unit})'] +
               [f"{float(lookup[(case, endpoint)]['mean']):.2f} ± {float(lookup[(case, endpoint)]['sd']):.2f}" for case, _ in labels]
               for endpoint, name, unit in measures])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.6))
    for ax, (endpoint, name, unit) in zip(axes, measures):
        group = [lookup[(case, endpoint)] for case, _ in labels]
        ax.bar(range(3), [float(r['mean']) for r in group],
               yerr=[float(r['sd']) for r in group], capsize=4,
               color=['#73808d', '#d39528', '#246b98'])
        ax.set_xticks(range(3), ['Parent', 'V140T', 'ATH_R2_09'], rotation=20)
        ax.set_title(name, fontsize=9)
        ax.set_ylabel(unit)
        ax.grid(axis='y', alpha=.15)
    fig.tight_layout()
    image(fig, 'Matched field, geometry and interaction predictions',
          'Error bars show sample SD along a single trajectory, not independent experimental uncertainty. Only calculations from our declared 30 ns protocol share these axes.')
    doc.add_paragraph('The candidate field is less negative than the evaluated parent. Its mean interaction change is +0.177 kcal/mol; the conditional temporal-block interval [−0.124, +0.478] includes zero. This assessment does not resolve an interaction improvement. The LMO interaction is a pre-reaction coupling estimate, not an activation barrier or a measured activity.')
    doc.add_paragraph('[Protocol and sequence identities](../../../../results/task_004_athol1_substrate/run_001_20261112_181250_0bd28c/steps/10_reaction_electrostatics/README.md).')


def add_open_source_metrics(doc, folder, image, plt):
    """Render verified alternative-method results, distinct from published predictions."""
    path = resolve_artifact(folder / 'reference_comparison/open_source_metrics.csv')
    if not path.exists():
        return
    from collections import defaultdict
    groups = defaultdict(list)
    diagnostic_or_duplicate = {'Zhang_cellulase_M2_E158C', 'Zhang_beta_glucanase_M5_G74P',
                               'Zhang_reported_cellulase_WT_T131D', 'Zhang_reported_cellulase_M2_T257K'}
    for row in rows(path):
        if row.get('status', 'verified') != 'verified' or row.get('origin') == 'parent':
            continue
        if row['candidate_id'] in diagnostic_or_duplicate:
            continue
        if row['method'].startswith('DDGun') and resolve_artifact(folder / 'steps/07_ddgun_stability/predictions.csv').exists():
            continue  # The original verified DDGun table and plot already show these rows.
        groups[(row['metric'], row['method'], row['unit'], row['protocol'])].append(row)
    for (metric, method, unit, protocol), group in groups.items():
        doc.add_heading(metric + ' — open-source assessment', 1)
        doc.add_paragraph(f'Method: {method}. Units: {unit}. Protocol: {protocol}. Values below were calculated in this work for the listed sequences.', style='keep_with_next')
        show_change = all(r.get('delta_from_parent') not in (None, '') for r in group)
        headers = ['Sequence', 'Group', 'Parent / background', f'Prediction ({unit})']
        if show_change:
            headers.append(f'Change from parent ({unit})')
        values = []
        for row in group:
            value = [row['candidate_id'], 'Reported reference' if row['origin'] == 'reference' else 'Our candidate',
                     row['parent_id'], f"{float(row['value']):.6g}"]
            if show_change:
                value.append(f"{float(row['delta_from_parent']):+.6g}")
            values.append(value)
        doc.table(headers, values)
        fig, ax = plt.subplots(figsize=(11, max(2.7, .48 * len(group) + 1)))
        plot_field = 'delta_from_parent' if show_change else 'value'
        ax.barh(range(len(group)), [float(r[plot_field]) for r in group],
                color=['#d39528' if r['origin'] == 'reference' else '#246b98' for r in group])
        ax.set_yticks(range(len(group)), [r['candidate_id'].replace('Zhang_', '') for r in group])
        ax.invert_yaxis()
        ax.set_xlabel(f'{"Change from evaluated parent: " if show_change else ""}{metric} ({unit})')
        ax.grid(axis='x', alpha=.15)
        fig.tight_layout()
        image(fig, metric + ': reference and our sequences',
              'Amber: reported reference variants recalculated here. Blue: our retained candidates. All rows in this panel use the stated method and protocol.'
              + (' The plot shows changes from the evaluated parent.' if show_change else ''))


def build_task(env, task):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    tid = task['id']
    folder = historical_result(env, tid)
    doc = MarkdownReport(task['title'] + ' — benchmark report')
    table = doc.table
    source = doc.source

    doc.add_heading(task['title'] + ' — benchmark report', 0)
    doc.add_paragraph('Comparison scope: historical agent-alone candidates only. Published predictions and reference variants recalculated here are labelled separately. Specialist-assisted results are available in the results index and are not pooled into these tables.')
    run_record = env / 'runs' / tid / folder.name / 'run.json'
    model_name = json.loads(run_record.read_text())['model']
    doc.add_paragraph('Agent Scientist: ' + model_name + '. Predictor names and units are listed with each measurement.')

    if task.get('metrics'):
        doc.add_heading('Published predictions and our predictions', 1)
        table(['Property / predictor', 'Published prediction', 'Our candidates'], [r[:3] for r in task['metrics']])
        citations = {
            'task_001_rml_stability': ('Teng et al., Tables 1 and sections 3.4/3.7', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11727178/'),
            'task_002_leh_stability': ('Wijma et al., Figure 1 and methods', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3893934/'),
            'task_003_bla_high_temperature': ('Fan et al., computational screening', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10883975/'),
            'task_004_athol1_substrate': ('Shao et al., Figure 8A and electrostatic analysis', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC12288847/'),
            'task_005_sun_leh_pythia': ('Sun et al., LEH case study', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11763918/'),
            'task_006_zhang_hydrolases': ('Zhang et al., original supplementary tables S1/S3/S5/S7', 'https://doi.org/10.1016/j.ijbiomac.2024.138274'),
        }
        if tid in citations:
            source(*citations[tid])

    blue, amber = '#246b98', '#d39528'
    plt.rcParams.update({'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
    charts = 0
    with tempfile.TemporaryDirectory(prefix='enzyme_report_') as temporary:
        def image(fig, title, caption):
            nonlocal charts
            path = Path(temporary) / f'chart_{charts}.png'
            fig.savefig(path, dpi=170, bbox_inches='tight')
            plt.close(fig)
            doc.add_figure(path, title, caption)
            charts += 1

        if tid == 'task_006_zhang_hydrolases':
            agreement = resolve_artifact(env / 'benchmark' / 'evaluation' / tid / 'comparisons/published_prediction_only.csv')
            if agreement.exists():
                pairs = [dict(r, background=r['background'].replace('-', '_'),
                              method='ESM2' if r['method'] == 'ESM' else r['method'],
                              paper_score=r['published_prediction'], our_score=r['our_prediction'])
                         for r in rows(agreement)]
                example = [('cellulase_WT', 'Pythia', 'T131D'), ('cellulase_M2', 'ESM2', 'T257K'),
                           ('beta_glucanase_WT', 'Pythia', 'N65I'), ('beta_glucanase_M5', 'ESM2', 'I65Y'),
                           ('beta_glucanase_M5', 'ESM2', 'P10D')]
                examples = [r for bg, method, mutation in example for r in pairs
                            if r['background'] == bg and r['method'] == method and r['mutation'] == mutation]
                doc.add_heading('Same-variant prediction comparison', 1)
                table(['Background', 'Predictor', 'Mutation', 'Published score', 'Our score'],
                      [[r['background'], r['method'], r['mutation'], r['paper_score'], r['our_score']] for r in examples])
                stats = task.get('published_score_agreement', [])
                if isinstance(stats, list) and stats:
                    table(['Predictor / background', 'Rows', 'Mean absolute difference', 'Rank correlation'],
                          [[f"{r['method']} / {r['construct']}", r['reference_rows'], number(r['agent_alone']['MAE'], 6), number(r['agent_alone']['Spearman_rho'], 6)] for r in stats])
                groups = [('cellulase_WT', 'Pythia'), ('cellulase_M2', 'ESM2'), ('beta_glucanase_WT', 'Pythia'), ('beta_glucanase_M5', 'ESM2')]
                fig, axes = plt.subplots(1, 4, figsize=(12, 3.4))
                for ax, (background, method) in zip(axes, groups):
                    group = [r for r in pairs if r['background'] == background and r['method'] == method]
                    x = [float(r['paper_score']) for r in group]
                    y = [float(r['our_score']) for r in group]
                    if x:
                        low, high = min(x + y), max(x + y)
                        ax.plot([low, high], [low, high], '--', color='#999', linewidth=.8)
                        ax.scatter(x, y, color=blue, s=14, alpha=.7)
                    ax.set_title(method + '\n' + background.replace('_', ' '), fontsize=9)
                    ax.set_xlabel('Published score')
                    ax.set_ylabel('Our score')
                fig.tight_layout()
                image(fig, 'Published versus recalculated scores', 'Each panel compares the same variants and scoring background. Scores are unitless; the dashed line marks equal values.')

        energy_path = resolve_artifact(folder / 'steps/07_ddgun_stability/predictions.csv')
        if energy_path.exists():
            energy = [r for r in rows(energy_path) if not r['candidate'].startswith('paper-control')]
            doc.add_heading('Our stability predictions', 1)
            table(['Candidate', 'Mutations', 'DDGun unfolding ΔΔG (kcal/mol)'],
                  [[r['candidate'], r['variant'], r['value']] for r in energy])
            doc.add_paragraph('Change is relative to our selected parent. Positive DDGun unfolding ΔΔG indicates predicted stabilization; negative indicates predicted destabilization.')
            fig, ax = plt.subplots(figsize=(11, max(2.7, .5 * len(energy) + 1)))
            values = [float(r['value']) for r in energy]
            ax.barh(range(len(energy)), values, color=blue)
            ax.set_yticks(range(len(energy)), [r['candidate'] for r in energy])
            ax.invert_yaxis()
            ax.axvline(0, color='#777', linewidth=.8)
            ax.set_xlabel('Predicted unfolding ΔΔG versus selected parent (kcal/mol)')
            for i, value in enumerate(values):
                ax.annotate(f'{value:+.1f}', (value, i), xytext=(6 if value >= 0 else -6, 0), textcoords='offset points', va='center', ha='left' if value >= 0 else 'right')
            ax.margins(x=.4)
            fig.tight_layout()
            image(fig, 'Stability change from our parent', 'All bars use DDGun_SEQ and the same selected parent within this task.')

        candidates = [dict(r, origin='our') for r in task.get('candidates', [])]
        comparison_path = resolve_artifact(folder / 'reference_comparison/predictions.csv')
        if comparison_path.exists():
            # This file is an explicitly integrated, verified same-method comparison.
            candidates = rows(comparison_path)
        candidates = [r for r in candidates if r.get('origin') != 'parent']
        if tid == 'task_006_zhang_hydrolases':
            excluded = {'Zhang_cellulase_M2_E158C', 'Zhang_beta_glucanase_M5_G74P', 'Zhang_reported_cellulase_WT_T131D', 'Zhang_reported_cellulase_M2_T257K'}
            candidates = [r for r in candidates if r['candidate_id'] not in excluded]
        if candidates:
            doc.add_heading('Property predictions calculated in this work', 1)
            table(['Sequence', 'Group', 'Parent / background', 'Predicted Tm (°C)', 'ΔTm (°C)', 'NetSolP', 'pHPred (raw)'],
                  [[r['candidate_id'], 'Reference' if r.get('origin') == 'reference' else 'Our candidate' if r.get('origin') == 'our' else 'Parent',
                    r.get('parent_id', ''), number(r.get('Tm_degC')), number(r.get('delta_Tm_degC')), number(r.get('NetsolP'), 6), number(r.get('pHPred_raw'))] for r in candidates])
            plot_rows = [r for r in candidates if r.get('origin') != 'parent' and r.get('Tm_degC') not in ('', None)]
            if plot_rows:
                fig, axes = plt.subplots(1, 2, figsize=(12, max(3.2, min(5.2, .4 * len(plot_rows) + 1.5))), sharey=True)
                for i, row in enumerate(plot_rows):
                    color = amber if row.get('origin') == 'reference' else blue
                    if row.get('delta_Tm_degC') not in ('', None):
                        axes[0].barh(i, float(row['delta_Tm_degC']), color=color)
                    if row.get('NetsolP') not in ('', None):
                        axes[1].barh(i, float(row['NetsolP']), color=color)
                axes[0].set_yticks(range(len(plot_rows)), [r['candidate_id'].replace('Zhang_', '') for r in plot_rows])
                axes[0].invert_yaxis()
                axes[0].axvline(0, color='#777', linewidth=.8)
                axes[0].set_xlabel('Predicted ΔTm versus listed parent (°C)')
                axes[1].set_xlabel('NetSolP score (0–1)')
                axes[1].set_xlim(0, 1)
                for ax in axes:
                    ax.grid(axis='x', alpha=.15)
                fig.tight_layout()
                image(fig, 'Candidate and reference property predictions', 'Blue: our candidates. Amber: reference variants calculated in this work. Changes use the parents listed in the table.')
        add_open_source_metrics(doc, folder, image, plt)
        if tid == 'task_004_athol1_substrate':
            add_electrostatics(doc, folder, image, plt)
        doc.add_paragraph(f'[Results and preparation details](../../../../results/{tid}/{folder.name}/README.md) · [Published reference](../../../reference_data/{tid}/references.md).')

    target = env / 'benchmark' / 'evaluation' / tid / 'comparisons/benchmark_report.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(target)
    print(f'{tid}: {charts} linked figures; {len(doc.tables)} tables')


def build(env):
    tasks = json.loads((env / 'benchmark/reference_data/report_data.json').read_text())['tasks']
    for task in tasks:
        if task.get('executed'):
            build_task(env, task)
    index = ['# Benchmark comparisons', '', 'These six comparison reports use historical agent-alone runs only. Specialist-assisted runs have separate result records; they are not pooled into the benchmark tables. Each task report contains published predictions, method-labeled comparisons and embedded figures. Open-source recalculations score reported reference variants and our retained candidates under a shared protocol within each panel. Parent identity and calculation details are in the corresponding results folder.', '', '| Task | Report |', '|---|---|']
    for task in tasks:
        link = ('evaluation/' + task['id'] + '/comparisons/benchmark_report.md' if task.get('executed') else 'reference_data/' + task['id'] + '/references.md')
        index.append(f"| {task['title']} | [{'Comparison and figures' if task.get('executed') else 'Published reference'}]({link}) |")
    index += ['', '[Benchmark definitions](definitions/README.md) · [Reference data](reference_data/README.md) · [Evaluation records](evaluation/README.md) · [All approaches and run results](../results/README.md)', '', 'Rebuild from saved data with `python scripts/build_reports.py`. Requires `matplotlib`. Report generation does not run predictors.', '']
    (env / 'benchmark/README.md').write_text('\n'.join(index))
    # Reports are regenerated documentation; scientific/image bytes keep their identities.
    for record in (env / 'benchmark/evaluation').glob('*/comparisons/provenance.json'):
        provenance = json.loads(record.read_text())
        for artifact in provenance['artifacts']:
            digest = hashlib.sha256((record.parent / artifact['path']).read_bytes()).hexdigest()
            if artifact.get('filename_components') and digest != artifact['sha256']:
                raise ValueError('A scientific benchmark artifact changed; review its identity before publishing.')
            artifact['sha256'] = digest
            evidence = artifact.get('migration_evidence')
            if evidence:
                same = digest == evidence['original_sha256']
                evidence['content_preserved'] = same
                evidence['change_kind'] = 'byte_preserving_move_or_rename' if same else 'documentation_or_metadata_update'
        record.write_text(json.dumps(provenance, indent=2) + '\n')
    manifest_path = env / 'benchmark/DATA_PROVENANCE.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        manifest['files'] = [
            {'path': str(path.relative_to(env)),
             'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
            for folder in ('benchmark', 'results', 'config', 'runs')
            for path in sorted((env / folder).rglob('*'))
            if path.is_file() and path != manifest_path
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().environment)


if __name__ == '__main__':
    main()

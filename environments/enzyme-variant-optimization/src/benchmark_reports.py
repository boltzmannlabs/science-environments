"""Build one concise Word benchmark per task from saved predictions; no model or network calls."""
from __future__ import annotations
import argparse
import csv
import json
import tempfile
from pathlib import Path


def rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def number(value, digits=4):
    return '—' if value in (None, '') else f'{float(value):.{digits}f}'


def build_task(env, task):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from docx import Document
    from docx.shared import Inches, Pt, Mm, RGBColor
    from docx.enum.section import WD_ORIENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.opc.constants import RELATIONSHIP_TYPE as RT

    tid = task['id']
    folder = env / 'results' / tid / 'agent-alone'
    doc = Document()
    doc.core_properties.author = 'Science environments'
    doc.core_properties.last_modified_by = 'Science environments'
    doc.core_properties.comments = ''
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Mm(297), Mm(210)
    sec.top_margin = sec.bottom_margin = Mm(14)
    sec.left_margin = sec.right_margin = Mm(16)
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(10)
    for name in ['Title', 'Heading 1', 'Heading 2']:
        doc.styles[name].font.color.rgb = RGBColor.from_string('246B98')
    sec.footer.paragraphs[0].text = 'Enzyme variant optimization | Computational prediction comparison'

    def table(headers, values):
        result = doc.add_table(rows=1, cols=len(headers))
        result.style = 'Light Shading Accent 1'
        for cell, value in zip(result.rows[0].cells, headers):
            cell.text = str(value)
        repeat = OxmlElement('w:tblHeader')
        result.rows[0]._tr.get_or_add_trPr().append(repeat)
        for values_row in values:
            cells = result.add_row().cells
            for cell, value in zip(cells, values_row):
                cell.text = str(value)
        return result

    def source(title, url):
        paragraph = doc.add_paragraph('Source: ')
        link = OxmlElement('w:hyperlink')
        link.set(qn('r:id'), paragraph.part.relate_to(url, RT.HYPERLINK, is_external=True))
        run, text = OxmlElement('w:r'), OxmlElement('w:t')
        text.text = title
        run.append(text)
        link.append(run)
        paragraph._p.append(link)

    doc.add_heading(task['title'] + ' — benchmark report', 0)
    doc.add_paragraph('Agent-alone candidates, published prediction values and reference variants calculated in this work.')
    metadata = folder / 'EXECUTION_METADATA.json'
    if metadata.exists():
        model = json.loads(metadata.read_text()).get('llm', {})
        doc.add_paragraph('Agent Scientist: ' + model.get('model', 'See results') + '. Predictor names and units are listed with each measurement.')

    if task.get('metrics'):
        doc.add_heading('Published predictions and our predictions', 1)
        table(['Property / predictor', 'Published prediction', 'Our candidates'], [r[:3] for r in task['metrics']])
        citations = {
            'task_001_rml_stability': ('Teng et al., Tables 1 and sections 3.4/3.7', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC11727178/'),
            'task_002_leh_stability': ('Wijma et al., Figure 1 and methods', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3893934/'),
            'task_003_bla_high_temperature': ('Fan et al., computational screening', 'https://pmc.ncbi.nlm.nih.gov/articles/PMC10883975/'),
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
            doc.add_heading(title, 2)
            doc.add_picture(str(path), width=Inches(9.65))
            doc.add_paragraph(caption, 'Caption')
            charts += 1

        if tid == 'task_006_zhang_hydrolases':
            agreement = env / 'benchmark' / tid / 'comparisions/published_prediction_only.csv'
            if agreement.exists():
                pairs = rows(agreement)
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

        energy_path = folder / 'steps/07_ddgun_stability/predictions.csv'
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
        comparison_path = folder / 'reference_comparison/predictions.csv'
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
        doc.add_paragraph('Parent identity, preparation details and run records: results/' + tid + '/agent-alone/README.md.')

    target = env / 'benchmark' / tid / 'comparisions/benchmark_report.docx'
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(target)
    print(f'{tid}: {charts} embedded charts; {len(doc.tables)} tables')


def build(env):
    tasks = json.loads((env / 'benchmark/report_data.json').read_text())['tasks']
    for task in tasks:
        if task.get('executed'):
            build_task(env, task)
    index = ['# Benchmark comparisons', '', 'Each task report contains numerical comparisons and embedded figures. Parent identity and calculation details are in the corresponding results folder.', '', '| Task | Report |', '|---|---|']
    for task in tasks:
        link = task['id'] + ('/comparisions/benchmark_report.docx' if task.get('executed') else '/references.md')
        index.append(f"| {task['title']} | [{'Word comparison' if task.get('executed') else 'Published reference'}]({link}) |")
    index += ['', 'Rebuild from saved data with `python scripts/build_reports.py`. Requires `python-docx` and `matplotlib`. Report generation does not run predictors.', '']
    (env / 'benchmark/README.md').write_text('\n'.join(index))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--environment', type=Path, default=Path(__file__).resolve().parents[1])
    build(parser.parse_args().environment)


if __name__ == '__main__':
    main()

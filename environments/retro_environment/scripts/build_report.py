#!/usr/bin/env python3
"""Render a public, model-only route report from sanitized data.

Optional isolated dependencies: python-docx and RDKit. No service access or raw
private platform data is used.
"""
import io
import json
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem.Draw import rdMolDraw2D
from docx import Document
from docx.shared import Inches, Pt

BASE = Path(__file__).resolve().parents[1]
RESULTS = BASE / 'results'
RESEARCH = BASE.parents[1] / 'research' / 'retro_environment'


def add_table(doc, headings, rows):
    table = doc.add_table(rows=1, cols=len(headings))
    table.style = 'Light Shading Accent 1'
    for cell, value in zip(table.rows[0].cells, headings):
        cell.text = str(value)
    for row in rows:
        for cell, value in zip(table.add_row().cells, row):
            cell.text = str(value)


def draw_reaction(step, index, number, figure_dir):
    pieces = step['reactants'] + [step['product']]
    width = 330
    height = 190
    for text in pieces:
        if Chem.MolFromSmiles(text) is None:
            raise ValueError(f'Invalid SMILES at top{index} step {number}: {text}')
    # RDKit's multi-molecule renderer preserves every reactant and product.
    mols = [Chem.MolFromSmiles(x) for x in pieces]
    drawing = rdMolDraw2D.MolDraw2DCairo(width * len(pieces), height)
    drawing.DrawMolecules(mols, legends=['Reactant ' + str(i + 1) for i in range(len(pieces) - 1)] + ['Predicted product'])
    drawing.FinishDrawing()
    path = figure_dir / f'top{index:02d}_step{number:02d}.png'
    path.write_bytes(drawing.GetDrawingText())
    return path


def main():
    data = json.loads((RESULTS / 'route_summary.json').read_text())
    audit = json.loads((RESULTS / 'top0_validation.json').read_text())
    fig_dir = RESULTS / 'figures'
    fig_dir.mkdir(exist_ok=True)
    doc = Document()
    doc.styles['Normal'].font.size = Pt(9)
    doc.add_heading('Retro environment: 16 model routes and evidence audit', 0)
    doc.add_paragraph('Target: ' + data['target_smiles'])
    doc.add_paragraph('All routes, ranking scores and yield fields below are computational. No experimentally validated synthesis of this exact target was established. The original private platform output was not distributed.')
    doc.add_heading('Evidence and result', 1)
    doc.add_paragraph('The top0 route was separately assessed: protection conditions include fluoride (incompatible with TBS formation); the protected aryl ether ranked last with forward model score 0 and had no credible coupling catalyst; deprotection is a generic reaction-family analogy. Top1 has the highest illustrative compounded model percentage, but not a measured yield or demonstrated practical superiority.')
    add_table(doc, ['Route', 'Explicit steps', 'Model rank score', 'Illustrative model-yield product (%)', 'Validation'], [
        [r['route'], r['explicit_tree_steps'], r['model_ranking_score'], r['illustrative_sequential_product_pct'], r['experimental_validation']]
        for r in data['routes']
    ])
    doc.add_heading('Literature benchmark and comparator', 1)
    doc.add_paragraph('Protection benchmark: Corey & Venkateswarlu, DOI 10.1021/ja00772a043 (bibliographic class-level precedent; protocol not inspected). Diaryl ether benchmark: Cristau et al., DOI 10.1021/ol036290g (bibliographic class-level precedent; full paper access restricted). Deprotection comparator: Reich, ChemSpider SyntheticPages 132, DOI 10.1039/SP132, reports an experimental 32% isolated yield for a different TBS ether. This yield is NOT a yield for the target. No full route to the exact target was verified; broad patent hits are not target-route evidence.')
    doc.add_paragraph('Public links: https://doi.org/10.1021/ja00772a043 ; https://doi.org/10.1021/ol036290g ; https://cssp.chemspider.com/132')
    for index, route in enumerate(data['routes']):
        doc.add_page_break()
        doc.add_heading(f"Route {route['route']}", 1)
        doc.add_paragraph('Model starting materials: ' + '; '.join(route['starting_materials']))
        doc.add_paragraph(f"Explicit transformations: {route['explicit_tree_steps']}; raw reported num_steps: {route['reported_num_steps']}; illustrative multiplied model percentages: {route['illustrative_sequential_product_pct']}%. No measured target yield.")
        for number, step in enumerate(route['steps'], 1):
            doc.add_heading(f"Step {number}: {step['reaction_name']}", 2)
            doc.add_paragraph('Precursors: ' + ' + '.join(step['reactants']))
            doc.add_paragraph('Predicted intermediate/product: ' + step['product'])
            doc.add_paragraph(f"Model reaction_yield: {step['model_reaction_yield_pct']}% (unmeasured).")
            path = draw_reaction(step, index, number, fig_dir)
            doc.add_picture(str(path), width=Inches(6.7))
            if index == 0:
                a = audit['steps'][number - 1]
                doc.add_paragraph('Selected-route check: forward rank ' + str(a['forward_product_rank']) + '; forward score ' + str(a['forward_model_score']) + '; mapping confidence ' + str(a['atom_mapping_confidence']) + '. ' + a['assessment'])
                doc.add_paragraph('Model-recommended conditions (not validated): ' + a['condition_recommendation'])
            else:
                doc.add_paragraph('Forward prediction, atom mapping, impurities and condition recommendation: NOT RUN for this route. No exact literature match established.')
    doc.add_heading('Limitations and next evidence', 1)
    doc.add_paragraph('No actual precursor procurement, product identification, target yield, selectivity or isolation was performed. Numerical route products multiply model fields under a simplifying assumption, ignore branch topology and separation losses, and cannot be interpreted as experimental or calibrated yields. Expert review and substrate-specific experimental evidence are needed before any route can be called feasible.')
    doc.add_paragraph('Method: sanitized reaction-node tree with one transformation per reaction-bearing node; local renderer RDKit ' + rdBase.rdkitVersion + '. Search boundaries and citations: research/retro_environment/references.md.')
    out = RESULTS / 'retro_benchmark_report.docx'
    doc.save(out)
    print(f'Rendered {len(data["routes"])} model routes and {sum(len(r["steps"]) for r in data["routes"])} structure schemes: {out}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build a PDF catalogue of declared scientific agents from repository metadata."""
from pathlib import Path
import json, re
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).parents[1]
OUT = ROOT / "docs" / "agent_catalog.pdf"

def task_description(path):
    text = path.read_text(errors="replace")
    m = re.search(r"## Description(?: and target)?\s*\n\s*(.*?)(?=\n## |\Z)", text, re.S | re.I)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()[:420]
    return "See the module task card for the declared scientific responsibility."

def task_map(module, prefix):
    d = ROOT / "environments" / module / "tasks"
    return {p.stem.split("_")[1].split("-")[0]: task_description(p)
            for p in d.glob(prefix + "*.md") if p.name != "TASK_CARD_TEMPLATE.md"}

def contract_rows(path, module, task_prefix=None):
    data = json.loads(path.read_text())
    descriptions = task_map(module, task_prefix) if task_prefix else {}
    rows = []
    for item in data:
        purpose = item.get("problem") or item.get("expected_recovery")
        if not purpose:
            number = item["id"].split("-")[-1].lstrip("0") or "0"
            purpose = descriptions.get(number, f"Specialist responsibility: {item.get('group', 'scientific workflow')}")
        rows.append((item["id"], item["name"], re.sub(r"\s+", " ", purpose).strip()))
    return rows

def file_rows(module, prefix, id_prefix):
    d = ROOT / "environments" / module / "tasks"
    rows = []
    for p in sorted(d.glob(prefix + "*.md")):
        if p.name == "TASK_CARD_TEMPLATE.md":
            continue
        text = p.read_text(errors="replace")
        title = re.search(r"^# Task:\s*(.*)$", text, re.M)
        name = (title.group(1) if title else p.stem).replace("_", " ").replace("-", " ")
        num = re.search(r"(?:^|_)(\d+)", p.stem)
        ident = f"{id_prefix}-{int(num.group(1)):02d}" if num else p.stem
        rows.append((ident, name.title(), task_description(p)))
    return rows

modules = [
    ("SPE", file_rows("spe_agents", "spe_", "SPE")),
    ("Geometry Optimisation", file_rows("geo_opt_agents", "geo_opt_", "GEO")),
    ("HOMO–LUMO", file_rows("homo_lumo_agents", "homo_lumo_", "HL")),
    ("QM/MM", contract_rows(ROOT/"environments/qmmm_agents/agents/contracts.json", "qmmm_agents", "qmmm_")),
    ("Molecular Dynamics", contract_rows(ROOT/"environments/md_agents/agents/contracts.json", "md_agents", "md_")),
    ("Coarse-Grained MD", contract_rows(ROOT/"environments/coarse_grained_md/agents/contracts.json", "coarse_grained_md", "cg_")),
    ("FEP/TI specialist agents", contract_rows(ROOT/"environments/fep_ti_agents/agents/fep_agent_contracts.json", "fep_ti_agents")),
    ("FEP/TI problem-solving agents", contract_rows(ROOT/"environments/fep_ti_agents/agents/contracts.json", "fep_ti_agents")),
]

styles = getSampleStyleSheet()
title = ParagraphStyle("CatalogTitle", parent=styles["Title"], alignment=TA_CENTER, fontSize=20, leading=24, spaceAfter=8)
subtitle = ParagraphStyle("Subtitle", parent=styles["Normal"], alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=14)
heading = ParagraphStyle("ModuleHeading", parent=styles["Heading1"], fontSize=15, leading=18, spaceBefore=6, spaceAfter=8)
cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=7.5, leading=9)
small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=8.5, leading=11)

OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=13*mm, leftMargin=13*mm, topMargin=13*mm, bottomMargin=13*mm)
story = [Paragraph("Scientific Agent Catalogue", title), Paragraph("Boltzmann Labs science-environments • generated from repository contracts and task cards", subtitle)]
story.append(Paragraph("Purpose", heading))
story.append(Paragraph("This catalogue lists declared specialist agents and summarizes their intended responsibility. An entry documents an agent contract; it is not by itself evidence that a production engine calculation has been qualified.", small))
story.append(Spacer(1, 6))
total = 0
for idx, (module, rows) in enumerate(modules):
    total += len(rows)
    story.append(Paragraph(f"{module} ({len(rows)} agents)", heading))
    data = [[Paragraph("ID", cell), Paragraph("Agent", cell), Paragraph("Purpose", cell)]]
    data += [[Paragraph(a, cell), Paragraph(b, cell), Paragraph(c, cell)] for a,b,c in rows]
    table = Table(data, colWidths=[24*mm, 52*mm, 101*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f4e79")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#b7c9d6")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f3f7fa")]),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3), ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(table)
    if idx != len(modules)-1:
        story.append(PageBreak())
story.append(Spacer(1, 8))
story.append(Paragraph(f"Total declared agents: {total}", small))
story.append(Paragraph("Source: versioned files under environments/*/agents and environments/*/tasks. Regenerate with scripts/build_agent_catalog_pdf.py.", small))
doc.build(story)
print(f"Wrote {OUT} ({total} agents)")

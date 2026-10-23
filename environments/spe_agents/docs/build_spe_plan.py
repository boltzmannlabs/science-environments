from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ASSETS = DOCS / "assets"
OUTPUT = DOCS / "Boltzmann_Labs_SPE_Agent_Implementation_Plan.docx"

NAVY = "10243E"
BLUE = "176B87"
TEAL = "2AA6A1"
CYAN = "DDF4F3"
PALE = "EFF5F8"
AMBER = "E6A23C"
RED = "B54747"
GRAY = "5B6770"
WHITE = "FFFFFF"


def load_contracts() -> list[dict]:
    contracts = []
    for path in sorted((ROOT / "environments").glob("*/agent.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["path"] = str(path.relative_to(ROOT))
        contracts.append(data)
    if len(contracts) != 18:
        raise RuntimeError(f"Expected 18 SPE contracts, found {len(contracts)}")
    return contracts


def save_figure(fig: plt.Figure, filename: str) -> Path:
    path = ASSETS / filename
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def rounded_box(ax, xy, width, height, text, color, *, fontsize=9, text_color="white", edge=None):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        linewidth=1.3,
        edgecolor=edge or color,
        facecolor=color,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=text_color,
        weight="semibold",
        wrap=True,
    )
    return box


def make_architecture_diagram() -> Path:
    fig, ax = plt.subplots(figsize=(13.5, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.965, "One shared SPE framework, eighteen scientific contracts", ha="center", va="top", fontsize=18, weight="bold", color="#10243E")

    groups = [
        (0.025, 0.72, "CORE MOLECULAR\n01–05", "#176B87"),
        (0.025, 0.53, "METHOD &\nELECTRONIC STRUCTURE\n06–10", "#2AA6A1"),
        (0.025, 0.31, "CHEMISTRY &\nINTERACTIONS\n11–15", "#7456A8"),
        (0.025, 0.09, "DRUG DISCOVERY, MLIP\n& QUALITY CONTROL\n16–20", "#C17B26"),
    ]
    for x, y, label, color in groups:
        rounded_box(ax, (x, y), 0.19, 0.14 if y != 0.09 else 0.16, label, color, fontsize=9)
        ax.add_patch(FancyArrowPatch((0.215, y + 0.07), (0.275, 0.5), arrowstyle="-|>", mutation_scale=14, linewidth=1.2, color="#81909A"))

    shared = [
        "Input parsing & molecular validation",
        "Task routing & environment contract",
        "Submission, status & retry control",
        "Structured result/property extraction",
        "Provenance, artifacts & error diagnosis",
        "Independent acceptance evaluation",
    ]
    ax.add_patch(FancyBboxPatch((0.275, 0.11), 0.39, 0.78, boxstyle="round,pad=0.02,rounding_size=0.025", linewidth=2, edgecolor="#176B87", facecolor="#EFF5F8"))
    ax.text(0.47, 0.855, "SHARED SPE FRAMEWORK", ha="center", va="center", fontsize=13, weight="bold", color="#10243E")
    for index, text in enumerate(shared):
        y = 0.72 - index * 0.105
        rounded_box(ax, (0.305, y), 0.33, 0.075, text, "#FFFFFF", fontsize=9, text_color="#10243E", edge="#B8CBD4")

    targets = [
        (0.73, 0.68, "Existing SPE engine\nprimary shared backend", "#176B87"),
        (0.73, 0.49, "Orbital / property adapters", "#2AA6A1"),
        (0.73, 0.32, "QM/MM adapter", "#7456A8"),
        (0.73, 0.15, "MLIP adapter", "#C17B26"),
    ]
    for x, y, label, color in targets:
        ax.add_patch(FancyArrowPatch((0.665, 0.5), (0.72, y + 0.065), arrowstyle="-|>", mutation_scale=14, linewidth=1.3, color="#81909A"))
        rounded_box(ax, (x, y), 0.235, 0.13, label, color, fontsize=9)

    ax.text(0.5, 0.035, "Adapters execute calculations; environment contracts decide what is valid, required, acceptable, and recoverable.", ha="center", va="center", fontsize=9.5, color="#5B6770")
    return save_figure(fig, "shared-spe-architecture.png")


def make_portfolio_map(contracts: list[dict]) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(14, 9.2))
    group_specs = [
        ("A. Core molecular SPE", range(0, 5), "#176B87"),
        ("B. Electronic structure & methods", range(5, 10), "#2AA6A1"),
        ("C. Chemistry & molecular interactions", range(10, 15), "#7456A8"),
        ("D. Drug discovery & advanced SPE", range(15, 20), "#C17B26"),
    ]
    for ax, (title, indices, color) in zip(axes.flat, group_specs):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.01, 0.02), 0.98, 0.94, boxstyle="round,pad=0.015,rounding_size=0.025", linewidth=1.7, edgecolor=color, facecolor="#F8FBFC"))
        ax.text(0.05, 0.91, title, fontsize=13, weight="bold", color=color, va="top")
        y = 0.76
        for index in indices:
            contract = contracts[index]
            circle = plt.Circle((0.09, y + 0.03), 0.043, color=color)
            ax.add_patch(circle)
            ax.text(0.09, y + 0.03, contract["id"], color="white", ha="center", va="center", fontsize=9, weight="bold")
            name = contract["name"].replace(" Agent", "")
            ax.text(0.16, y + 0.03, name, color="#10243E", ha="left", va="center", fontsize=10.2, weight="semibold")
            y -= 0.145
    fig.suptitle("SPE specialist portfolio", fontsize=20, weight="bold", color="#10243E", y=0.99)
    fig.text(0.5, 0.012, "Eighteen environments; one calculation infrastructure; distinct scientific contracts and evidence gates.", ha="center", fontsize=10, color="#5B6770")
    fig.tight_layout(rect=(0, 0.035, 1, 0.965))
    return save_figure(fig, "spe-environment-portfolio.png")


def make_roadmap_diagram() -> Path:
    phases = [
        ("Foundation", 1, 2, "Shared schemas, adapters, provenance"),
        ("Priority agents", 2, 4, "01, 02, 03, 06, 07, 20"),
        ("Core chemistry", 4, 6, "04, 05, 14"),
        ("Orbitals & properties", 5, 7, "08, 09"),
        ("Interaction workflows", 7, 10, "10, 11, 16, 17, 18"),
        ("Metal systems", 9, 12, "12, 13"),
        ("QM/MM", 11, 13, "15"),
        ("MLIP reference", 13, 15, "19"),
    ]
    colors = ["#10243E", "#176B87", "#2AA6A1", "#3A8EA5", "#7456A8", "#9B6B9E", "#C17B26", "#E6A23C"]
    fig, ax = plt.subplots(figsize=(14, 6.7))
    ax.set_xlim(0.5, 14.5)
    ax.set_ylim(-0.5, len(phases) - 0.5)
    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels([item[0] for item in phases], fontsize=10)
    ax.set_xticks(range(1, 15))
    ax.set_xticklabels([f"W{week}" for week in range(1, 15)], fontsize=9)
    ax.xaxis.tick_top()
    ax.grid(axis="x", color="#D8E1E6", linewidth=0.8)
    for index, ((_, start, end, label), color) in enumerate(zip(phases, colors)):
        ax.barh(index, end - start + 1, left=start - 0.45, height=0.58, color=color, edgecolor="white")
        ax.text((start + end) / 2, index, label, ha="center", va="center", color="white", fontsize=8.8, weight="semibold")
    ax.invert_yaxis()
    ax.set_title("Indicative 14-week implementation roadmap", fontsize=19, weight="bold", color="#10243E", pad=30)
    ax.text(7.5, len(phases) - 0.1, "Promotion occurs by evidence gate—not by calendar date.", ha="center", fontsize=10, color="#5B6770")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    return save_figure(fig, "spe-implementation-roadmap.png")


def make_quality_flow() -> Path:
    steps = [
        ("1", "Interpret", "objective & outputs"),
        ("2", "Validate", "structure, charge, spin"),
        ("3", "Plan", "method & adapter"),
        ("4", "Execute", "fixed-geometry SPE"),
        ("5", "Diagnose", "classify failure"),
        ("6", "Recover", "bounded & recorded"),
        ("7", "Evaluate", "independent evidence"),
        ("8", "Report", "results & limits"),
    ]
    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    xs = [0.02 + index * 0.122 for index in range(8)]
    colors = ["#176B87", "#176B87", "#2AA6A1", "#2AA6A1", "#7456A8", "#7456A8", "#C17B26", "#C17B26"]
    for index, ((number, title, detail), x, color) in enumerate(zip(steps, xs, colors)):
        rounded_box(ax, (x, 0.32), 0.10, 0.38, f"{number}\n{title}\n{detail}", color, fontsize=8.6)
        if index < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + 0.10, 0.51), (xs[index + 1], 0.51), arrowstyle="-|>", mutation_scale=14, linewidth=1.2, color="#81909A"))
    ax.text(0.5, 0.89, "Controlled SPE execution and quality lifecycle", ha="center", fontsize=18, weight="bold", color="#10243E")
    ax.text(0.5, 0.12, "Any scientific-setting change exits the automatic path and becomes a human-review decision.", ha="center", fontsize=10, color="#B54747", weight="semibold")
    return save_figure(fig, "spe-quality-lifecycle.png")


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=70, start=90, bottom=70, end=90) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_run_font(run, name="Aptos", size=None, color=None, bold=None) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, size=8, color=GRAY)
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])


def add_heading(doc: Document, text: str, level: int = 1):
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.keep_with_next = True
    run = paragraph.add_run(text)
    return paragraph


def add_body(doc: Document, text: str, *, bold_lead: str | None = None):
    p = doc.add_paragraph(style="Body Text")
    if bold_lead and text.startswith(bold_lead):
        lead = p.add_run(bold_lead)
        lead.bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def add_bullets(doc: Document, items: list[str] | tuple[str, ...]):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(item)


def add_numbered(doc: Document, items: list[str] | tuple[str, ...]):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        p.add_run(item)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None, font_size=8.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    hdr = table.rows[0]
    set_repeat_table_header(hdr)
    for i, header in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(header)
        set_run_font(run, size=font_size, color=WHITE, bold=True)
        if widths:
            cell.width = Inches(widths[i])
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(values):
            cell = cells[i]
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            if row_index % 2:
                set_cell_shading(cell, PALE)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(str(value))
            set_run_font(run, size=font_size, color=NAVY)
            if widths:
                cell.width = Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_picture(doc: Document, path: Path, width: float, caption: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    run = cap.add_run(caption)
    set_run_font(run, size=8.5, color=GRAY)
    run.italic = True


def add_contract_detail(doc: Document, contract: dict):
    add_heading(doc, f"{contract['id']}. {contract['name']}", 2)
    add_body(doc, contract["description"])
    rows = [
        ["Group / status", f"{contract['group']} / {contract['integration_status']}"],
        ["Required inputs", " • ".join(contract["required_inputs"])],
        ["Optional inputs", " • ".join(contract["optional_inputs"])],
        ["Outputs", " • ".join(contract["outputs"])],
        ["Intended adapters", ", ".join(f"{name}" for name in contract["tool_adapters"])],
        ["Validation", " • ".join(contract["validation_checks"])],
        ["Acceptance evidence", " • ".join(contract["acceptance_criteria"])],
        ["Scientific boundary", " • ".join(contract["capability_boundaries"])],
        ["Bounded recovery", " • ".join(contract["recovery_actions"]) or "No automatic recovery"],
        ["Human review", " • ".join(contract["human_review_when"])],
        ["Retry ceiling", str(contract["max_retries"])],
    ]
    add_table(doc, ["Contract field", "Environment-specific rule"], rows, widths=[1.45, 5.75], font_size=7.8)


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(0.65)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos")
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor.from_string(NAVY)

    body = styles["Body Text"]
    body.font.name = "Aptos"
    body._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos")
    body.font.size = Pt(9.5)
    body.paragraph_format.space_after = Pt(5)
    body.paragraph_format.line_spacing = 1.08

    for level, size, color in ((1, 20, NAVY), (2, 14, BLUE), (3, 11, TEAL)):
        style = styles[f"Heading {level}"]
        style.font.name = "Aptos Display"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(10 if level == 1 else 7)
        style.paragraph_format.space_after = Pt(5)

    for name in ("List Bullet", "List Number"):
        style = styles[name]
        style.font.name = "Aptos"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos")
        style.font.size = Pt(9.2)
        style.paragraph_format.space_after = Pt(2)

    header = section.header.paragraphs[0]
    header.text = "BOLTZMANN LABS  |  SPE AGENT PROGRAM"
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run_font(header.runs[0], size=8, color=BLUE, bold=True)
    add_page_number(section.footer.paragraphs[0])

    settings = doc.settings._element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)


def add_toc(doc: Document) -> None:
    p = doc.add_paragraph()
    run = p.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Right-click and update this field if the table of contents is not populated automatically."
    separate.append(text)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char, instr, separate, end])


def build_document() -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    contracts = load_contracts()
    architecture = make_architecture_diagram()
    portfolio = make_portfolio_map(contracts)
    roadmap = make_roadmap_diagram()
    lifecycle = make_quality_flow()

    doc = Document()
    configure_document(doc)

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    run = p.add_run("BOLTZMANN LABS")
    set_run_font(run, name="Aptos Display", size=13, color=TEAL, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(5)
    run = p.add_run("18 Specialized Single-Point Energy\nAgent Environments")
    set_run_font(run, name="Aptos Display", size=27, color=NAVY, bold=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Implementation Plan, Scientific Contracts, Validation Strategy and Delivery Roadmap")
    set_run_font(run, size=11.5, color=BLUE, bold=True)

    cover_image = ASSETS / "spe-agent-network-cover.png"
    pic = doc.add_paragraph()
    pic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pic.add_run().add_picture(str(cover_image), width=Inches(7.05))

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(5)
    run = p.add_run("ONE SHARED SPE FRAMEWORK  •  TWENTY SCIENTIFIC TASK CONTRACTS")
    set_run_font(run, size=10, color=TEAL, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Version 1.0  |  {date.today().isoformat()}  |  Planning baseline")
    set_run_font(run, size=8.5, color=GRAY)
    doc.add_page_break()

    add_heading(doc, "Document control", 1)
    add_table(
        doc,
        ["Field", "Value"],
        [
            ["Purpose", "Implementation plan for 18 specialized SPE agent environments using shared calculation infrastructure"],
            ["Scope", "Environment contracts, shared services, phased implementation, verification, governance and delivery gates"],
            ["Audience", "Boltzmann Labs scientific software, computational chemistry, ML platform, QA and program leadership teams"],
            ["Source of truth", "Version-controlled contracts in environments/<id>-<slug>/agent.json"],
            ["Current status", "All 18 active contracts defined; historical IDs 13 and 16 retired"],
            ["Decision principle", "Promote capabilities only when execution and scientific-acceptance evidence both pass"],
        ],
        widths=[1.55, 5.65],
        font_size=8.5,
    )
    add_heading(doc, "Contents", 1)
    add_toc(doc)
    doc.add_page_break()

    add_heading(doc, "1. Executive summary", 1)
    add_body(doc, "This plan establishes eighteen active specialist agent environments for Single-Point Energy work. An environment is a scientific contract: it defines the problem it owns, required inputs, supported tool adapters, outputs, validation checks, evidence needed for acceptance, bounded recovery actions and escalation boundaries. The environments reuse a common SPE execution framework; they are not eighteen duplicated quantum-chemistry engines.")
    add_body(doc, "The implementation starts with the highest-leverage environments—small molecules, drug-like molecules, conformer comparison, DFT method comparison, basis convergence and independent quality control. It then adds orbital and property extraction, interaction-energy workflows, metal systems, prepared QM/MM calculations and MLIP reference comparisons. Every adapter remains unverified until representative end-to-end, invalid-input, failure, parser and scientific-evaluation tests pass.")
    add_heading(doc, "1.1 Outcomes", 2)
    add_bullets(doc, [
        "A single versioned framework for parsing, validation, routing, execution tracking, extraction, provenance and evaluation.",
        "Eighteen individually addressable specialists with explicit capability boundaries and no silent scientific-setting changes.",
        "Structured SPE results whose execution state is separate from scientific acceptance.",
        "Independent quality control that can audit every other environment and recommend only bounded, recorded recovery.",
        "A promotion process that moves integrations from unverified to prototype and validated only with evidence.",
    ])
    add_heading(doc, "1.2 Explicit non-goals", 2)
    add_bullets(doc, [
        "Building eighteen calculation backends or eighteen isolated Python environments.",
        "Treating electronic energies as free energies, binding affinities, pKa values or thermal observables without the required additional calculations.",
        "Locating transition states, optimizing geometries or sampling conformations unless a separate supported workflow is invoked.",
        "Automatically changing charge, multiplicity, chemical identity, method, basis, fragment partition or QM region to force a result.",
    ])
    add_picture(doc, architecture, 7.15, "Figure 1. Shared execution infrastructure with environment-specific scientific ownership.")
    doc.add_page_break()

    add_heading(doc, "2. Program architecture", 1)
    add_heading(doc, "2.1 Separation of shared and specialist responsibilities", 2)
    add_table(
        doc,
        ["Shared framework responsibility", "Environment-specific responsibility"],
        [
            ["Input parser and molecular-structure validation", "Allowed system types; charge, spin, fragment and partition rules"],
            ["Calculation submission and status tracking", "Supported methods, basis/ECP requirements and adapter selection"],
            ["Structured result and artifact extraction", "Required energies, orbitals, properties, components and units"],
            ["Failure taxonomy, retry accounting and provenance", "Scientific warnings, permitted recovery and escalation policy"],
            ["Independent evaluator interface", "Acceptance criteria and evidence required for pass/fail/review"],
            ["Registry, routing and prompt composition", "Task vocabulary, capability boundaries and handoff conditions"],
        ],
        widths=[3.25, 3.95],
        font_size=8.4,
    )
    add_heading(doc, "2.2 Common execution lifecycle", 2)
    add_picture(doc, lifecycle, 7.15, "Figure 2. Every specialist follows the same controlled lifecycle.")
    add_numbered(doc, [
        "Interpret the objective and requested outputs without broadening the scientific claim.",
        "Validate structure, units, electron count, charge, multiplicity, method and all environment-specific definitions.",
        "Resolve only declared adapters and record the exact calculation plan and expected artifacts.",
        "Execute fixed-geometry calculations while preserving settings, logs, versions and inputs.",
        "Classify failures before correction; never treat a retry as a scientific redesign.",
        "Apply only declared bounded recovery within the retry ceiling and record each change.",
        "Evaluate every acceptance criterion using explicit evidence independent of process completion.",
        "Report results, provenance, warnings, limitations and unresolved review conditions.",
    ])
    add_heading(doc, "2.3 Core state model", 2)
    add_table(
        doc,
        ["Layer", "Allowed states", "Rule"],
        [
            ["Integration maturity", "unverified • prototype • validated • blocked", "Describes adapter readiness, not a single job result"],
            ["Execution", "completed • failed • blocked • needs-review", "Describes the calculation workflow"],
            ["Independent evaluation", "pass • fail • needs-review • not-evaluated", "Describes scientific and evidence acceptance"],
            ["Failure class", "input • capability • tool • configuration • execution • convergence • parsing • scientific • review", "Determines whether recovery is allowed"],
        ],
        widths=[1.35, 2.45, 3.4],
        font_size=8.1,
    )
    doc.add_page_break()

    add_heading(doc, "3. SPE environment portfolio", 1)
    add_picture(doc, portfolio, 7.15, "Figure 3. The eighteen specialist environments grouped by scientific purpose.")
    rows = []
    for contract in contracts:
        rows.append([
            contract["id"],
            contract["name"].replace(" Agent", ""),
            contract["group"],
            ", ".join(contract["tool_adapters"]),
            contract["integration_status"],
        ])
    add_table(doc, ["ID", "Environment", "Group", "Intended adapter(s)", "Status"], rows, widths=[0.38, 2.35, 1.2, 2.55, 0.75], font_size=7.1)
    doc.add_page_break()

    add_heading(doc, "4. Phased implementation roadmap", 1)
    add_body(doc, "The roadmap is deliberately evidence-gated. Week labels are planning targets, not permission to promote an environment. A phase can finish only when its code, fixtures, failure behavior and independent scientific evaluation satisfy the gate.")
    add_picture(doc, roadmap, 7.15, "Figure 4. Indicative sequence; workstreams overlap where interfaces are stable.")
    phases = [
        ["0", "Weeks 1–2", "Shared foundation", "Schemas; adapter protocol; parser bridge; job states; artifact/provenance model; evaluator; mock adapter", "Framework can validate, execute a mock, fail, recover, evaluate and report"],
        ["1", "Weeks 2–4", "Priority specialists", "01, 02, 03, 06, 07, 20", "Representative valid, invalid, failure and evidence tests pass"],
        ["2", "Weeks 4–6", "Charged/open-shell/reaction", "04, 05, 14", "Electron-count, spin and stoichiometric bookkeeping verified"],
        ["3", "Weeks 5–7", "Orbitals and properties", "08, 09", "Wavefunction compatibility and visualization-artifact schemas stable"],
        ["4", "Weeks 7–10", "Interaction workflows", "10, 11, 16, 17, 18", "Fragment/reference arithmetic, sign conventions and BSSE paths tested"],
        ["5", "Weeks 9–12", "Metal systems", "12, 13", "Oxidation/spin/ECP/relativistic and cluster-boundary review gates proven"],
        ["6", "Weeks 11–13", "Prepared QM/MM", "15", "Partition, boundary, embedding and energy-component consistency validated"],
        ["7", "Weeks 13–14", "MLIP reference", "19", "Reliable reference dataset, energy alignment and OOD policy available"],
    ]
    add_table(doc, ["Phase", "Target", "Workstream", "Scope", "Exit evidence"], phases, widths=[0.42, 0.75, 1.25, 2.35, 2.45], font_size=7.4)
    add_heading(doc, "4.1 Priority build sequence", 2)
    add_bullets(doc, [
        "First operational candidates: 01, 02, 03, 06, 07 and 20.",
        "Add 04, 05 and 14 early enough that charge, open-shell and reaction bookkeeping shape the shared schemas.",
        "Do not begin metal-system promotion until method/ECP support and spin-state review policy are explicit.",
        "Do not promote QM/MM until a prepared, parameterized system and stable partition contract exist.",
        "Do not promote MLIP comparison until model-domain metadata and compatible QM reference data are available.",
    ])
    doc.add_page_break()

    add_heading(doc, "5. Detailed environment contracts", 1)
    add_body(doc, "The following implementation specifications are generated from the version-controlled environment contracts. The JSON files remain the machine-readable source of truth.")
    for index, contract in enumerate(contracts):
        add_contract_detail(doc, contract)
        if index in {4, 9, 14}:
            doc.add_page_break()
    doc.add_page_break()

    add_heading(doc, "6. Shared framework work packages", 1)
    work_packages = [
        ["WP1", "Contracts and schemas", "Versioned task/result schemas; contract validation; status vocabularies; unit conventions", "Schema fixtures and backward-compatibility tests"],
        ["WP2", "Structure ingestion", "JSON/XYZ and approved external parsers; atom/coordinate checks; unit normalization; immutable original input", "Golden parsing fixtures and malformed-input suite"],
        ["WP3", "Scientific preflight", "Electron count; charge/multiplicity parity; method/basis/element support; fragment/QM-region rules", "Per-environment valid and invalid matrices"],
        ["WP4", "Adapter layer", "Common submit/status/cancel/result interface over existing SPE and specialist services", "Mock contract tests plus versioned real-adapter smoke tests"],
        ["WP5", "Result extraction", "Energies, units, orbitals, properties, component arithmetic, logs and visualization artifacts", "Parser fixtures including malformed and partial outputs"],
        ["WP6", "Diagnosis and recovery", "Failure classification, bounded actions, retry ceiling, duplicate-attempt prevention and audit log", "Known-failure and retry-exhaustion tests"],
        ["WP7", "Independent evaluation", "Exact acceptance evidence, pass/fail/review semantics and environment evaluator plugins", "Evaluator tests independent of adapter mocks"],
        ["WP8", "Observability and provenance", "Task IDs, timestamps, engine versions, full settings, artifact checksums and lineage", "Reproduction drill from preserved record"],
        ["WP9", "Security and operations", "Resource limits, input size limits, timeouts, cancellation, secret isolation and sandbox policy", "Operational readiness checklist"],
    ]
    add_table(doc, ["WP", "Area", "Implementation content", "Verification artifact"], work_packages, widths=[0.42, 1.4, 3.2, 2.25], font_size=7.5)
    add_heading(doc, "6.1 Proposed adapter interface", 2)
    add_body(doc, "Each engine integration should implement a small common surface: capability discovery, request translation, submission, status polling or completion, cancellation, structured result translation and artifact collection. Capability discovery must report engine/version, supported elements, methods, basis/ECP options, open-shell support, property outputs and hard resource limits. An adapter must reject unsupported settings before submission rather than approximate them.")
    add_heading(doc, "6.2 Provenance minimum", 2)
    add_bullets(doc, [
        "Original and normalized input digests, structure identifiers and all transformations.",
        "Environment ID and contract version used to validate and evaluate the task.",
        "Adapter, engine and engine version; full method, basis, dispersion, solvent, SCF and resource settings.",
        "Execution timestamps, host/device class where relevant, attempt number and recovery change log.",
        "Raw outputs, structured outputs, warnings, logs, artifact paths and checksums.",
        "Criterion-by-criterion independent evaluation evidence and final decision.",
    ])
    doc.add_page_break()

    add_heading(doc, "7. Verification and scientific acceptance", 1)
    add_heading(doc, "7.1 Test pyramid", 2)
    tests = [
        ["Contract", "All 18 active contracts load; IDs/slugs unique; required fields complete; status and retry values valid", "Every change"],
        ["Schema", "Valid tasks/results accepted; missing, extra, wrongly typed and unitless fields rejected", "Every change"],
        ["Scientific preflight", "Geometry, electron count, spin, composition, fragments, references and partitions", "Per environment"],
        ["Adapter", "Capability discovery, translation, timeout, failure, cancellation and malformed output", "Per engine/version"],
        ["Extraction", "Energy/property values, units, arrays, artifacts and warnings from golden outputs", "Per output format"],
        ["Recovery", "Allowed action succeeds; forbidden scientific change escalates; retries stop at ceiling", "Per failure class"],
        ["Evaluator", "Pass, fail, needs-review and not-evaluated from explicit evidence", "Per acceptance criterion"],
        ["End to end", "Representative real calculation with reproducible provenance", "Before promotion"],
        ["Regression", "Reference cases remain within declared tolerances across releases", "Release gate"],
    ]
    add_table(doc, ["Layer", "Required coverage", "Cadence"], tests, widths=[1.15, 4.95, 1.2], font_size=8.0)
    add_heading(doc, "7.2 Minimum fixture set per environment", 2)
    add_bullets(doc, [
        "One representative valid input and expected structured result shape.",
        "One missing-required-input case and one scientifically inconsistent input case.",
        "One unsupported method, element, basis, property or partition case where applicable.",
        "One engine/tool failure and one malformed or incomplete output case.",
        "One bounded recovery success and one retry-exhaustion or forbidden-change escalation case.",
        "One acceptance pass, one scientific fail and one needs-review evidence set.",
    ])
    add_heading(doc, "7.3 Acceptance arithmetic that must be independently reproduced", 2)
    add_table(
        doc,
        ["Workflow", "Independent check"],
        [
            ["Conformer ranking", "Recompute all relative energies from recorded absolute energies and common units"],
            ["Method/basis series", "Recompute pairwise and successive differences; verify fixed geometry and settings"],
            ["Interaction energy", "E(complex) − ΣE(fragments), with explicit geometry and BSSE convention"],
            ["Reaction energy", "ΣνproductsE − ΣνreactantsE, preserving stoichiometric coefficients and sign"],
            ["Strain energy", "E(target geometry) − E(reference geometry) for the same chemical state"],
            ["MLIP comparison", "Recompute aligned errors after units, atom order and energy-zero convention are verified"],
        ],
        widths=[1.75, 5.45],
        font_size=8.2,
    )
    doc.add_page_break()

    add_heading(doc, "8. Recovery policy", 1)
    add_body(doc, "Recovery is an auditable response to a classified failure, not permission to alter the scientific question. The quality-control agent can recommend recovery, but the source environment owns its allowed action list and retry ceiling.")
    add_table(
        doc,
        ["May be automatic when declared", "Must require human review"],
        [
            ["Increase SCF iteration ceiling within configured bounds", "Change charge, multiplicity or target electronic state"],
            ["Use a documented conservative SCF convergence aid", "Change method, functional, basis, ECP or relativistic model"],
            ["Retry transient transport/execution failure", "Move atoms, optimize geometry or change molecular identity"],
            ["Reparse preserved output or regenerate a supported property", "Change fragments, stoichiometry, QM region, boundary or embedding"],
            ["Normalize exact units or atom ordering with an audit record", "Change solvent, dispersion, counterpoise or acceptance threshold"],
            ["Repair representation-only metadata", "Suppress warnings, omit failed components or claim unsupported observables"],
        ],
        widths=[3.6, 3.6],
        font_size=8.2,
    )
    add_heading(doc, "8.1 Recovery decision sequence", 2)
    add_numbered(doc, [
        "Classify the failure and identify the evidence supporting that classification.",
        "Check whether the source contract declares a corresponding recovery action.",
        "Confirm that the proposed action preserves scientific identity and has not already failed identically.",
        "Record the before/after setting, rationale, confidence and attempt number.",
        "Run within the remaining retry budget; independently evaluate the new result.",
        "Escalate if evidence remains incomplete, diagnostics conflict or any scientific setting must change.",
    ])
    doc.add_page_break()

    add_heading(doc, "9. Risk register and mitigations", 1)
    risks = [
        ["R1", "A completed calculation is mistaken for a valid solution", "High", "Independent acceptance state and criterion evidence; QC environment 20"],
        ["R2", "Charge/spin or electronic state is wrong", "High", "Electron-count parity, explicit multiplicity, spin diagnostics and mandatory review"],
        ["R3", "Incompatible settings corrupt comparisons", "High", "Immutable comparison protocol and machine-checked settings fingerprint"],
        ["R4", "Interaction/reaction arithmetic uses inconsistent references", "High", "Explicit fragment/stoichiometric graph and independent recomputation"],
        ["R5", "Metal calculation converges to a questionable state", "High", "Oxidation/spin/ECP checks, stability diagnostics and no automatic state change"],
        ["R6", "Cluster results are overinterpreted", "Medium", "Prominent environment boundaries and model provenance in every result"],
        ["R7", "Adapter drift changes parsed outputs", "High", "Engine-version pinning, golden output fixtures and release regression"],
        ["R8", "Recovery loop hides failures", "High", "Retry ceilings, duplicate-attempt detection and immutable audit history"],
        ["R9", "MLIP is used outside its domain", "High", "Model cards, element/domain checks, uncertainty/OOD thresholds and QM references"],
        ["R10", "Resource costs grow unexpectedly", "Medium", "Preflight estimates, atom/basis limits, queue policy, timeouts and cancellation"],
    ]
    add_table(doc, ["ID", "Risk", "Impact", "Primary mitigation"], risks, widths=[0.4, 2.4, 0.6, 3.8], font_size=7.8)
    add_heading(doc, "9.1 Critical external dependencies", 2)
    add_bullets(doc, [
        "Documented capability/version endpoint for the existing Boltzmann SPE engine.",
        "Stable output artifacts for orbital and electron-density/property extraction.",
        "Validated metal/ECP and open-shell method support with representative benchmark cases.",
        "Prepared-system contract and component-energy convention for QM/MM.",
        "Versioned MLIP model metadata and a compatible reference QM dataset.",
    ])
    doc.add_page_break()

    add_heading(doc, "10. Promotion and release governance", 1)
    add_table(
        doc,
        ["Status", "Meaning", "Required evidence"],
        [
            ["unverified", "Contract exists; integration has not been demonstrated", "Complete contract only; no operational claim"],
            ["prototype", "Adapter works on controlled fixtures or dry runs", "Translation, parsing, negative tests and known limitations"],
            ["validated", "Representative real workflows and scientific evaluation pass", "End-to-end, failures, recovery, reproducibility and independent review"],
            ["blocked", "A precise missing capability prevents supported execution", "Named blocker, affected scope and resolution condition"],
        ],
        widths=[0.9, 2.4, 3.9],
        font_size=8.2,
    )
    add_heading(doc, "10.1 Environment promotion checklist", 2)
    add_bullets(doc, [
        "The intended adapter resolves to an actual installed or reachable service and reports its version.",
        "Supported methods, basis sets, elements, charge/spin modes, properties and limits are machine-readable.",
        "Request and response translation preserve all scientific settings and units.",
        "Valid, invalid, tool-failure, non-convergence, malformed-output and review fixtures pass.",
        "Every acceptance criterion has an executable or explicitly reviewed evidence check.",
        "Recovery behavior respects the declared action list and maximum retries.",
        "A representative run can be reproduced from stored inputs, settings, versions and artifacts.",
        "Capability boundaries and unresolved limitations are present in user-facing results.",
    ])
    add_heading(doc, "10.2 Release deliverables", 2)
    add_table(
        doc,
        ["Release", "Deliverable"],
        [
            ["R0 — Contract baseline", "Eighteen reviewed JSON contracts, schemas, CLI registry/router, prompt builder and independent evaluator"],
            ["R1 — Priority prototype", "01, 02, 03, 06, 07 and 20 connected to controlled adapter fixtures"],
            ["R2 — Core operational candidate", "Priority set plus 04, 05, 08, 09 and 14 on representative real cases"],
            ["R3 — Interaction expansion", "10, 11, 16, 17 and 18 with verified reference bookkeeping"],
            ["R4 — Advanced chemistry", "12, 13 and 15 with explicit review-heavy gates"],
            ["R5 — MLIP comparison", "19 with domain metadata, uncertainty policy and reference benchmark"],
        ],
        widths=[1.8, 5.4],
        font_size=8.1,
    )
    doc.add_page_break()

    add_heading(doc, "11. Current repository implementation", 1)
    add_body(doc, "The planning baseline already provides a standalone SPE package. This document does not mark engine integrations operational; it maps the existing contract scaffold to the work required for implementation and validation.")
    add_table(
        doc,
        ["Repository path", "Purpose"],
        [
            ["environments/<id>-<slug>/agent.json", "Eighteen machine-readable specialist contracts"],
            ["src/spe_agents/models.py", "Contract model and configuration validation"],
            ["src/spe_agents/registry.py", "Loading, lookup and keyword routing"],
            ["src/spe_agents/prompts.py", "Composition of shared rules with one specialist contract"],
            ["src/spe_agents/evaluation.py", "Independent evidence evaluation interface"],
            ["src/spe_agents/cli.py", "Validate, list, show, route, prompt and evaluate commands"],
            ["schemas/task.schema.json", "Structured task exchange contract"],
            ["schemas/result.schema.json", "Structured result, provenance and acceptance-evidence contract"],
            ["tests/", "Registry, routing, prompt and evaluator baseline tests"],
        ],
        widths=[2.7, 4.5],
        font_size=8.2,
    )
    add_heading(doc, "11.1 Immediate next actions", 2)
    add_numbered(doc, [
        "Inventory the existing SPE engine's actual method, basis, element, open-shell, property and artifact capabilities.",
        "Implement a versioned adapter protocol and a mock adapter contract test suite.",
        "Connect environment 01 to the engine using water, methane, ammonia and ethanol fixtures.",
        "Implement comparison orchestration for 03, 06 and 07 with settings fingerprints and independent arithmetic.",
        "Implement environment 20 as a separate evaluator/recovery service before broadening execution.",
        "Promote only the paths supported by recorded real-run and failure evidence; leave the rest unverified or blocked.",
    ])

    add_heading(doc, "Appendix A. Definition of done", 1)
    add_bullets(doc, [
        "All 18 active contracts remain version-controlled and validate against the shared model.",
        "At least the priority six environments run end to end through an actual versioned adapter.",
        "No environment fabricates or infers unsupported scientific results.",
        "Every completed result carries units, settings, versions, artifacts, warnings and criterion evidence.",
        "Independent evaluation can disagree with execution success and force fail or needs-review.",
        "Recovery never changes scientific settings silently and always stops at the retry ceiling.",
        "Representative benchmarks and limitations are documented before operational use.",
    ])
    add_heading(doc, "Appendix B. Generated visual asset", 1)
    add_body(doc, "The cover illustration was generated specifically for this plan using the built-in image-generation workflow. The architecture, portfolio, roadmap and quality-lifecycle diagrams are deterministic project-local figures generated by this build script so their labels remain accurate and reproducible.")

    doc.core_properties.title = "Boltzmann Labs — 18 Specialized SPE Agent Environments"
    doc.core_properties.subject = "Implementation plan, scientific contracts, validation strategy and delivery roadmap"
    doc.core_properties.author = "Boltzmann Labs"
    doc.core_properties.keywords = "single-point energy, SPE, agents, DFT, QM/MM, MLIP, validation"
    doc.core_properties.comments = "Generated from version-controlled SPE environment contracts."
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    result = build_document()
    print(result)

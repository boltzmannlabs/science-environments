"""Render compact JPG method diagrams; reads no raw jobs and starts no scientific tools."""
from pathlib import Path
from run_paths import historical_result, resolve_artifact
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

SPECS = [{'task': 'task_001_rml_stability',
  'title': 'RML stability',
  'stages': [['Parent checks', 'Python · 3TGL sequence'],
             ['Variant generation', 'SolubleMPNN'],
             ['Property screening', 'Enzymes · NetSolP'],
             ['Protein structures', 'Protein Structure Prediction'],
             ['Substrate scoring', 'Vina'],
             ['Structure quality', 'MolProbity · CCTBX']],
  'later': 'Enzymes + NetSolP: properties     |     DDGun_SEQ: stability'},
 {'task': 'task_002_leh_stability',
  'title': 'LEH stability',
  'stages': [['Parent checks', 'Python · 1NWW dimer'],
             ['Generation and revision', 'SolubleMPNN · ThermalMPNN'],
             ['Property screening', 'Enzymes · NetSolP'],
             ['Complex structures', 'Boltz2'],
             ['Substrate scoring', 'Vina'],
             ['Structure quality', 'MolProbity']],
  'later': 'Enzymes + NetSolP: properties     |     DDGun_SEQ: stability'},
 {'task': 'task_003_bla_high_temperature',
  'title': 'BLA high-temperature performance',
  'stages': [['Parent checks', 'Python · mature BLA'],
             ['Generation and revision', 'SolubleMPNN'],
             ['Temperature screening', 'Enzymes'],
             ['Complex structures', 'Boltz2'],
             ['Substrate poses', 'DiffDock'],
             ['Structure quality', 'MolProbity · CCTBX']],
  'later': 'Enzymes + NetSolP: properties   |   EvoEF1: folding\n'
           'FASPR → PACKMAN: static packing entropy'},
 {'task': 'task_004_athol1_substrate',
  'title': 'AtHOL1 substrate expansion',
  'stages': [['Parent and reaction', 'Python · 3LCC + ligands'],
             ['Generation and revision', 'SolubleMPNN · ThermalMPNN'],
             ['Property screening', 'CatPred · Enzymes'],
             ['Protein structures', 'Protein Structure Prediction'],
             ['Ligand-state modeling', 'Placer'],
             ['Structure quality', 'MolProbity']],
  'later': 'Enzymes + NetSolP + EvoEF1: properties and folding\n'
           'OpenMM → field analysis + PySCF: reaction-site assessment'},
 {'task': 'task_005_sun_leh_pythia',
  'title': 'Sun LEH / Pythia study',
  'stages': [['Freeze inputs', 'Python · 1NWW mapping'],
             ['Mutation scoring', 'Pythia'],
             ['Verify coverage', 'Python'],
             ['Rank substitutions', 'Python · summed score'],
             ['Select mutations', 'Python · score < −2'],
             ['Seal scoring outputs', 'Python audit']],
  'later': 'Enzymes + NetSolP: properties     |     DDGun_SEQ: stability'},
 {'task': 'task_006_zhang_hydrolases',
  'title': 'Zhang cellulase / β-glucanase study',
  'stages': [['Freeze sequences', 'Python · WT and M2/M5'],
             ['WT structures', 'AlphaFold2 / ColabFold'],
             ['WT mutation scoring', 'Pythia'],
             ['M2/M5 mutation scoring', 'ESM-2'],
             ['Verify and rank', 'Python'],
             ['Seal comparisons', 'Python']],
  'later': 'Enzymes + NetSolP: properties     |     EvoEF1: whole-variant folding'},
 {'task': 'task_001_rml_stability',
  'title': 'RML stability',
  'approach': 'agent-with-specialist',
  'stages': [['Parent checks', 'Python · 3TGL sequence'],
             ['Generation and revision', 'SolubleMPNN'],
             ['Property screening', 'Enzymes · NetSolP'],
             ['Complex models', 'Boltz2'],
             ['Quality and exposure', 'MolProbity · PepPatch'],
             ['Review outputs', 'Native proposer + critic']],
  'footer_title': 'EXPORTED RESULTS',
  'later': 'Sequences · property screens · structural measurements · sealed shortlist'},
 {'task': 'task_002_leh_stability',
  'title': 'LEH stability',
  'approach': 'agent-with-specialist',
  'stages': [['Parent checks', 'Python · 1NWW dimer'],
             ['Generation and revision', 'SolubleMPNN'],
             ['Property screening', 'Enzymes · NetSolP'],
             ['Complex and pose models', 'Boltz2 · Vina'],
             ['Quality and exposure', 'MolProbity · PepPatch'],
             ['Review outputs', 'Native proposer + critic']],
  'footer_title': 'EXPORTED RESULTS',
  'later': 'Sequences · property screens · structural measurements · original selection'},
 {'task': 'task_005_sun_leh_pythia',
  'title': 'Sun LEH / Pythia study',
  'approach': 'agent-with-specialist',
  'stages': [['Freeze inputs', 'Python · 1NWW mapping'],
             ['Review plan', 'Native proposer + critic'],
             ['Score substitutions', 'Pythia'],
             ['Select mutation library', 'Python · summed score'],
             ['Review results', 'Native proposer + critic'],
             ['Verify and retain outputs', 'Python audit']],
  'footer_title': 'EXPORTED RESULTS',
  'later': '2755 mapped substitution scores · 33-mutation sum-score library'},
 {'task': 'task_006_zhang_hydrolases',
  'title': 'Zhang cellulase / β-glucanase study',
  'approach': 'agent-with-specialist',
  'stages': [['Freeze inputs', 'Python'],
             ['WT structures', 'AlphaFold2 / ColabFold'],
             ['WT scores', 'Pythia'],
             ['M2/M5 scores', 'ESM-2'],
             ['Review', 'Native proposer + critic']],
  'footer_title': 'EXPORTED RESULTS',
  'later': 'Pythia · ESM-2 · structure quality · published-score agreement'}]


def build_zhang(env, spec):
    """Keep WT structure scoring and stabilized-sequence scoring in separate lanes."""
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.patch.set_facecolor("white")
    ax.set(xlim=(0, 12), ylim=(0, 9))
    ax.axis("off")
    ax.text(.5, 8.45, spec["title"], fontsize=22, weight="bold", color="#16334b")
    ax.text(.5, 7.98, "SPECIALIST-ASSISTED · NATIVE PROPOSER + CRITIC" if spec.get("approach") else "AGENT ALONE · TWO SCORING BACKGROUNDS", fontsize=10,
            weight="bold", color="#647789")

    def card(x, y, width, height, title, subtitle):
        ax.add_patch(FancyBboxPatch((x, y), width, height,
                     boxstyle="round,pad=.035,rounding_size=.13",
                     facecolor="#eef5fa", edgecolor="#c5d9e8", linewidth=1.4))
        ax.text(x + width / 2, y + height * .67, title, fontsize=13,
                weight="bold", color="#16334b", ha="center", va="center")
        ax.text(x + width / 2, y + height * .27, subtitle, fontsize=10.5,
                color="#375469", ha="center", va="center")

    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                     mutation_scale=13, color="#8198aa", linewidth=1.5,
                     shrinkA=6, shrinkB=6))

    card(3.55, 6.75, 4.9, .86, "Freeze inputs", "Python · exact WT and M2/M5 sequences")
    card(.8, 5.3, 4.8, 1.05, "WT structure prediction", "AlphaFold2 / ColabFold")
    card(6.4, 5.3, 4.8, 1.05, "Stabilized sequence inputs", "Cellulase M2 · β-glucanase M5")
    card(.8, 3.85, 4.8, 1.05, "Pythia", "WT structure-conditioned mutation scores")
    card(6.4, 3.85, 4.8, 1.05, "ESM-2", "M2/M5 sequence-conditioned mutation scores")
    card(3.55, 2.35, 4.9, .95, "Verify, rank and retain outputs", "Python · keep scoring backgrounds separate")
    arrow((4.6, 6.75), (3.2, 6.35))
    arrow((7.4, 6.75), (8.8, 6.35))
    arrow((3.2, 5.3), (3.2, 4.9))
    arrow((8.8, 5.3), (8.8, 4.9))
    arrow((3.2, 3.85), (4.8, 3.3))
    arrow((8.8, 3.85), (7.2, 3.3))
    ax.add_patch(FancyBboxPatch((.5, .55), 11, 1.2,
                 boxstyle="round,pad=.035,rounding_size=.13",
                 facecolor="#fbf5e9", edgecolor="#e9d9b5"))
    ax.text(.75, 1.4, spec.get("footer_title", "LATER BENCHMARK CALCULATIONS"), fontsize=10,
            weight="bold", color="#886627")
    ax.text(.75, .93, spec["later"], fontsize=11.5, color="#5b503d")
    target = resolve_artifact(historical_result(env, spec["task"], spec.get("approach", "agent-alone")) / "figures/workflow.jpg")
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(target, dpi=140, format="jpg", pil_kwargs={"quality": 93}, facecolor="white")
    plt.close(fig)


def build(env):
    for spec in SPECS:
        if spec["task"] == "task_006_zhang_hydrolases":
            build_zhang(env, spec)
            continue
        fig, ax = plt.subplots(figsize=(12, 9))
        fig.patch.set_facecolor("#ffffff")
        ax.set(xlim=(0, 12), ylim=(0, 9))
        ax.axis("off")
        ax.text(.5, 8.45, spec["title"], fontsize=23, weight="bold", color="#16334b", va="center")
        ax.text(.5, 7.94, "SPECIALIST-ASSISTED · NATIVE PROPOSER + CRITIC" if spec.get("approach") else "FINAL METHOD PATH · AGENT ALONE", fontsize=10, weight="bold", color="#647789")
        positions = [(0.5, 5.45), (4.35, 5.45), (8.2, 5.45), (8.2, 2.95), (4.35, 2.95), (.5, 2.95)]
        edges = [(0,1),(1,2),(2,3),(3,4),(4,5)]
        width, height = 3.3, 1.6
        for i, ((stage, tool), (x,y)) in enumerate(zip(spec["stages"], positions)):
            ax.add_patch(FancyBboxPatch((x,y),width,height,boxstyle="round,pad=0.04,rounding_size=0.15",facecolor="#eef5fa",edgecolor="#c5d9e8",linewidth=1.4))
            ax.text(x+.22,y+1.18,f"{i+1:02d}",fontsize=11,weight="bold",color="#557a96")
            ax.text(x+.22,y+.83,stage,fontsize=12,weight="bold",color="#16334b")
            import textwrap
            ax.text(x+.22,y+.38,"\n".join(textwrap.wrap(tool, 29)),fontsize=10.5,color="#375469",va="center",linespacing=1.25)
        for start,end in edges:
            x,y=positions[start]; xx,yy=positions[end]
            if yy == y:
                a=(x+width,y+height/2) if xx>x else (x,y+height/2)
                b=(xx,yy+height/2) if xx>x else (xx+width,yy+height/2)
            else:
                a=(x+width/2,y);b=(xx+width/2,yy+height)
            ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=13,color="#8198aa",linewidth=1.5,shrinkA=6,shrinkB=6))
        ax.add_patch(FancyBboxPatch((.5,.55),11,1.5,boxstyle="round,pad=.04,rounding_size=.14",facecolor="#fbf5e9",edgecolor="#e9d9b5"))
        ax.text(.75,1.67,spec.get("footer_title", "LATER BENCHMARK CALCULATIONS"),fontsize=10,weight="bold",color="#886627")
        ax.text(.75,1.12,spec["later"],fontsize=12,color="#5b503d",va="center",linespacing=1.5)
        target=resolve_artifact(historical_result(env, spec["task"], spec.get("approach", "agent-alone"))/"figures"/"workflow.jpg")
        target.parent.mkdir(parents=True,exist_ok=True)
        fig.savefig(target,dpi=140,format="jpg",pil_kwargs={"quality":93},facecolor="white")
        plt.close(fig)

if __name__ == "__main__":
    build(Path(__file__).resolve().parents[1])

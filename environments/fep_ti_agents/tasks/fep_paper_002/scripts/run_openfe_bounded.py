"""Run a bounded OpenFE hybrid-topology smoke calculation for PTP1B.

This is deliberately short (3 lambda windows, one repeat, 1 ps production)
and is an execution/diagnostic artifact, not a publication-level FEP run.
Charges are read from the corrected GAFF2/AM1-BCC MOL2 files; no evaluator
answer or prepared OpenFE configuration is read by the runner.
"""
from __future__ import annotations

import json
import shutil
import argparse
from pathlib import Path

import gufe
from openfe import LomapAtomMapper, ProteinComponent, SmallMoleculeComponent, SolventComponent
from openfe.protocols.openmm_rfe import RelativeHybridTopologyProtocol

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "execution" / "openfe_bounded_run"
PARAM = ROOT / "execution" / "parameterization_corrected"


def charged_component(label: str) -> SmallMoleculeComponent:
    from openff.toolkit import Molecule
    from openff.units import unit
    from rdkit import Chem

    mol = Chem.SDMolSupplier(str(ROOT / "inputs" / f"ligand_{label}.sdf"), removeHs=False)[0]
    off = Molecule.from_rdkit(mol, allow_undefined_stereo=True)
    lines = (PARAM / f"{label}.mol2").read_text().splitlines()
    start = lines.index("@<TRIPOS>ATOM") + 1
    charges = []
    for line in lines[start:]:
        if line.startswith("@<TRIPOS>"):
            break
        charges.append(float(line.split()[-1]))
    off.partial_charges = charges * unit.elementary_charge
    return SmallMoleculeComponent.from_openff(off, name=label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--windows", type=int, default=3)
    parser.add_argument("--production-ps", type=int, default=1)
    parser.add_argument("--equilibration-ps", type=int, default=1)
    args = parser.parse_args()
    global OUT
    OUT = args.output if args.output.is_absolute() else ROOT / args.output
    OUT.mkdir(parents=True, exist_ok=True)
    a = charged_component("23477")
    b = charged_component("23482")
    protein = ProteinComponent.from_pdb_file(ROOT / "inputs" / "ptp1b_2QBS_protein.pdb")
    solvent = SolventComponent(positive_ion="Na", negative_ion="Cl")
    mapper = LomapAtomMapper(time=20, threed=True, max3d=1.0, element_change=True)
    mapping = next(mapper.suggest_mappings(a, b))

    settings = RelativeHybridTopologyProtocol.default_settings()
    settings.protocol_repeats = 1
    settings.lambda_settings.lambda_windows = args.windows
    settings.simulation_settings.n_replicas = args.windows
    settings.simulation_settings.minimization_steps = 1
    settings.simulation_settings.equilibration_length = f"{args.equilibration_ps} ps"
    settings.simulation_settings.production_length = f"{args.production_ps} ps"
    settings.simulation_settings.time_per_iteration = "1 ps"
    settings.simulation_settings.real_time_analysis_interval = f"{max(1, args.production_ps // 10)} ps"
    settings.simulation_settings.real_time_analysis_minimum_time = f"{max(1, args.production_ps // 10)} ps"
    settings.output_settings.checkpoint_interval = "1 ps"
    # This OpenMM build exposes the RTX 3060 through OpenCL, not CUDA.  Use
    # the registered GPU backend and retain the CUDA failure as provenance.
    settings.engine_settings.compute_platform = "OpenCL"
    protocol = RelativeHybridTopologyProtocol(settings)

    systems_a = list(__import__("openfe.setup.chemicalsystem_generator", fromlist=["EasyChemicalSystemGenerator"]).EasyChemicalSystemGenerator(solvent=solvent, protein=protein)(a))
    systems_b = list(__import__("openfe.setup.chemicalsystem_generator", fromlist=["EasyChemicalSystemGenerator"]).EasyChemicalSystemGenerator(solvent=solvent, protein=protein)(b))
    records = {"status": "RUNNING", "engine": "OpenFE/OpenMM", "platform": "OpenCL", "gpu_backend": "NVIDIA GeForce RTX 3060 (OpenCL)", "cuda_attempt": "FAILED_NO_REGISTERED_CUDA_PLATFORM", "mapping_atoms": len(mapping.componentA_to_componentB), "windows": args.windows, "repeat": 1, "equilibration_ps": args.equilibration_ps, "production_ps": args.production_ps, "legs": {}}

    for leg, (state_a, state_b) in zip(("solvent", "complex"), zip(systems_a, systems_b)):
        leg_dir = OUT / leg
        leg_dir.mkdir(parents=True, exist_ok=True)
        ctx_dir, scratch_dir = leg_dir / "context", leg_dir / "scratch"
        ctx_dir.mkdir(exist_ok=True)
        scratch_dir.mkdir(exist_ok=True)
        dag = protocol.create(stateA=state_a, stateB=state_b, mapping=mapping, name=f"ptp1b_23477_23482_{leg}")
        setup_u, sim_u, analysis_u = list(dag.protocol_units)
        setup = setup_u.execute(context=gufe.Context(ctx_dir, scratch_dir))
        leg_record = {"setup_ok": setup.ok(), "setup_result": str(setup)}
        if setup.ok():
            sim = sim_u.execute(context=gufe.Context(ctx_dir, scratch_dir), setup_results=setup)
            leg_record["simulation_ok"] = sim.ok()
            leg_record["simulation_result"] = str(sim)
            if sim.ok():
                analysis = analysis_u.execute(context=gufe.Context(ctx_dir, scratch_dir), simulation_results=sim)
                leg_record["analysis_ok"] = analysis.ok()
                leg_record["analysis_result"] = str(analysis)
            else:
                leg_record["simulation_exception"] = getattr(sim, "exception", None)
                leg_record["simulation_traceback"] = getattr(sim, "traceback", "")[-4000:]
        else:
            leg_record["setup_exception"] = getattr(setup, "exception", None)
            leg_record["setup_traceback"] = getattr(setup, "traceback", "")[-4000:]
        records["legs"][leg] = leg_record

    records["status"] = "EXECUTED_REVIEW"
    records["qualification"] = "REVIEW"
    records["qualification_reason"] = (
        f"{args.windows}-window GPU execution completed for both legs, but one repeat and "
        f"{args.production_ps} production samples/window do not establish convergence, "
        "replica agreement, or uncertainty; retain REVIEW."
    )
    (OUT / "run_record.json").write_text(json.dumps(records, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

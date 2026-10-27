#!/usr/bin/env python3
"""Run the actual OpenMM core MD qualification case and audit its evidence."""
from __future__ import annotations
import argparse, hashlib, json, platform, time
from pathlib import Path
from io import StringIO

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', default='results/core_openmm')
    ap.add_argument('--repeat', type=int, default=1)
    args = ap.parse_args()
    try:
        import openmm
        from openmm import unit
        from openmm.app import PDBFile, ForceField, Modeller, PME, HBonds, Simulation, DCDReporter, StateDataReporter
    except Exception as exc:
        raise SystemExit(f'OpenMM unavailable: {exc}')
    root = Path(__file__).resolve().parents[1]
    case = root / 'cases/water_box_request.json'
    seed_pdb = root / 'cases/water_box.pdb'
    out = root / args.output
    out.mkdir(parents=True, exist_ok=True)
    request = json.loads(case.read_text())
    pdb = PDBFile(str(seed_pdb))
    forcefield = ForceField('tip3p.xml')
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addSolvent(forcefield, model='tip3p', boxSize=openmm.Vec3(2.5, 2.5, 2.5)*unit.nanometer)
    result = {'task_id': request['task_id'], 'repeat': args.repeat, 'status': 'FAIL',
              'engine': 'OpenMM', 'engine_version': openmm.__version__,
              'platform': platform.platform(), 'seed': request['seed'],
              'request_sha256': hashlib.sha256(case.read_bytes()).hexdigest(),
              'structure_sha256': hashlib.sha256(seed_pdb.read_bytes()).hexdigest(),
              'atom_count': modeller.topology.getNumAtoms(), 'trajectory_frames': 0}
    dcd = out / f'repeat_{args.repeat}.dcd'; log = out / f'repeat_{args.repeat}.log'
    started = time.perf_counter()
    system = forcefield.createSystem(modeller.topology, nonbondedMethod=PME,
                                      nonbondedCutoff=1*unit.nanometer,
                                      constraints=HBonds)
    integrator = openmm.LangevinMiddleIntegrator(300*unit.kelvin, 1/unit.picosecond, 1*unit.femtosecond)
    integrator.setRandomNumberSeed(request['seed'] + args.repeat - 1)
    simulation = Simulation(modeller.topology, system, integrator)
    simulation.context.setPositions(modeller.positions)
    simulation.minimizeEnergy(maxIterations=250)
    state0 = simulation.context.getState(getEnergy=True, getPositions=True)
    e0 = state0.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    simulation.reporters.append(DCDReporter(str(dcd), 100))
    simulation.reporters.append(StateDataReporter(str(log), 100, step=True, potentialEnergy=True,
                                                   kineticEnergy=True, temperature=True, density=True,
                                                   speed=True, separator=','))
    simulation.step(request['production_steps'])
    state1 = simulation.context.getState(getEnergy=True, getPositions=True)
    e1 = state1.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    result.update({'status':'PASS', 'minimized_potential_kj_mol':float(e0),
                   'final_potential_kj_mol':float(e1), 'potential_delta_kj_mol':float(e1-e0),
                   'production_steps':request['production_steps'], 'timestep_fs':1.0,
                   'trajectory_frames':request['production_steps']//100,
                   'wall_time_s':round(time.perf_counter()-started,6),
                   'trajectory_sha256':hashlib.sha256(dcd.read_bytes()).hexdigest(),
                   'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
                   'platform_name':simulation.context.getPlatform().getName()})
    (out / f'repeat_{args.repeat}.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__': main()

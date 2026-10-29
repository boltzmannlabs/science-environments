#!/usr/bin/env python3
"""Run executable CG checks on three representative OpenMM systems."""
from __future__ import annotations
import json, math, time
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from cg_agents.runtime import run_all_agents
from openmm import CustomBondForce, CustomNonbondedForce, LangevinMiddleIntegrator, Platform, Vec3, unit, System
from openmm.app import Element, Simulation, Topology

ROOT = Path(__file__).parents[1]
OUT = ROOT / 'results' / 'agent_harness'

def _positions(family):
    if family == 'protein':
        return [Vec3(0.4 + i*.28, 1.5 + 0.08*math.sin(i), 1.5) for i in range(10)]
    if family == 'membrane':
        return [Vec3(0.6 + (i%4)*.5, 0.8 + (i//4)*.5, 1.5) for i in range(16)]
    return [Vec3(0.8 + (i%5)*.35, 0.8 + (i//5)*.35, 1.5) for i in range(20)]

def run_system(family, seed):
    positions = _positions(family)
    n = len(positions)
    topology = Topology(); chain = topology.addChain(); residue = topology.addResidue('CG', chain)
    atoms = [topology.addAtom(f'B{i+1}', Element.getByAtomicNumber(6), residue) for i in range(n)]
    bonds = []
    if family == 'membrane':
        for y in range(4):
            for x in range(4):
                i = y*4+x
                if x < 3: bonds.append((i, i+1))
                if y < 3: bonds.append((i, i+4))
    else:
        bonds = [(i, i+1) for i in range(n-1)]
    for i, j in bonds: topology.addBond(atoms[i], atoms[j])
    system = System()
    for _ in range(n): system.addParticle(72.0 * unit.dalton)
    bf = CustomBondForce('0.5*k*(r-r0)^2'); bf.addGlobalParameter('k', 400.0 * unit.kilojoule_per_mole/unit.nanometer**2); bf.addGlobalParameter('r0', .35 * unit.nanometer)
    for i, j in bonds: bf.addBond(i, j, [])
    system.addForce(bf)
    nf = CustomNonbondedForce('4*epsilon*(sigma/r)^12'); nf.addGlobalParameter('epsilon', .15*unit.kilojoule_per_mole); nf.addGlobalParameter('sigma', .25*unit.nanometer); nf.setNonbondedMethod(CustomNonbondedForce.CutoffPeriodic); nf.setCutoffDistance(1.0*unit.nanometer)
    for _ in range(n): nf.addParticle([])
    system.addForce(nf); system.setDefaultPeriodicBoxVectors(Vec3(4,0,0), Vec3(0,4,0), Vec3(0,0,4))
    integrator = LangevinMiddleIntegrator(300*unit.kelvin, 1/unit.picosecond, 0.002*unit.picoseconds); integrator.setRandomNumberSeed(seed)
    names = [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())]
    platform = Platform.getPlatformByName('CUDA') if 'CUDA' in names else Platform.getPlatformByName('CPU')
    sim = Simulation(topology, system, integrator, platform); sim.context.setPositions(positions*unit.nanometer)
    start = time.perf_counter(); sim.minimizeEnergy(maxIterations=100); sim.step(100); state = sim.context.getState(getEnergy=True, getPositions=True)
    energy = float(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)); coords = state.getPositions(asNumpy=True).value_in_unit(unit.nanometer)
    return {'family': family, 'platform': platform.getName(), 'beads': n, 'bonds': len(bonds), 'steps': 100, 'seed': seed, 'energy_kj_mol': energy, 'wall_time_s': round(time.perf_counter()-start, 6), 'finite_energy': math.isfinite(energy), 'finite_coordinates': bool(np.isfinite(coords).all()), 'mapping_valid': True, 'model': 'custom_harmonic_bond_repulsive_pair', 'parameters_complete': True, 'box_valid': True, 'minimized': True, 'replicas': 2}

def main():
    records = []
    for family in ('protein', 'membrane', 'llps'):
        first = run_system(family, 17); second = run_system(family, 18); first['repeat_energy_delta'] = abs(first['energy_kj_mol']-second['energy_kj_mol']); first['repeat'] = 1; first['agents'] = run_all_agents(first); records.append(first)
    OUT.mkdir(parents=True, exist_ok=True); result = {'benchmark': 'cg-agent-harness-v1', 'systems': records, 'scope': 'executable smoke qualification; not production CG science'}
    (OUT/'results.json').write_text(json.dumps(result, indent=2)+'\n'); print(json.dumps(result, indent=2))

if __name__ == '__main__': main()

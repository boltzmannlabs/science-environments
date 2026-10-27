#!/usr/bin/env python3
"""Execute the small, deliberately non-production CG bead-spring profile."""
import json
import time
from pathlib import Path

from openmm import CustomBondForce, CustomNonbondedForce, LangevinMiddleIntegrator, Platform, Vec3, unit
from openmm.app import Element, Simulation, Topology

OUT = Path(__file__).parents[1] / 'results' / 'toy_openmm'

def main():
    n = 8
    topology = Topology()
    chain = topology.addChain()
    residue = topology.addResidue('BEAD', chain)
    atoms = [topology.addAtom(f'B{i+1}', Element.getByAtomicNumber(6), residue) for i in range(n)]
    for i in range(n - 1):
        topology.addBond(atoms[i], atoms[i + 1])

    system = __import__('openmm').System()
    for _ in range(n):
        system.addParticle(1.0 * unit.dalton)
    bonds = CustomBondForce('0.5*k*(r-r0)^2')
    bonds.addGlobalParameter('k', 500.0 * unit.kilojoule_per_mole / unit.nanometer**2)
    bonds.addGlobalParameter('r0', 0.35 * unit.nanometer)
    for i in range(n - 1):
        bonds.addBond(i, i + 1, [])
    system.addForce(bonds)
    repulsion = CustomNonbondedForce('4*epsilon*(sigma/r)^12')
    repulsion.addGlobalParameter('epsilon', 0.2 * unit.kilojoule_per_mole)
    repulsion.addGlobalParameter('sigma', 0.30 * unit.nanometer)
    repulsion.setNonbondedMethod(CustomNonbondedForce.CutoffPeriodic)
    repulsion.setCutoffDistance(1.0 * unit.nanometer)
    for _ in range(n): repulsion.addParticle([])
    system.addForce(repulsion)
    system.setDefaultPeriodicBoxVectors(Vec3(3,0,0), Vec3(0,3,0), Vec3(0,0,3))
    integrator = LangevinMiddleIntegrator(300 * unit.kelvin, 1 / unit.picosecond, 0.002 * unit.picoseconds)
    integrator.setRandomNumberSeed(17)
    platform = Platform.getPlatformByName('CUDA') if 'CUDA' in [Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())] else Platform.getPlatformByName('CPU')
    sim = Simulation(topology, system, integrator, platform)
    positions = [Vec3(0.2 + i * 0.25, 0.2, 0.2) for i in range(n)] * unit.nanometer
    sim.context.setPositions(positions)
    start = time.perf_counter()
    sim.minimizeEnergy(maxIterations=100)
    sim.step(100)
    state = sim.context.getState(getEnergy=True, getPositions=True)
    elapsed = round(time.perf_counter() - start, 6)
    energy = state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
    result = {'status': 'PASS', 'profile': 'toy_bead_spring', 'engine': 'OpenMM', 'platform': platform.getName(), 'beads': n, 'steps': 100, 'seed': 17, 'potential_kj_mol': float(energy), 'wall_time_s': elapsed, 'qualification_scope': 'adapter smoke test only'}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'repeat_1.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()

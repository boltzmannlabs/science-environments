#!/usr/bin/env python3
"""Bounded real-system MD runs on repaired, force-field-supported structures."""
from pathlib import Path
import json, math, time
import openmm
from openmm import unit
from openmm.app import PDBFile, ForceField, Modeller, PME, HBonds, Simulation, DCDReporter, StateDataReporter

ROOT=Path(__file__).parents[1]; SRC=ROOT/'results/real_system_smoke'; OUT=ROOT/'results/real_system_production'; OUT.mkdir(parents=True,exist_ok=True)
for src in sorted(SRC.glob('*.repaired.pdb')):
    name=src.name.replace('.repaired.pdb',''); rec={'system':name,'engine':'OpenMM','engine_version':openmm.__version__,'status':'FAIL','input':str(src)}
    try:
        pdb=PDBFile(str(src)); ff=ForceField('amber14-all.xml','amber14/tip3p.xml'); modeller=Modeller(pdb.topology,pdb.positions)
        system=ff.createSystem(modeller.topology,nonbondedMethod=PME,nonbondedCutoff=1*unit.nanometer,constraints=HBonds)
        integ=openmm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,1*unit.femtosecond); integ.setRandomNumberSeed(20261028)
        platform=openmm.Platform.getPlatformByName('CUDA') if 'CUDA' in [openmm.Platform.getPlatform(i).getName() for i in range(openmm.Platform.getNumPlatforms())] else openmm.Platform.getPlatformByName('CPU')
        sim=Simulation(modeller.topology,system,integ,platform); sim.context.setPositions(modeller.positions); sim.minimizeEnergy(maxIterations=100)
        dcd=OUT/(name+'.dcd'); log=OUT/(name+'.log'); sim.reporters=[DCDReporter(str(dcd),10),StateDataReporter(str(log),10,step=True,potentialEnergy=True,temperature=True,speed=True,separator=',')]
        start=time.perf_counter(); sim.step(100); state=sim.context.getState(getEnergy=True,getPositions=True); e=float(state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole))
        rec.update(status='PASS' if math.isfinite(e) else 'FAIL',platform=platform.getName(),atoms=modeller.topology.getNumAtoms(),steps=100,final_energy_kj_mol=e,wall_time_s=round(time.perf_counter()-start,3),trajectory=str(dcd),log=str(log))
    except Exception as exc: rec['error']=f'{type(exc).__name__}: {exc}'
    (OUT/(name+'.json')).write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps(rec))

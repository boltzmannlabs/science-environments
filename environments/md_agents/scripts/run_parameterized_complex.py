#!/usr/bin/env python3
from pathlib import Path
import json, math, time
import openmm
from openmm import unit
from openmm.app import AmberPrmtopFile, AmberInpcrdFile, Simulation, DCDReporter, StateDataReporter
root=Path(__file__).parents[1]; d=root/'results/benzamidine_parameterization'
top=AmberPrmtopFile(str(d/'trypsin_benzamidine.prmtop')); inp=AmberInpcrdFile(str(d/'trypsin_benzamidine.inpcrd'))
system=top.createSystem(nonbondedMethod=openmm.app.PME, nonbondedCutoff=1*unit.nanometer, constraints=openmm.app.HBonds)
integ=openmm.LangevinMiddleIntegrator(300*unit.kelvin,1/unit.picosecond,1*unit.femtosecond); integ.setRandomNumberSeed(20261028)
platform=openmm.Platform.getPlatformByName('CUDA'); sim=Simulation(top.topology,system,integ,platform); sim.context.setPositions(inp.positions); sim.minimizeEnergy(maxIterations=1000)
dcd=d/'trypsin_benzamidine.dcd'; log=d/'trypsin_benzamidine.log'; sim.reporters=[DCDReporter(str(dcd),10),StateDataReporter(str(log),10,step=True,potentialEnergy=True,temperature=True,speed=True,separator=',')]
t=time.perf_counter(); sim.step(100); e=float(sim.context.getState(getEnergy=True).getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole))
result={'status':'PASS' if math.isfinite(e) else 'FAIL','engine':'OpenMM','platform':'CUDA','nonbonded_method':'PME','steps':100,'atoms':top.topology.getNumAtoms(),'final_energy_kj_mol':e,'wall_time_s':round(time.perf_counter()-t,3),'parameterization':'AmberTools antechamber GAFF2 AM1-BCC','net_charge_counterions':'6 Cl- added for +6 starting charge','trajectory':str(dcd),'log':str(log)}
(d/'trypsin_benzamidine_production.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))

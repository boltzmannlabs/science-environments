#!/usr/bin/env python3
"""Run a reproducible OpenMM preparation/minimization smoke test on real PDBs."""
from pathlib import Path
import json, time, math
import openmm
from openmm import unit
from openmm.app import PDBFile, ForceField, Modeller, PME, HBonds, Simulation

ROOT=Path(__file__).parents[1]
OUT=ROOT/'results/real_system_smoke'; OUT.mkdir(parents=True,exist_ok=True)
systems=['villin_headpiece.pdb','dna_duplex.pdb','barnase_barstar.pdb','trypsin_benzamidine.pdb']
for name in systems:
    path=ROOT/'src/cases/real_systems'/name; rec={'system':name,'status':'FAIL','engine':'OpenMM','engine_version':openmm.__version__,'original_input':str(path)}
    try:
        # Derive a repaired copy; never overwrite the downloaded source PDB.
        from pdbfixer import PDBFixer
        fixer=PDBFixer(filename=str(path))
        fixer.removeHeterogens(keepWater=True)
        fixer.findMissingResidues(); fixer.findMissingAtoms(); fixer.addMissingAtoms(); fixer.addMissingHydrogens(7.0)
        repaired=OUT/(name+'.repaired.pdb')
        from openmm.app import PDBFile as PDBWriter
        with repaired.open('w') as fh: PDBWriter.writeFile(fixer.topology,fixer.positions,fh)
        pdb=PDBFile(str(repaired)); ff=ForceField('amber14-all.xml','amber14/tip3p.xml')
        modeller=Modeller(pdb.topology,pdb.positions); modeller.addHydrogens(ff)
        # Keep this a bounded preparation test; no production claim is made.
        system=ff.createSystem(modeller.topology,nonbondedMethod=PME,nonbondedCutoff=1*unit.nanometer,constraints=HBonds)
        integ=openmm.VerletIntegrator(0.001*unit.picoseconds)
        sim=Simulation(modeller.topology,system,integ); sim.context.setPositions(modeller.positions)
        t=time.perf_counter(); sim.minimizeEnergy(maxIterations=25)
        state=sim.context.getState(getEnergy=True,getPositions=True)
        e=state.getPotentialEnergy().value_in_unit(unit.kilojoule_per_mole)
        atoms=modeller.topology.getNumAtoms()
        physical = math.isfinite(float(e)) and abs(float(e))/max(atoms,1) < 1e6
        rec.update(status='PASS' if physical else 'REVIEW',atoms=atoms,energy_kj_mol=float(e),wall_time_s=round(time.perf_counter()-t,3),repaired_input=str(repaired),repair='PDBFixer missing atoms/hydrogens; heterogens removed in derived copy',physical_sanity='PASS' if physical else 'FAIL')
    except Exception as exc: rec['error']=f'{type(exc).__name__}: {exc}'
    (OUT/(name+'.json')).write_text(json.dumps(rec,indent=2)+'\n'); print(json.dumps(rec))

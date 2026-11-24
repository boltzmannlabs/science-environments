#!/usr/bin/env python3
"""Materialize deterministic, task-specific diagnostic fixtures.

These fixtures make every packet executable by the harness.  They are small
diagnostic inputs, not production protein/ligand reference systems; adapters
must still qualify them scientifically before reporting PASS.
"""
from __future__ import annotations
import json, shutil
from pathlib import Path

ROOT = Path(__file__).parents[1]

PDB = """REMARK 900 MD agent diagnostic fixture; synthetic and reproducible
ATOM      1  O   HOH A   1       0.000   0.000   0.000  1.00  0.00           O
ATOM      2  H1  HOH A   1       0.957   0.000   0.000  1.00  0.00           H
ATOM      3  H2  HOH A   1      -0.239   0.927   0.000  1.00  0.00           H
END
"""
GRO = """Synthetic MD diagnostic fixture
    3
    1HOH     OW    1   0.000   0.000   0.000
    1HOH    HW1    2   0.095   0.000   0.000
    1HOH    HW2    3  -0.024   0.093   0.000
   1.00000   1.00000   1.00000
"""
MOL2 = """@<TRIPOS>MOLECULE
DIAGNOSTIC_LIGAND
 3 2 1 0 0
SMALL
@<TRIPOS>ATOM
      1 C1  0.0000  0.0000  0.0000 C.3 1 LIG 0.0
      2 O1  1.4300  0.0000  0.0000 O.3 1 LIG -0.2
      3 H1  1.8000  0.8000  0.0000 H 1 LIG 0.2
@<TRIPOS>BOND
     1 1 2 1
     2 2 3 1
"""
SDF = """diagnostic_ligand
  MDAGENT

  3  2  0  0  0  0  0  0  0  0999 V2000
    0.0000    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0
    1.4300    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0
    1.8000    0.8000    0.0000 H   0  0  0  0  0  0  0  0  0  0  0  0
  1  2  1  0  0  0  0
  2  3  1  0  0  0  0
M  END
$$$$
"""

def main() -> None:
    packets = sorted((ROOT / "src/cases/inputs").glob("MD-??/task.json"))
    made = 0
    for packet_path in packets:
        packet = json.loads(packet_path.read_text())
        fixture = packet["input"]["fixture"]
        target = ROOT / fixture
        ext = target.suffix.lower()
        if target.exists() and ext != ".parquet":
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.name == "water_box.pdb" and (ROOT / "src/cases/water_box.pdb").exists():
            shutil.copy2(ROOT / "src/cases/water_box.pdb", target)
        elif ext == ".pdb": target.write_text(PDB)
        elif ext == ".gro": target.write_text(GRO)
        elif ext == ".mol2": target.write_text(MOL2)
        elif ext == ".sdf": target.write_text(SDF)
        elif ext == ".dcd" and (ROOT / "results/core_openmm/repeat_5.dcd").exists():
            shutil.copy2(ROOT / "results/core_openmm/repeat_5.dcd", target)
        elif ext == ".itp": target.write_text("; synthetic diagnostic topology\n[ atomtypes ]\n; intentionally unresolved type for failure testing\n")
        elif ext == ".csv": target.write_text("replica,observable\n1,0.10\n2,0.11\n3,0.09\n")
        elif ext == ".parquet":
            # A real columnar fixture, intentionally marked corrupt by the
            # packet metadata rather than by using an invalid file format.
            import pandas as pd
            pd.DataFrame({"step": [0, 1, 2], "energy": [-1.0, -0.9, -0.8]}).to_parquet(target, index=False)
        else:
            target.write_text(json.dumps({"fixture": fixture, "task_id": packet["task_id"], "parameters": packet["input"]["parameters"], "provenance": "synthetic diagnostic fixture; not a reference result"}, indent=2) + "\n")
        made += 1
    print(json.dumps({"packets": len(packets), "fixtures_created": made}, indent=2))

if __name__ == "__main__": main()

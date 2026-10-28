#!/usr/bin/env bash
set -euo pipefail
base="$(cd "$(dirname "$0")/.." && pwd)"
out="$base/results/benzamidine_parameterization"
awk '($0 ~ /^ATOM/ && substr($0,18,3) != "HOH" && substr($0,13,4) !~ /H/) || $0 ~ /^TER/ || $0 ~ /^END/' "$base/results/real_system_smoke/trypsin_benzamidine.pdb.repaired.pdb" | sed 's/HIE/HIS/g; s/NILE/ILE/g' > "$out/trypsin_protein_no_waters.pdb"
cat > "$out/tleap.in" <<EOF
source leaprc.protein.ff14SB
source leaprc.gaff2
source leaprc.water.tip3p
loadamberparams $out/benzamidine.frcmod
BEN = loadmol2 $out/benzamidine.mol2
PROT = loadpdb $out/trypsin_protein_no_waters.pdb
COMPLEX = combine { PROT BEN }
check COMPLEX
solvateBox COMPLEX TIP3PBOX 10.0
addIonsRand COMPLEX Cl- 6
check COMPLEX
saveamberparm COMPLEX $out/trypsin_benzamidine.prmtop $out/trypsin_benzamidine.inpcrd
savepdb COMPLEX $out/trypsin_benzamidine.parameterized.pdb
quit
EOF
(cd "$out" && tleap -f tleap.in > tleap.log 2>&1)
echo "$out/trypsin_benzamidine.prmtop"

# Fixed-Pose CDR Side-Chain Reconstruction

## Method
For each candidate, the 1N8Z backbone (N/CA/C) is kept fixed. Each designed CDR residue's side chain is replaced with the new residue type, placed using an ideal geometry oriented so its CA->CB vector matches the original CA->CB direction. This yields a fixed-pose structure with the designed CDRs — the matched-conditions representation closest to the benchmark's fixed-pose REF15.

## Mapping
Candidate VH position i (1-based) = 1N8Z chain B residue i. Candidate VL position i = 1N8Z chain A residue i. Verified 1:1 (AB_08: VH 118/120 match, VL 102/107 match).

## Caveats
- Ideal side-chain geometry (approximate, no hydrogens). Not a full rotamer optimization.
- Intramolecular clashes from the reconstruction are reported but do not affect ProDIGy (intermolecular).
- This is an approximation for a matched-conditions binding comparison, not a physical simulation.

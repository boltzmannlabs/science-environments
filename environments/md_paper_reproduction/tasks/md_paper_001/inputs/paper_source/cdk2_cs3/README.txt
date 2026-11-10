equil_nvt_gpu.mdp, equil_npt_gpu.mdp, and equil_md_gpu.mdp: grompp input files with MD parameters for NVT, NPT, and Production run, respectively.
index.ndx: Index file
em.gro: A coordinate file after energy minimization.
topol_fin.top: Topology file
CDK2_CS3_lig_GMX_new16.itp: Topology file for ligand CS3

Executable binary files for NVT, NPT, and Production run is produced by following commands.
grompp -f equil_nvt_gpu.mdp -c em.gro -p topol_fin.top -n index.ndx -o nvt.tpr
mdrun -s nvt.tpr -deffnm nvt

grompp -f equil_npt_gpu.mdp -c nvt.gro -p topol_fin.top -n index.ndx -t nvt.cpt -o npt.tpr -maxwarn 1
mdrun -s npt.tpr -deffnm npt

grompp -f equil_md_gpu.mdp -c npt.gro -p topol_fin.top -n index.ndx -o md1.tpr -maxwarn 1



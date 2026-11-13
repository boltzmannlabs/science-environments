"""Descriptive coordinate QA of native apo monomers. No inference, docking, acceptance gates or submission.
Run with the existing scientific Python environment; preserve native PDBs unchanged.
SASA: heavy-atom Shrake-Rupley, 160 Fibonacci points, 1.4-A probe; C/N/O/S radii specified below.
Polar-neighbor flags are a contact proxy, NOT a validated buried-unsatisfied-H-bond score.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import gemmi
import numpy as np


def csv_save(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def load(path):
    st = gemmi.read_structure(str(path))
    assert len(st) == 1
    atoms = []
    residues = []
    for chain in st[0]:
        for r in chain:
            if r.het_flag != 'A':
                continue
            residues.append((chain.name, r))
            for a in r:
                if not a.element.is_hydrogen:
                    atoms.append({'chain':chain.name, 'position':r.seqid.num, 'icode':r.seqid.icode.strip(),
                                  'residue':r.name, 'atom':a.name, 'element':a.element.name,
                                  'xyz':np.array([a.pos.x,a.pos.y,a.pos.z]), 'B':a.b_iso})
    lookup = {(a['position'],a['atom']):a['xyz'] for a in atoms}
    assert np.isfinite(np.array([a['xyz'] for a in atoms])).all()
    return atoms, residues, lookup


def fit(x, y):
    xc, yc = x.mean(axis=0), y.mean(axis=0)
    u, _, vt = np.linalg.svd((x-xc).T @ (y-yc))
    rotation = u @ np.diag([1.,1.,np.linalg.det(u@vt)]) @ vt
    rmsd = float(np.sqrt(np.mean(np.sum(((x-xc)@rotation+yc-y)**2, axis=1))))
    return rotation, xc, yc, rmsd


def sasa(atoms):
    xyz = np.array([a['xyz'] for a in atoms])
    radii = np.array([{'C':1.70,'N':1.55,'O':1.52,'S':1.80}[a['element']]+1.4 for a in atoms])
    n = 160
    i = np.arange(n)
    z = 1-2*(i+0.5)/n
    theta = i*math.pi*(3-math.sqrt(5))
    sphere = np.column_stack((np.sqrt(1-z*z)*np.cos(theta),np.sqrt(1-z*z)*np.sin(theta),z))
    d2 = ((xyz[:,None,:]-xyz[None,:,:])**2).sum(-1)
    result = []
    for j in range(len(atoms)):
        ns = np.where((d2[j] < (radii[j]+radii)**2) & (np.arange(len(atoms)) != j))[0]
        pts = xyz[j]+sphere*radii[j]
        buried = np.any(np.sum((pts[:,None,:]-xyz[ns][None,:,:])**2,axis=2)<radii[ns][None,:]**2,axis=1)
        result.append(float(4*math.pi*radii[j]**2*(1-buried.mean())))
    return np.array(result), d2


def main(root):
    manifest = json.loads((root/'structure_evidence/revision2_apo_analysis_manifest.json').read_text())
    sequence_rows = list(csv.DictReader((root/'candidate_history.csv').open()))
    seqs = {r['candidate_id']:r['sequence'] for r in sequence_rows}
    parent_id = sequence_rows[0]['candidate_id']
    _, _, parent = load(root/'structure_evidence/parent_monomer_native.pdb')
    _, _, crystal = load(root.parent/'input_bundle/sources/3TGL.pdb')
    core = [p for p in range(5,270) if not 82 <= p <= 96]
    lid = list(range(82,97))
    # Algorithm self-check on a synthetic rigid transform, not biological data.
    test = np.array([[0.,0.,0.],[1.,0.,0.],[0.,2.,0.],[0.,0.,3.]])
    q = np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
    assert fit(test@q+np.array([3.,2.,1.]),test)[3] < 1e-10
    outdir = root/'structure_evidence/revision2_apo_descriptives'
    outdir.mkdir(exist_ok=True)
    summaries = []
    details = []
    for m in manifest['models']:
        cid = m['candidate_id']
        source = root/m['evidence_pdb']
        atoms, residues, lookup = load(source)
        seq = ''.join(gemmi.find_tabulated_residue(r.name).one_letter_code for _,r in residues)
        assert seq == seqs[cid] and len(residues) == 269
        assert [r.seqid.num for _,r in residues] == list(range(1,270))
        x = np.array([lookup[p,'CA'] for p in core])
        lid_x = np.array([lookup[p,'CA'] for p in lid])
        fits = {}
        for name, ref in [('predicted_parent',parent),('closed_crystal_3TGL',crystal)]:
            y = np.array([ref[p,'CA'] for p in core])
            r, xc, yc, rmsd = fit(x,y)
            lid_y = np.array([ref[p,'CA'] for p in lid])
            lid_rmsd = float(np.sqrt(np.mean(np.sum(((lid_x-xc)@r+yc-lid_y)**2,axis=1))))
            fits[name] = {'core_CA_RMSD_A':rmsd,'lid_CA_RMSD_after_core_fit_A':lid_rmsd,'core_count':len(core),'lid_count':len(lid)}
        access, d2 = sasa(atoms)
        atom_rows = []
        polar_flags = []
        hydro_total = 0.
        for i,a in enumerate(atoms):
            aa = gemmi.find_tabulated_residue(a['residue']).one_letter_code
            if aa in 'AVILMFWY':
                hydro_total += access[i]
            partners = []
            if a['element'] in ['N','O']:
                partners = [j for j,b in enumerate(atoms) if b['element'] in ['N','O'] and
                            (b['chain'],b['position'],b['icode']) != (a['chain'],a['position'],a['icode']) and
                            d2[i,j] <= 3.5**2]
                if access[i] <= 1.0 and not partners:
                    polar_flags.append({'position':a['position'],'residue':a['residue'],'atom':a['atom'],'sasa_A2':float(access[i])})
            atom_rows.append({k:a[k] for k in ['chain','position','icode','residue','atom','element']} |
                             {'sasa_A2':float(access[i]),'other_residue_NO_within_3_5A':len(partners) if a['element'] in ['N','O'] else ''})
        csv_save(outdir/f'{cid}_atom_accessibility.csv',atom_rows)
        ca_conf = [{'position':r.seqid.num,'residue':r.name,'native_CA_B_confidence':next(a.b_iso for a in r if a.name=='CA')}
                   for _,r in residues]
        csv_save(outdir/f'{cid}_residue_confidence.csv',ca_conf)
        distance = lambda p,a,q,b: float(np.linalg.norm(lookup[p,a]-lookup[q,b]))
        network = {'Ser144_OG_His257_NE2_A':distance(144,'OG',257,'NE2'),
                   'His257_ND1_Asp203_OD1_A':distance(257,'ND1',203,'OD1'),
                   'His257_ND1_Asp203_OD2_A':distance(257,'ND1',203,'OD2'),
                   'Cys29_SG_Cys268_SG_A':distance(29,'SG',268,'SG'),
                   'Cys40_SG_Cys43_SG_A':distance(40,'SG',43,'SG'),
                   'Cys235_SG_Cys244_SG_A':distance(235,'SG',244,'SG')}
        entry = {'candidate_id':cid,'source_PDB':m['evidence_pdb'],'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'sequence_exact':True,'core_and_lid_fits':fits,'measurements':network,
                 'heavy_atom_SASA_A2':float(access.sum()),'hydrophobic_residue_SASA_A2_AVILMFWY':float(hydro_total),
                 'buried_NO_without_other_residue_NO_neighbor_3_5A':polar_flags,
                 'lowest_native_CA_confidences':sorted(ca_conf,key=lambda x:x['native_CA_B_confidence'])[:10],
                 'not_a_substrate_complex':True,'catalytic_acceptance_ranges':None,
                 'missing_required_evidence':['substrate pose and atom map','protein-ligand clashes and ligand quality','substrate carbonyl/oxyanion geometry','prepared-state protonation where native H absent','positioned deacylation water evidence']}
        details.append(entry)
        summaries.append({'candidate_id':cid,'native_pLDDT':m['native_pLDDT'],'native_pTM':m['native_pTM'],
                          'core_CA_RMSD_to_parent_A':fits['predicted_parent']['core_CA_RMSD_A'],
                          'lid_CA_RMSD_to_parent_after_core_fit_A':fits['predicted_parent']['lid_CA_RMSD_after_core_fit_A'],
                          'lid_CA_RMSD_to_closed_crystal_after_core_fit_A':fits['closed_crystal_3TGL']['lid_CA_RMSD_after_core_fit_A'],
                          'heavy_atom_SASA_A2':float(access.sum()),'hydrophobic_residue_SASA_A2_AVILMFWY':float(hydro_total),
                          'buried_NO_neighbor_proxy_count':len(polar_flags),
                          'minimum_CA_confidence':min(x['native_CA_B_confidence'] for x in ca_conf),**network})
    p = summaries[0]
    assert p['candidate_id'] == parent_id
    for s in summaries:
        s['hydrophobic_residue_SASA_delta_vs_parent_A2'] = s['hydrophobic_residue_SASA_A2_AVILMFWY']-p['hydrophobic_residue_SASA_A2_AVILMFWY']
        s['buried_NO_neighbor_proxy_delta_vs_parent'] = s['buried_NO_neighbor_proxy_count']-p['buried_NO_neighbor_proxy_count']
    csv_save(outdir/'summary.csv',summaries)
    report = {'method':'Native apo coordinate analysis; no structure prediction or docking',
              'software':{'numpy':np.__version__,'gemmi':gemmi.__version__},
              'SASA':{'method':'heavy-atom Shrake-Rupley','points_per_atom':160,'probe_radius_A':1.4,
                      'vdw_radii_A':{'C':1.70,'N':1.55,'O':1.52,'S':1.80}},
              'core_fit':'C-alpha positions5-269 excluding82-96, identical mapping and Kabsch fit for every model',
              'lid':'Positions82-96; displacement is descriptive, not a requirement to stay closed',
              'polar_proxy':'N/O heavy atoms with SASA<=1 A2 and no N/O from another residue within3.5 A. No donor/acceptor typing or hydrogen angle; not a true unsatisfied-H-bond score or acceptance gate.',
              'geometry':'Distances in angstrom; no catalytic bounds or inferred rate',
              'synthetic_rigid_fit_selftest':'passed','model_count':len(details),'models':details}
    (outdir/'measurements.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'models_analyzed':len(details),'summary_csv':str(outdir/'summary.csv'),'measurements_json':str(outdir/'measurements.json'),'all_sequences_exact':True,'synthetic_fit_test':'passed'},indent=2))

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    main(p.parse_args().root.resolve())

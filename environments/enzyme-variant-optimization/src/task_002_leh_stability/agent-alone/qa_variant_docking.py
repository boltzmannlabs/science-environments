"""Inspect native ligand poses and assemble exact-coordinate review scenes; no sampling/preparation/dispatch."""
import pathlib,json,zipfile,io,csv,hashlib,copy,math
import numpy as np
import gemmi
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
R=pathlib.Path(__file__).resolve().parent
ref=Chem.MolFromSmiles(json.loads((R/'DOCKING_PROTOCOL.json').read_text())['smiles'])
canon=Chem.MolToSmiles(ref); ref_names={x['reference_smiles_index']:x['GH9_atom_name'] for x in json.loads((R/'structure_evidence/parent_siteA_docking_QA.json').read_text())['measurements'][0]['mapping']}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
def xyz(a):return np.array([a.pos.x,a.pos.y,a.pos.z])
def dist(a,b):return float(np.linalg.norm(a-b))
def angle(a,b,c):
 u=a-b;v=c-b
 return float(np.degrees(np.arccos(np.clip(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v),-1,1))))

J=json.loads((R/'jobs.json').read_text()); groups={}; allrows=[]; completed=[]
for a in J['attempts']:
 if a.get('native_session_id')!='RUN_0002' or a['job_name']!='Vina_basic_docking':continue
 aid=a['attempt_id']; folder=R/'raw'/aid; sdf=list(folder.glob('*_docking_sdf.zip')); js=list(folder.glob('*_docking_results.json')); cs=list(folder.glob('*_docking_res.csv'))
 if not(sdf and js and cs):continue
 target=a['experiment_data']['target_name']; cid,site=target.split('_site'); receptor=R/f'prepared/{cid}_dimer_reference_waters.pdb'; s=gemmi.read_structure(str(receptor)); lookup={(ch.name,res.seqid.num,res.seqid.icode.strip(),at.name):xyz(at) for ch in s[0] for res in ch for at in res}; water=[xyz(at) for ch in s[0] if ch.name==site for res in ch if res.name=='HOH' for at in res if at.element.name=='O']; assert len(water)==1; w=water[0]
 native=json.loads(js[0].read_text()); table=list(csv.DictReader(cs[0].open())); records=[]; molecules={}; idx=0
 with zipfile.ZipFile(sdf[0]) as z:
  for member in z.namelist():
   if not member.endswith('.sdf'):continue
   for m in Chem.ForwardSDMolSupplier(io.BytesIO(z.read(member)),removeHs=False):
    assert m is not None and Chem.MolToSmiles(m)==canon
    stereo=Chem.Mol(m);Chem.AssignStereochemistryFrom3D(stereo,replaceExistingTags=True);assert Chem.MolToSmiles(stereo)==canon
    assert rdMolDescriptors.CalcMolFormula(m)=='C10H16O' and Chem.GetFormalCharge(m)==0 and m.GetNumHeavyAtoms()==11
    maps=m.GetSubstructMatches(ref,useChirality=True,uniquify=False);assert len(maps)==1;mp=maps[0];conf=m.GetConformer(); positions={ref_names[i]:np.array(conf.GetAtomPosition(j)) for i,j in enumerate(mp)}
    pose=int(m.GetProp('Pose'));score=float(m.GetProp('Score')); row=next(x for x in table if int(x['Pose'])==pose-1); nrow=next(x for x in native.values() if isinstance(x,dict) and x.get('Pose')==pose-1)
    assert float(row['Score'])==score==nrow['Score'] and row['NAMES']==nrow['NAMES']=='cis_plus_LEO_GH9' and row['SMILES']==nrow['SMILES']==json.loads((R/'DOCKING_PROTOCOL.json').read_text())['smiles']
    o,c1,c2=positions['O'],positions['C6'],positions['C8'];get=lambda res,atom:lookup[(site,res,'',atom)]
    geometry={'Asp101_OD1_epoxide_O_A':dist(get(101,'OD1'),o),'Asp101_OD2_epoxide_O_A':dist(get(101,'OD2'),o),'water_O_C1_A':dist(w,c1),'water_O_C2_A':dist(w,c2),'water_C1_O_deg':angle(w,c1,o),'water_C2_O_deg':angle(w,c2,o)}
    for res,atoms in [(53,['OH']),(55,['OD1']),(132,['OD1','OD2'])]:
     for atom in atoms:geometry[f'water_O_{res}_{atom}_A']=dist(w,get(res,atom))
    for ar in ['NE','NH1','NH2']:
     for dr in [101,132]:
      for at in ['OD1','OD2']:geometry[f'Arg99_{ar}_Asp{dr}_{at}_A']=dist(get(99,ar),get(dr,at))
    mapping=[{'reference_smiles_index':i,'pose_atom_index':j,'GH9_atom_name':ref_names[i],'element':m.GetAtomWithIdx(j).GetSymbol(),'xyz':positions[ref_names[i]].tolist()} for i,j in enumerate(mp)]
    r={'native_SDF_pose':pose,'native_table_pose':pose-1,'score':score,'score_unit':None,'SDF_member':member,'graph_charge_formula_encoded_and_coordinate_stereo_match':True,'explicit_H_atoms':sum(at.GetAtomicNum()==1 for at in m.GetAtoms()),'mapping':mapping,'geometry':geometry};records.append(r);molecules[pose]=positions
 assert len(records)==len(table)==len(native) and len({x['native_SDF_pose'] for x in records})==len(records)
 primary=min(records,key=lambda x:(x['score'],x['native_SDF_pose']));out={'candidate_id':cid,'site':site,'attempt_id':aid,'doc_id':a['doc_id'],'receptor_path':str(receptor),'receptor_sha256':sha(receptor),'artifacts':[{'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in [sdf[0],js[0],cs[0]]],'pose_count':len(records),'all_actual_SDF_chemical_states_match':True,'all_native_pose_ID_offsets_verified':True,'primary_policy':'native lowest score, not catalytic proximity','primary_SDF_pose':primary['native_SDF_pose'],'measurements':records,'catalytic_bounds':None,'reactive_protonation_and_water_H':None,'geometry_source':'Unchanged submitted receptor and actual native SDF; processed worker receptor not returned.'}
 save(R/f'structure_evidence/{cid}/site{site}_docking_QA.json',out)
 groups.setdefault(cid,{})[site]=(out,molecules[primary['native_SDF_pose']]);completed.append({'candidate_id':cid,'site':site,'attempt_id':aid,'pose_count':len(records),'primary':{k:primary[k] for k in ['native_SDF_pose','score','geometry']}})
 for row in records:allrows.append({'candidate_id':cid,'site':site,'attempt_id':aid,**{k:row[k] for k in ['native_SDF_pose','native_table_pose','score']},**row['geometry']})
scenes=[]
for cid,sites in groups.items():
 if set(sites)!=set('AB'):continue
 p=R/f'prepared/{cid}_dimer_reference_waters.pdb';s=gemmi.read_structure(str(p)); old={(ch.name,res.seqid.num,res.seqid.icode.strip(),res.name,a.name,a.element.name):xyz(a).tolist() for ch in s[0] for res in ch for a in res}
 ligands=[]
 for site,chain,num in [('A','C',901),('B','D',902)]:
  out,pos=sites[site];ch=gemmi.Chain(chain);res=gemmi.Residue();res.name='GH9';res.seqid=gemmi.SeqId(num,' ');res.het_flag='H'
  for name,coord in pos.items():
   at=gemmi.Atom();at.name=name;at.element=gemmi.Element('O' if name=='O' else 'C');at.pos=gemmi.Position(*coord);at.occ=1;at.b_iso=0;res.add_atom(at)
  ch.add_residue(res);s[0].add_chain(ch);ligands.append({'site':site,'chain_id':chain,'residue_number':num,'attempt_id':out['attempt_id'],'native_SDF_pose':out['primary_SDF_pose'],'mapping':next(x['mapping'] for x in out['measurements'] if x['native_SDF_pose']==out['primary_SDF_pose'])})
 scene=R/f'structure_evidence/{cid}/{cid}_native_primary_pair_no_crystal_symmetry_for_review.cif'; doc=s.make_mmcif_document(); block=doc.sole_block(); block.set_mmcif_category('_cell.',{}); block.set_mmcif_category('_symmetry.',{}); doc.write_file(str(scene));back=gemmi.read_structure(str(scene));new={(ch.name,res.seqid.num,res.seqid.icode.strip(),res.name,a.name,a.element.name):xyz(a).tolist() for ch in back[0] for res in ch for a in res}
 assert all(k in new and new[k]==v for k,v in old.items()) and len(new)==len(old)+22
 for lig in ligands:
  for m in lig['mapping']:assert new[(lig['chain_id'],lig['residue_number'],'','GH9',m['GH9_atom_name'],m['element'])]==m['xyz']
 manifest={'candidate_id':cid,'path':str(scene),'sha256':sha(scene),'receptor_path':str(p),'receptor_sha256':sha(p),'receptor_atoms_retained':len(old),'all_original_receptor_atoms_and_coordinates_preserved':True,'native_ligand_atoms_retained':22,'ligands':ligands,'interpretation':'Coordinate-preserving submitted receptor plus separate native score-primary A/B poses. Not jointly docked/relaxed/protonated; native processed receptor and water H remain unobserved. New distinct input requiring own review.','review_status':'NOT_APPROVED_NOT_UPLOADED','dictionary':'chemistry_sources/GH9.cif','dictionary_sha256':sha(R/'chemistry_sources/GH9.cif'),'hydrogens_added':False,'restraints_generated':False}
 save(R/f'structure_evidence/{cid}/native_primary_pair_review_manifest.json',manifest);scenes.append({k:manifest[k] for k in ['candidate_id','path','sha256','receptor_sha256']})
save(R/'variant_docking_summary.json',{'sites':completed,'scenes':scenes,'total_poses':sum(x['pose_count'] for x in completed),'completed_site_count':len(completed),'complete_candidate_pair_count':len(scenes),'all_descriptive_no_catalytic_pass_claim':True})
if allrows:
 with (R/'variant_docking_measurements.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(allrows[0]));w.writeheader();w.writerows(allrows)
print(json.dumps({'sites':len(completed),'candidate_pairs':len(scenes),'poses':sum(x['pose_count'] for x in completed),'primary_scores':[(x['candidate_id'],x['site'],x['primary']['score']) for x in completed]},indent=2))

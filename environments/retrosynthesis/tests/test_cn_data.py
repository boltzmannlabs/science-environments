"""Private source loading and public outcome-free grouped data contracts."""
import csv
import hashlib
import io
from copy import deepcopy

import pytest
from synthesis_route_gym.cn_data import (
    SOURCE_HEADERS, load_cn_records, public_cn_records, frozen_split,
)


def source_row(**updates):
    row=dict.fromkeys(SOURCE_HEADERS,'')
    row.update({'Source':'JNJ HTE 2024','Aryl SMILES':'Clc1ccccc1','Amine SMILES':'CN',
        'Catalyst SMILES':'[Pd]','Base SMILES':'N','Solvent SMILES':'O',
        'Product SMILES':'CNc1ccccc1','Yield':'10','labels':'1'})
    row.update({key:'0' for key in SOURCE_HEADERS if key.startswith('Additive_')})
    return {**row,**updates}


def load(tmp_path,rows,headers=SOURCE_HEADERS):
    data=io.StringIO(newline=''); writer=csv.DictWriter(data,fieldnames=headers)
    writer.writeheader();writer.writerows(rows)
    raw=data.getvalue().encode();path=tmp_path/'source.csv';path.write_bytes(raw)
    return load_cn_records(path,hashlib.sha256(raw).hexdigest())


def test_load_private_records_and_public_projection(tmp_path):
    records,audit=load(tmp_path,[source_row()])
    assert len(records)==1 and records[0]['label']==1
    assert records[0]['reported_response']==10
    assert audit['retained_records']==1
    assert audit['endpoint']=='reported_source_response_greater_than_or_equal_to_10'
    public=public_cn_records(records)
    assert 'label' not in public[0] and 'reported_response' not in public[0]
    assert 'source_index' not in public[0]
    assert public[0]['record_id']==records[0]['record_id']
    public[0]['aryl']='changed'
    assert records[0]['aryl']=='Clc1ccccc1'


def test_input_identity_and_public_projection_do_not_depend_on_outcomes(tmp_path):
    first,_=load(tmp_path,[source_row(Yield='0',labels='0')])
    second,_=load(tmp_path,[source_row(Yield='60',labels='1')])
    assert first[0]['record_id']==second[0]['record_id']
    assert public_cn_records(first)==public_cn_records(second)


def test_exact_ten_and_above_100_response_preserved_as_binary_measurement(tmp_path):
    records,audit=load(tmp_path,[source_row(Yield='125',labels='1')])
    assert records[0]['reported_response']==125
    assert audit['responses_above_100']==1
    with pytest.raises(ValueError,match='label'):
        load(tmp_path,[source_row(Yield='10',labels='0')])


def test_source_filter_does_not_parse_other_source_outcomes(tmp_path):
    records,audit=load(tmp_path,[source_row(Source='Dreher Doyle 2018',Yield='hidden',labels='hidden'),source_row()])
    assert len(records)==1 and records[0]['source_index']==1
    assert audit['source_counts']=={'Dreher Doyle 2018':1,'JNJ HTE 2024':1}


def test_input_only_exclusions_and_canonical_duplicates(tmp_path):
    rows=[source_row(),source_row(**{'Aryl SMILES':'c1ccccc1Cl','Yield':'0','labels':'0'}),
        source_row(**{'Solvent SMILES':''}),source_row(**{'Amine SMILES':'bad-smiles'}),
        source_row(**{'Product SMILES':'CCO'}),source_row(Additive_present='1')]
    records,audit=load(tmp_path,rows)
    assert len(records)==1 and records[0]['source_index']==0
    assert audit['replicate_records_removed']==1
    assert audit['input_exclusions']=={'missing_structure':1,'invalid_structure':1,
        'outside_cn_domain':1,'unknown_additive_composition':1}


@pytest.mark.parametrize('field,value',[('Yield','nan'),('Yield','inf'),('Yield','-1'),
    ('Yield',''),('labels','nan'),('labels','2'),('labels','')])
def test_invalid_outcomes_fail_whole_source_not_selective_drop(tmp_path,field,value):
    with pytest.raises(ValueError): load(tmp_path,[source_row(**{field:value})])


def test_fingerprint_and_schema_fail_before_loading(tmp_path):
    path=tmp_path/'source.csv';path.write_text('unexpected\nvalue\n')
    with pytest.raises(ValueError,match='digest'):load_cn_records(path,'0'*64)
    with pytest.raises(ValueError,match='schema'):load_cn_records(path,hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):load_cn_records(path,'not-a-digest')


def grouped_records(n=40):
    return tuple({'record_id':f'r{i}-{j}','group_id':f'g{i}','label':i%2,
        'reported_response':float(i),'source_index':i*2+j,
        'aryl':'Clc1ccccc1','amine':'CN','catalyst':'[Pd]','base':'N','solvent':'O',
        'product':'C'*(i+1)} for i in range(n) for j in range(2))


def test_group_split_is_frozen_and_outcome_independent():
    records=grouped_records();before=deepcopy(records)
    split=frozen_split(records)
    assert set(split)=={'train','development','calibration','assessment'}
    assert {k:len(v) for k,v in split.items()}=={'train':48,'development':12,'calibration':8,'assessment':12}
    assert sorted(i for v in split.values() for i in v)==list(range(len(records)))
    groups=[{records[i]['group_id'] for i in indices} for indices in split.values()]
    assert all(not a&b for i,a in enumerate(groups) for b in groups[i+1:])
    changed=tuple({**r,'label':1-r['label'],'reported_response':100-r['reported_response']} for r in records)
    assert frozen_split(changed)==split
    assert records==before


def test_split_requires_sufficient_groups_and_unique_records():
    with pytest.raises(ValueError):frozen_split(grouped_records(19))
    with pytest.raises(ValueError):frozen_split((*grouped_records(),grouped_records()[0]))


def test_nonchiral_product_scaffold_keeps_variants_together(tmp_path):
    rows=[source_row(),source_row(**{'Aryl SMILES':'Clc1ccc(F)cc1','Product SMILES':'CNc1ccc(F)cc1'})]
    records,_=load(tmp_path,rows)
    assert len(records)==2
    assert records[0]['group_id']==records[1]['group_id']


def test_split_rejects_one_product_assigned_contradictory_groups():
    records=grouped_records()
    bad=({**records[0],'product':records[-1]['product']},*records[1:])
    with pytest.raises(ValueError,match='product'):
        frozen_split(bad)


def test_real_loader_split_keeps_product_scaffolds_disjoint(tmp_path):
    rows=[]
    # Ring sizes vary scaffold identity; each input pair has two solvent conditions.
    for ring_size in range(3,23):
        ring='C2'+'C'*(ring_size-1)+'2'
        for solvent in ('O','CO'):
            rows.append(source_row(**{'Aryl SMILES':'Clc1ccc('+ring+')cc1',
                'Product SMILES':'CNc1ccc('+ring+')cc1','Solvent SMILES':solvent}))
    records,audit=load(tmp_path,rows)
    assert audit['group_count']==20 and len(records)==40
    split=frozen_split(records)
    scaffold_sets=[{records[i]['group_id'] for i in indices} for indices in split.values()]
    assert all(not a&b for j,a in enumerate(scaffold_sets) for b in scaffold_sets[j+1:])
    assert sorted(i for indices in split.values() for i in indices)==list(range(40))

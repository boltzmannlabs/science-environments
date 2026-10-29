"""Selection uses input descriptors and retains inventory siblings together."""
import pytest
from synthesis_route_gym.development_design import select_route_groups


def rows():
    targets = ['CCO','CCCCO','C[C@H](O)F','CCC[C@H](O)F','CCCCCCO']
    return [{'task_id':f't{i}-{stock}','target':target,'partition':'development',
             'track':'reference_route','inventory_exclusions':[] if stock == 'full' else ['O']}
            for i,target in enumerate(targets) for stock in ('full','restricted')]


def test_selection_is_order_independent_grouped_and_input_only():
    first = select_route_groups(rows(), 4)
    assert first == select_route_groups(list(reversed(rows())), 4)
    assert len(first) == 4
    assert all(len(group['task_ids']) == 2 for group in first)
    assert len({group['group_id'] for group in first}) == 4
    assert any(group['has_stereochemistry'] for group in first)
    assert any(not group['has_stereochemistry'] for group in first)


@pytest.mark.parametrize('change',[{'partition':'final'},{'reference_route':{}},{'outcomes':{}}, {'target':'invalid'}])
def test_development_selection_rejects_nonpublic_or_wrong_partition(change):
    raw = rows()
    raw[0] = {**raw[0], **change}
    with pytest.raises(ValueError):
        select_route_groups(raw,4)


def test_group_count_and_duplicate_identity_are_checked():
    with pytest.raises(ValueError):
        select_route_groups(rows(), 10)
    with pytest.raises(ValueError):
        select_route_groups(rows()+[rows()[0]],4)

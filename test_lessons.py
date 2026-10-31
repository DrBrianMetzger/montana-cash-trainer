from cash_lessons import LESSONS, evaluate, scenario
import pytest

def test_unique_scenarios_and_feedback():
    ids=[]
    for group,items in LESSONS.items():
        assert len(items)>=3
        for item in items:
            ids.append(item['id'])
            assert scenario(item['id']) == (group,item)
            assert item['preferred'] and set(item['preferred'])<=set(item['options'])
            assert set(item['options'])==set(item['feedback'])
            for choice in item['options']:
                result=evaluate(item,choice)
                assert result['preferred']==(choice in item['preferred'])
                assert result['explanation']
    assert len(ids)==len(set(ids))

def test_invalid_action_rejected():
    with pytest.raises(ValueError):
        evaluate(LESSONS['Preflop Discipline'][0], 'All in')

import sys
from unittest.mock import MagicMock
sys.modules.setdefault('streamlit',MagicMock())
from helena_course import LESSONS, scenario, a4_scenario, card_html

def test_curriculum():
    assert len(LESSONS)==8
    assert all(len(items)>=2 for items in LESSONS.values())

def test_determinism_and_actions():
    for lesson in LESSONS:
        a=scenario(103,lesson,1)
        b=scenario(103,lesson,2)
        assert a==scenario(103,lesson,1)
        assert a['question']!=b['question']
        assert a['baseline'] in a['actions']
        assert b['baseline'] in b['actions']

def test_suits_preserve_rainbow_and_suitedness():
    for seed in range(50):
        s=scenario(seed,'Missing the Flop',0)
        cards=s['hand'].split()
        assert cards[0][-1]==cards[1][-1]
        board=s['board'].split()
        assert len({x[-1] for x in board})==3

def test_a4_scenario_pot_math():
    pre=a4_scenario(1,'Preflop')
    flop=a4_scenario(1,'Flop')
    assert pre['pot']==36
    assert flop['pot'] in (71,106)
    assert pre['baseline'] in pre['actions']
    assert flop['baseline'] in flop['actions']
    assert 'HYPOTHETICAL' in pre['question']

def test_html_escape():
    assert '<script>' not in card_html('<script>')

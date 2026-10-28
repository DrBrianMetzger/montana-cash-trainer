import json
import pytest
from game_engine import Game
from training_db import TrainingDB
from personas import DEFAULTS, default_profile, validate_profile

def test_fold_ends_hand():
    g=Game();g.act('Fold');assert g.ended and not g.legal()
def test_call_updates_pot_and_response():
    g=Game();g.act('Call');assert g.pot==4 and g.hero_stack==398
    g.opponent('Check');assert g.street=='Flop'
def test_raise_changes_pot_and_opponent():
    g=Game();g.act('Raise',6);assert g.pot==8 and g.to_act=='villain'
    g.opponent('Call');assert g.pot==12 and g.street=='Flop'
def test_check_not_bet():
    g=Game();g.act('Call');g.opponent('Check');p=g.pot
    g.act('Check');assert g.pot==p and g.to_act=='villain'
def test_illegal_and_cap_block():
    g=Game();
    with pytest.raises(ValueError):g.act('Check')
    with pytest.raises(ValueError):g.act('Raise',800)
def test_db_roundtrip(tmp_path):
    a=TrainingDB(tmp_path/'a.sqlite');s=a.start_session('pluribus_prediction')
    assert a.save_prediction(s,'h|4','Fold','Bet / raise','Flop')
    assert not a.save_prediction(s,'h|4','Fold','Bet / raise','Flop')
    a.save_reference({'id':'abc','board':'KsKc5d','image_b64':'Zm9v','frequencies':{'Check':100}})
    b=TrainingDB(tmp_path/'b.sqlite');b.restore(a.backup())
    assert len(b.rows('pluribus_predictions'))==1
    assert b.references()[0]['image_b64']=='Zm9v'
    assert json.loads(b.backup())['version']==1

def test_profiles():
    for name in DEFAULTS: assert validate_profile(default_profile(name))['name']==name

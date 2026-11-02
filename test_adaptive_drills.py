import sys, types
try:
    import streamlit
except ImportError:
    sys.modules["streamlit"] = types.ModuleType("streamlit")
from datetime import date
from drill_engine import generate, categories, due_date, record_context, summary, pick_category

def test_generates_every_category():
    for cat in categories():
        s=generate(cat,seed=19)
        assert s['lesson']==cat and s['baseline'] in s['actions']
        assert s['source_type']=='heuristic_coaching'
        assert len(s['hand'].split())==2

def test_repeatability():
    assert generate(categories()[0],seed=55)==generate(categories()[0],seed=55)

def test_spaced_review():
    today=date(2026,11,1)
    assert due_date(today,False,0)=='2026-11-02'
    assert due_date(today,True,2)=='2026-11-08'

def test_record_and_summary():
    s=generate(categories()[0],seed=3)
    c=record_context(s,s['baseline'],'High',[],date(2026,11,1))
    assert c['matches_baseline'] and c['review_due']=='2026-11-02'
    stats=summary([c],date(2026,11,2))
    assert stats[s['lesson']]['due']==1

def test_unseen_prioritized():
    assert pick_category([],today=date(2026,11,1)) in categories()

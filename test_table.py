from table_engine import Table,CAP

def test_default_table():
    t=Table(seed=2)
    assert t.n==8 and t.pot>=300 and len(t.seats[0].cards)==2
    assert len({c for s in t.seats for c in s.cards})==16

def test_nine_and_shill():
    t=Table(9,True,seed=3)
    assert len(t.seats)==9
    assert t.seats[-1].house and t.seats[-1].stack<=20000
    assert t.house_buyins==20000

def test_fold_ends_when_only_one_left():
    t=Table(4,seed=1)
    for i in range(1,4):t.seats[i].folded=True
    t.pending=[0];t.to_act=0
    if 'Fold' in t.legal(0):
        t.act(0,'Fold')
        assert t.ended

def test_cap_never_exceeded_in_hero_bet():
    t=Table(4,seed=4)
    if t.ended:return
    t.to_act=0;t.pending=[0]
    t.highest=t.seats[0].street
    t.pot=79500
    if 'Bet' in t.legal(0):
        try:t.act(0,'Bet',200)
        except ValueError:pass
    assert t.pot<=CAP

def test_position_labels():
    for n in range(4,10):
        t=Table(n,seed=1)
        labels=[t.position(i) for i in range(n)]
        assert len(labels)==len(set(labels))
        assert {'BTN','SB','BB'}.issubset(labels)

def test_hand_ranking():
    from table_engine import rank_seven
    assert rank_seven(['As','Ks','Qs','Js','Ts','2c','3d']) > rank_seven(['Ah','Ad','Ac','2s','2h','3d','4c'])
    assert rank_seven(['Ah','Ad','Ac','2s','2h','3d','4c']) < rank_seven(['Kh','Kd','Kc','Ks','2d','3d','4c'])

def test_showdown_conserves_chips_and_rake():
    t=Table(4,seed=10)
    before=sum(s.stack+s.total for s in t.seats)
    t._runout()
    assert t.ended
    assert sum(s.stack for s in t.seats)+t.rake_total==before

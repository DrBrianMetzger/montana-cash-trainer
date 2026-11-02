"""Strict importer for the documented MCT JSON interchange format only."""
import json,math
from datetime import datetime,timezone
from solver_models import SCHEMA,DECK,parse_cards,hand_class

def validate(raw):
    if not isinstance(raw,dict) or raw.get('schema')!=SCHEMA:
        raise ValueError('Unsupported schema. Use mct.solver.v1; native .gto2 files are not supported.')
    for field in ('id','solver','source','assumptions','nodes'):
        if field not in raw: raise ValueError('Missing '+field)
    if not isinstance(raw['id'],str) or not raw['id'].strip(): raise ValueError('Invalid solution ID')
    if not isinstance(raw['solver'],dict) or not all(raw['solver'].get(k) for k in ('name','version')): raise ValueError('Solver name/version required')
    if not isinstance(raw['source'],dict) or not raw['source'].get('reference'): raise ValueError('Source reference required')
    if raw['source'].get('verification') not in ('user_verified','unverified','synthetic_test'):
        raise ValueError('Verification must be user_verified, unverified, or synthetic_test')
    a=raw['assumptions']
    if not isinstance(a,dict) or not all(k in a for k in ('game_type','players','positions','effective_stack_bb','blinds','pot_bb','rake','preflop_action','betting_tree')):
        raise ValueError('Incomplete assumptions; no missing values will be invented')
    if not isinstance(a['players'],int) or a['players']<2 or a['players']>10: raise ValueError('Invalid player count')
    if not isinstance(raw['nodes'],list) or not raw['nodes']: raise ValueError('At least one node required')
    ids=set()
    for n in raw['nodes']:
        for k in ('id','parent_id','street','board','acting_position','actions','combos','pot_bb','effective_stack_bb','history'):
            if k not in n: raise ValueError('Node missing '+k)
        if not isinstance(n['id'],str) or n['id'] in ids: raise ValueError('Duplicate or invalid node ID')
        ids.add(n['id'])
        board=parse_cards(n['board'])
        if len(board) not in (0,3,4,5): raise ValueError('Board must contain 0, 3, 4, or 5 cards')
        if n['street'] not in ('Preflop','Flop','Turn','River'): raise ValueError('Invalid street')
        if len(board)!={'Preflop':0,'Flop':3,'Turn':4,'River':5}[n['street']]: raise ValueError('Board/street mismatch')
        actions=n['actions']
        if not isinstance(actions,list) or not actions or len(set(actions))!=len(actions) or any(not isinstance(x,str) or not x.strip() for x in actions): raise ValueError('Invalid actions')
        if not isinstance(n['combos'],dict): raise ValueError('Combos must be a dictionary')
        for combo,d in n['combos'].items():
            cards=parse_cards(combo.split())
            if len(cards)!=2 or set(cards)&set(board): raise ValueError('Blocked or invalid combo: '+combo)
            if not isinstance(d,dict) or 'weight' not in d or 'frequencies' not in d: raise ValueError('Combo missing weight/frequencies')
            w=d['weight']
            if not isinstance(w,(int,float)) or not math.isfinite(w) or not 0<=w<=1: raise ValueError('Combo weight must be 0..1')
            f=d['frequencies']
            if not isinstance(f,dict) or set(f)!=set(actions): raise ValueError('Each combo must specify every node action')
            if any(not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 or v>100 for v in f.values()) or abs(sum(f.values())-100)>0.5:
                raise ValueError('Frequencies must total 100 ±0.5 percentage points')
            for optional in ('ev_bb','equity'):
                if optional in d and (not isinstance(d[optional],dict if optional=='ev_bb' else (int,float))): raise ValueError('Invalid '+optional)
            if 'ev_bb' in d and (not set(d['ev_bb']).issubset(actions) or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in d['ev_bb'].values())): raise ValueError('Invalid action EV')
            if 'equity' in d and not 0<=d['equity']<=1: raise ValueError('Equity must be 0..1')
    for n in raw['nodes']:
        if n['parent_id'] is not None and (n['parent_id'] not in ids or n['parent_id']==n['id']): raise ValueError('Invalid parent node')
    clean=json.loads(json.dumps(raw))
    clean.setdefault('imported_utc',datetime.now(timezone.utc).isoformat())
    return clean

def import_json(blob):
    try: return validate(json.loads(blob))
    except (UnicodeDecodeError,json.JSONDecodeError) as e: raise ValueError('Invalid JSON: '+str(e)) from e

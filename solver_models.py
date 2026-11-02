"""Versioned solver interchange model. This is NOT a solver."""
from itertools import combinations
RANKS='AKQJT98765432'
SUITS='shdc'
DECK={r+s for r in RANKS for s in SUITS}
SCHEMA='mct.solver.v1'

def hand_classes():
    return [RANKS[i]*2 if i==j else (RANKS[i]+RANKS[j]+'s' if i<j else RANKS[j]+RANKS[i]+'o') for i in range(13) for j in range(13)]

def parse_cards(value):
    if isinstance(value,str): value=value.split()
    if not isinstance(value,list) or any(not isinstance(c,str) or c not in DECK for c in value) or len(value)!=len(set(value)):
        raise ValueError('Cards must be unique two-character tokens such as As Kd 7c.')
    return value

def hand_class(cards):
    a,b=cards
    if a[0]==b[0]: return a[0]*2
    hi,lo=sorted([a[0],b[0]],key=RANKS.index)
    return hi+lo+('s' if a[1]==b[1] else 'o')

def combos(hand,board=()):
    board=set(parse_cards(list(board)))
    if hand not in hand_classes(): raise ValueError('Invalid hand class')
    return [list(c) for c in combinations(sorted(DECK),2) if not board.intersection(c) and hand_class(c)==hand]

def cap_warning(sol):
    a=sol['assumptions']
    if a.get('pot_cap_gross')!=800 or a.get('game_type')!='Montana capped cash':
        return 'This solver solution does not model Montana’s $800 gross pot cap. Frequencies must not be treated as cap-adjusted.'
    return 'Verify that the solver actually supports the stated cap and rake rules.'

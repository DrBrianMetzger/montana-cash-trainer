"""Exact combinations and blocker-aware enumeration."""
from solver_models import combos

def combo_rows(node,hand):
    out=[]
    for c in combos(hand,node['board']):
        key=' '.join(c)
        rev=' '.join(reversed(c))
        d=node['combos'].get(key,node['combos'].get(rev))
        if d is not None:
            row={'combo':key,'weight':d['weight'],**{a+' (%)':v for a,v in d['frequencies'].items()}}
            if 'equity' in d:row['equity (%)']=100*d['equity']
            for a,v in d.get('ev_bb',{}).items():row[a+' EV (BB)']=v
            out.append(row)
    return out

"""Combination-weighted range summaries and 13x13 Streamlit display."""
from solver_models import hand_classes,hand_class

def summarize(node):
    out={h:{'weight':0.,'actions':{a:0. for a in node['actions']},'count':0} for h in hand_classes()}
    for combo,d in node['combos'].items():
        h=hand_class(combo.split());o=out[h];w=d['weight'];o['weight']+=w;o['count']+=1
        for a,v in d['frequencies'].items():o['actions'][a]+=w*v
    for o in out.values():
        if o['weight']:
            o['actions']={a:v/o['weight'] for a,v in o['actions'].items()}
    return out

def render_matrix(node):
    import streamlit as st
    summary=summarize(node)
    st.caption('Each cell shows the highest-frequency action; percentages are weighted by exact-combo range weights. Gray means no imported data.')
    cols=st.columns(13,gap='small')
    for i,h in enumerate(hand_classes()):
        d=summary[h];a=max(d['actions'],key=d['actions'].get) if d['weight'] else '—'
        p=d['actions'].get(a,0)
        with cols[i%13]:
            st.markdown(f'<div style="background:{"#235d50" if d["weight"] else "#34383c"};color:white;border-radius:4px;padding:5px 1px;text-align:center;font-size:11px;min-height:43px"><b>{h}</b><br>{a[:8]} {p:.0f}%</div>',unsafe_allow_html=True)
    return summary

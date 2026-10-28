"""Streamlit UI for experimental multiway table."""
import json
import streamlit as st
from table_engine import Table,fmt
from training_db import now,uid

def render_table(db):
    st.subheader('Playable Table · v1.2 beta')
    st.caption('8-handed default · 4–9 seats · experimental multiway engine. Opponent decisions are simple heuristics, not GTO. High-hand showdown, side pots and rake are modeled; multiway betting/cap procedures remain experimental.')
    c1,c2,c3=st.columns([2,1,1])
    with c1:n=st.slider('Seated players (including you)',4,9,8,key='table_n')
    with c2:shill=st.checkbox('Add House Shill',key='table_shill')
    with c3:st.write('');st.write('');start=st.button('Start / reset table',key='table_start')
    if start or 'multi_table' not in st.session_state:
        st.session_state.multi_table=Table(n=n,shill=shill)
        st.session_state.multi_hand_id=uid()
    t=st.session_state.multi_table
    if (n,shill)!=(t.n,t.shill):st.info('Click **Start / reset table** to apply the changed seating configuration.')
    st.info(f'Hand #{t.hand_no} · {t.n} players · {t.street} · gross pot {fmt(t.pot)} / $800')
    if t.shill:
        st.caption(f'House Shill: $200 initial buy-in · {t.house_rebuys} rebuy(s) · house funding {fmt(t.house_buyins)} · current house-player result {fmt(t.seats[-1].stack-t.house_buyins)} · separate rake collected {fmt(t.rake_total)}.')
    columns=st.columns(min(3,t.n))
    for i,s in enumerate(t.seats):
        with columns[i%len(columns)]:
            title=f'{s.name} ({t.position(i)})'
            if i==0:title+=' — YOU'
            if s.house:title+=' 🏠'
            st.write(f'**{title}** · {fmt(s.stack)}'+(' · folded' if s.folded else ''))
    st.markdown('**Your hole cards:** '+ ' '.join(t.seats[0].cards))
    st.markdown('**Board:** '+' '.join(t.board or ['(preflop)']))
    if t.ended:
        st.success(t.outcome)
        if st.button('Deal next hand',key='table_next'):
            t.start();st.session_state.multi_hand_id=uid();st.rerun()
    elif t.to_act==0:
        due=t.to_call(0)
        st.write(f'**Your turn** · to call {fmt(due)} · effective stack {fmt(t.seats[0].stack)}')
        opts=t.legal(0)
        choice=st.radio('Your action',opts,horizontal=True,key=f'table_action_{t.hand_no}_{t.street}_{len(t.history)}')
        amount=None
        if choice in ('Bet','Raise'):
            minimum=(t.highest+t.min_raise)/100
            amount=st.number_input('Announced total street bet ($)',min_value=round(minimum,2),value=round(minimum,2),step=1.0,key=f'table_amt_{t.hand_no}_{len(t.history)}')
            st.caption('Announced amounts may be reduced to respect the $800 gross cap. Multiway cap accounting remains conservative.')
        if st.button('Take action',type='primary',key='table_act'):
            try:
                context={'pot_cents':t.pot,'position':t.position(0),'board':list(t.board),'hole_cards':list(t.seats[0].cards),'to_call_cents':due,'announced_total_dollars':amount,'opponents':t.n-1,'shill':t.shill}
                street=t.street;t.act(0,choice,amount)
                db.decision(st.session_state.practice_session,'montana_practice',street,choice,context,hand_id=st.session_state.multi_hand_id)
                st.rerun()
            except ValueError as e:st.error(str(e))
    else:st.warning('Table awaiting opponent action; reset if necessary.')
    with st.expander('Action history',expanded=True):st.code('\n'.join(t.history[-45:]),language=None)
    st.caption('Experimental simulation: 10% rake up to $6 is deducted on settlement; $800 is a gross limit including rake. Multiway wagering and partial all-ins are simplified; verify live-house procedures before using for real-money decisions.')

"""Montana Cash Trainer: self-contained visual decision table.

Compatible with app.py's render_table(db) import. This is a visual
scenario trainer, NOT a replacement for the original multiway engine.
No solver EV, full betting engine, or showdown is claimed.
"""
from __future__ import annotations
import html
import random
import streamlit as st

RANKS = '23456789TJQKA'
SUITS = 'shdc'
CAP = 800.0

SEATS = [
    ('MoleculeMike','UTG',7,17), ('HelenaHomie','UTG+1',29,5),
    ('Montana Regular A','LJ',51,4), ('Montana Regular B','HJ',73,7),
    ('Montana Regular C','CO',91,25), ('You','BTN',78,80),
    ('SantiNobu','SB',29,79), ('PedaltotheMetalLisa','BB',7,57),
]
SCENARIOS = [
    {'title':'Isolation raise versus limpers','hero':'Ah Qh','board':'', 'pot':9,
     'to_call':2,'action':'Preflop','description':'Three players limp for $2. You are on the button with A♥ Q♥. What is your plan?',
     'feedback':'Consider an isolation raise for value against wide limping ranges. Sizing should reflect callers and your position; the best size depends on their tendencies.'},
    {'title':'Facing a short-stack open','hero':'Ts 9s','board':'','pot':18,
     'to_call':15,'action':'Preflop','description':'An $80 stack opens to $15 from UTG. You hold T♠ 9♠ in the cutoff.',
     'feedback':'The low stack-to-pot ratio reduces implied odds for suited connectors. Folding can be reasonable against a tight early-position range.'},
    {'title':'Top pair versus aggression','hero':'As Kh','board':'Ks 7h 2d','pot':72,
     'to_call':24,'action':'Flop','description':'Lisa bets $24 into $48 on K♠ 7♥ 2♦. You hold A♠ K♥.',
     'feedback':'Calling can retain weaker hands and bluffs. Raising may build value, but evaluate the opponent’s continuing range and who else remains in the pot.'},
    {'title':'Multiway overpair','hero':'Qs Qh','board':'5s 6d 7c','pot':68,
     'to_call':0,'action':'Flop','description':'You 3-bet QQ from the small blind; two players called. The flop is 5♠ 6♦ 7♣.',
     'feedback':'A connected multiway board favors more cautious continuation betting than a dry heads-up flop. Consider range interaction and likely calling hands.'},
]

def _card(token):
    if not token:
        return ''
    rank, suit = token[:-1], token[-1].lower()
    symbol = {'s':'♠','h':'♥','d':'♦','c':'♣'}.get(suit,'?')
    color = '#b91c1c' if suit in 'hd' else '#111827'
    return f'<span class="mt-card" style="color:{color}">{html.escape(rank)}{symbol}</span>'


def _new_scenario():
    st.session_state.mt_visual_index = random.randrange(len(SCENARIOS))
    st.session_state.mt_visual_answer = None
    st.session_state.mt_visual_number = st.session_state.get('mt_visual_number',0)+1


def render_table(db=None):
    """Render a graphical eight-seat scenario and real Streamlit controls."""
    if 'mt_visual_index' not in st.session_state:
        st.session_state.mt_visual_index = 0
        st.session_state.mt_visual_answer = None
        st.session_state.mt_visual_number = 1
    s = SCENARIOS[st.session_state.mt_visual_index]
    top1,top2 = st.columns([3,1])
    top1.subheader('Visual Practice Table')
    if top2.button('Next scenario', key='mt_visual_next', use_container_width=True):
        _new_scenario(); st.rerun()
    st.caption('Visual decision drills · 8 seats · $1/$2 · $800 gross pot cap · not a full-hand betting simulator')
    st.markdown('''<style>
    .mt-felt{position:relative;width:100%;max-width:900px;height:440px;margin:16px auto 22px;
      border:13px solid #252b32;border-radius:48% / 44%;background:radial-gradient(ellipse,#247d55 0%,#155b40 68%,#0c4433 100%);
      box-shadow:inset 0 0 0 4px #a0b8a3,0 9px 25px #0003;color:white;box-sizing:border-box}
    .mt-seat{position:absolute;transform:translate(-50%,-50%);width:115px;text-align:center;
      padding:5px 3px;border-radius:9px;background:#152a2cee;border:1px solid #8da69e;color:#fff;font-size:11px;line-height:1.35}
    .mt-seat.hero{border:2px solid #f8cc6a;background:#182c32}
    .mt-seat b{display:block;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .mt-center{position:absolute;top:45%;left:50%;transform:translate(-50%,-50%);text-align:center;width:72%}
    .mt-cards{display:flex;gap:5px;justify-content:center;margin:10px 0}
    .mt-card{display:inline-flex;justify-content:center;align-items:center;width:34px;height:47px;border-radius:5px;
      background:#fff;border:1px solid #b9b9b9;font-size:19px;font-weight:800;box-shadow:1px 2px 3px #0004}
    .mt-meta{font-size:13px;color:#f1f7f3}.mt-hero-cards{margin-top:5px}.mt-hero-cards .mt-card{width:26px;height:35px;font-size:15px}
    @media(max-width:650px){.mt-felt{height:340px;border-width:8px}.mt-seat{width:80px;font-size:9px}.mt-seat b{font-size:9px}.mt-card{width:27px;height:39px;font-size:16px}}
    </style>''', unsafe_allow_html=True)
    seats=[]
    for name,pos,x,y in SEATS:
        hero = name == 'You'
        extra = '<div class="mt-hero-cards">'+_card(s['hero'].split()[0])+_card(s['hero'].split()[1])+'</div>' if hero else ''
        seats.append(f'<div class="mt-seat {"hero" if hero else ""}" style="left:{x}%;top:{y}%"><b>{html.escape(name)}</b>{html.escape(pos)} · $400{extra}</div>')
    board=''.join(_card(t) for t in s['board'].split())
    center=f'<div class="mt-center"><div class="mt-meta">{html.escape(s["action"])} · POT ${s["pot"]:.0f}</div><div class="mt-cards">{board}</div><div class="mt-meta">${CAP-s["pot"]:.0f} remaining to cap</div></div>'
    st.markdown('<div class="mt-felt">'+''.join(seats)+center+'</div>',unsafe_allow_html=True)
    st.progress(min(1.0,s['pot']/CAP),text=f'Gross pot ${s["pot"]:.2f} / $800 (rake counts toward cap)')
    st.markdown(f'**{s["title"]}** · Scenario #{st.session_state.mt_visual_number}')
    st.write(s['description'])
    st.caption(f'Amount facing you: ${s["to_call"]:.2f}. These are fixed training scenarios, not live calculated legal actions.')
    options = ['Fold','Call','Raise'] if s['to_call'] else ['Check','Bet']
    if st.session_state.mt_visual_answer is None:
        cols=st.columns(len(options))
        for col,action in zip(cols,options):
            if col.button(action,key=f'mt_visual_{action}',use_container_width=True):
                st.session_state.mt_visual_answer=action
                st.rerun()
    else:
        st.success(f'Your choice: {st.session_state.mt_visual_answer}')
        st.info(s['feedback'])
        st.caption('This feedback is qualitative; no solver-backed grading or EV is implied.')
        if st.button('Try another hand',key='mt_visual_again'):
            _new_scenario();st.rerun()

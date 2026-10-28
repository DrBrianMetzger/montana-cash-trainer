"""Montana Cash Game Trainer v1.0 — scripted demonstration, not a solver."""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

DB = Path(__file__).with_name('trainer.sqlite3')
PERSONAS = {
    'SantiNobu': 'GTO-oriented adaptive opponent (expert)',
    'PedaltotheMetalLisa': 'Hyperaggressive barreler (advanced)',
    'MoleculeMike': 'Tight, low-bluff conservative opponent (intermediate)',
    'HelenaHomie': 'Positionally aware tight-aggressive regular (advanced)',
}
STREETS = [
    {'street':'Preflop', 'board':[], 'pot':11, 'hero_stack':400, 'to_call':6,
     'prompt':'UTG+1 opens to $6; cutoff calls. Hero is SB with Q♠ Q♥. Choose your action.',
     'options':['Fold','Call $5','Raise to $22','Raise to $35'],
     'feedback':{'Fold':'Too tight versus a small open and a call.', 'Call $5':'Calling keeps a strong value hand in a multiway pot out of position.', 'Raise to $22':'Value 3-bet, but sizing may invite two calls while out of position.', 'Raise to $35':'A larger isolation/value 3-bet can charge loose callers; the best size depends on their ranges.'}},
    {'street':'Flop', 'board':['5♣','6♦','7♠'], 'pot':66, 'hero_stack':378, 'to_call':0,
     'prompt':'Scripted line: Hero raised to $22 and both called. Flop 5♣ 6♦ 7♠. Hero acts first.',
     'options':['Check','Bet $20','Bet $40'],
     'feedback':{'Check':'Checking protects your checking range and controls a vulnerable multiway pot.', 'Bet $20':'Small c-bet may extract value but two opponents have substantial connectivity with this board.', 'Bet $40':'A larger bet builds a pot on a board that often favors callers; evaluate ranges carefully.'}},
    {'street':'Turn', 'board':['5♣','6♦','7♠','4♥'], 'pot':126, 'hero_stack':358, 'to_call':0,
     'prompt':'Scripted line: Hero bet $20 and both called. Turn 4♥. Hero acts first.',
     'options':['Check','Bet $30','Bet $60'],
     'feedback':{'Check':'Checking is prudent: any eight makes a straight, and multiway ranges are strong.', 'Bet $30':'Thin value/protection is difficult when many eight-x holdings beat QQ.', 'Bet $60':'A large bet risks value-owning yourself against strong continuing ranges.'}},
    {'street':'Turn response', 'board':['5♣','6♦','7♠','4♥'], 'pot':126, 'hero_stack':358, 'to_call':None,
     'prompt':'After Hero checks, UTG+1 bets and cutoff raises. Amounts were not recorded. Choose a response.',
     'options':['Fold','Call (unpriced)','Raise (unpriced)'],
     'feedback':{'Fold':'Reasonable fold against bet-plus-raise multiway strength on a four-straight board.', 'Call (unpriced)':'No exact pot odds can be calculated because bet and raise amounts are unknown.', 'Raise (unpriced)':'A raise faces exceptionally strong ranges; exact EV is not available.'}},
]

def init_db():
    with sqlite3.connect(DB) as db:
        db.execute('CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, session_id TEXT, recorded_utc TEXT, persona TEXT, street TEXT, action TEXT, scripted_pot INTEGER, feedback TEXT)')

def record(session_id, persona, stage, action, feedback):
    with sqlite3.connect(DB) as db:
        db.execute('INSERT INTO decisions (session_id,recorded_utc,persona,street,action,scripted_pot,feedback) VALUES (?,?,?,?,?,?,?)',
                   (session_id, datetime.now(timezone.utc).isoformat(), persona, stage['street'], action, stage['pot'], feedback))

def reset():
    st.session_state.step = 0
    st.session_state.answers = []
    st.session_state.session_id = datetime.now(timezone.utc).isoformat()

st.set_page_config(page_title='Montana Cash Game Trainer', page_icon='♠', layout='wide')
init_db()
if 'step' not in st.session_state:
    reset()
st.title('♠ Montana Cash Game Trainer')
st.warning('VERSION 1.0 · SCRIPTED DEMONSTRATION — not a live betting engine, GTO solver, or Montana rules certification. Actions do not change the scripted future streets.')
with st.sidebar:
    st.header('Opponent Lab · Preview')
    persona = st.selectbox('Study persona', list(PERSONAS))
    st.caption(PERSONAS[persona])
    st.info('Personas are selectable study labels in v1.0; they do not yet make autonomous decisions.')
    if st.button('Restart exercise'):
        reset()
        st.rerun()
    st.write('**Scenario:** $1/$2 · Hero SB · illustrative $400 starting stack')
    st.write('**Rake:** excluded from illustrative pot totals')
    st.write('**Pot cap:** $800, not yet enforced')

step = st.session_state.step
if step < len(STREETS):
    stage = STREETS[step]
    st.subheader(f'Decision {step+1}/{len(STREETS)} · {stage["street"]}')
    st.markdown('''<div style="background:#12513b;border:9px solid #543b27;border-radius:100px;padding:30px;text-align:center;color:white;font-size:20px;line-height:2.2">
    <div>UTG+1 &nbsp; ● &nbsp; $400 &nbsp;&nbsp;&nbsp;&nbsp; CO &nbsp; ● &nbsp; $400</div>
    <div style="font-size:30px">{board}</div>
    <div>Illustrative pot: ${pot}</div>
    <div style="font-size:30px">Q♠ &nbsp; Q♥</div>
    <div>HERO · SB &nbsp; | &nbsp; Scripted stack: ${stack}</div></div>'''.format(board=' '.join(stage['board']) or 'Preflop', pot=stage['pot'], stack=stage['hero_stack']), unsafe_allow_html=True)
    st.write(stage['prompt'])
    if stage['to_call'] is None:
        st.caption('Original turn wager amounts are unknown. No exact legal sizing or pot odds are implied.')
    action = st.radio('Choose an action', stage['options'], key=f'action_{step}')
    if st.button('Submit decision', type='primary'):
        feedback = stage['feedback'][action]
        record(st.session_state.session_id, persona, stage, action, feedback)
        st.session_state.answers.append({'street':stage['street'], 'action':action, 'feedback':feedback})
        st.session_state.step += 1
        st.rerun()
else:
    st.success('Exercise completed. Recorded decisions:')
    for a in st.session_state.answers:
        st.markdown(f'**{a["street"]} — {a["action"]}**  \n{a["feedback"]}')
    st.info('Actual showdown: UTG+1 held 7-8; cutoff held 8-8. Both had an eight-high straight on 5-6-7-4. Results do not determine whether earlier decisions were correct.')
    if st.button('Practice again'):
        reset()
        st.rerun()
st.divider()
st.caption('All feedback is heuristic coaching, not calculated EV. The scenario always follows the documented hand, regardless of your chosen actions.')
from gto_library import render_gto_library

st.divider()
render_gto_library()

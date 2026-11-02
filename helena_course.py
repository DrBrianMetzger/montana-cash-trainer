"""Helena Cash Game course: randomized decision drills, not a solver or game engine.
No additional dependencies beyond Streamlit.  Pot is a gross displayed scenario amount.
"""
from __future__ import annotations
import html
import json
import random
import uuid
from dataclasses import dataclass
import streamlit as st

TITLE = 'Helena Cash Game — Patience, Precision, and Exploitation'
# Two independent situations per lesson. Variables vary the opponent, sizing, stack,
# and seat; all are hypothetical except the clearly labeled A4s inspiration.
LESSONS = {
 'Playing Through a Cold Deck': [
  ('Preflop','Q♠ 8♦','', 'UTG','You have folded 11 hands in a row. First to act with Q8o. What now?',('Fold','Open $8','Limp $2'),'Fold','Boredom does not improve an early-position opening range.'),
  ('Flop','A♠ Q♠','K♦ 7♣ 2♥','CO','You opened $8; the big blind called and checked. You missed this dry flop.',('Check','Bet $6','Bet $20'),'Check','A check preserves showdown potential and avoids automatic c-betting. A small bet may also work against an overfolder; no universal solver answer.')],
 'Tight Linear 3-Betting Ranges': [
  ('Preflop','A♠ 4♠','', 'CO','You opened $8; HelenaHomie 3-bets to $25 from the button. You have no read beyond a tight, linear range.',('Fold','Call $17','4-bet $75'),'Fold','Against an assumed TT+/AQ+ heavy range, folding is a sensible baseline. Change the range assumption to reconsider.'),
  ('Preflop','K♣ Q♦','', 'HJ','You opened $8; MoleculeMike 3-bets to $30 on the button. The blinds fold.',('Fold','Call $22','4-bet $85'),'Fold','KQo can be dominated against a narrow linear 3-betting range; avoid paying for speculative reverse implied odds.')],
 'Missing the Flop': [
  ('Flop','A♠ Q♠','K♦ 7♣ 2♥','BTN','You opened preflop; the big blind called and checked. No pair or immediate draw.',('Check','Bet $6','Bet $22'),'Check','Check is a defensible default versus sticky callers; small bets can work against overfolders. Evaluate range advantage and backdoors.'),
  ('Flop','K♠ Q♠','5♦ 4♣ 2♥','CO','You raised; the big blind called and checked on a low connected board.',('Check','Bet $7','Bet $24'),'Check','This texture connects with blind defenses. Avoid a compulsory c-bet without fold equity or useful backdoors.')],
 'Discipline Against Underbluffing': [
  ('River','A♠ J♦','A♦ 9♣ 4♠ 7♥ 2♣','BTN','MoleculeMike check-called twice, then check-raised your $30 river value bet to $130.',('Fold','Call $100','Raise $250'),'Fold','If this particular river raise is value-heavy, a disciplined exploitative fold can be correct. Validate the assumption.'),
  ('Turn','K♣ Q♣','K♦ 8♠ 3♥ 6♦','CO','You c-bet the flop and conservative HelenaHomie check-raises a large turn bet.',('Fold','Call','Re-raise'),'Fold','Large turn raises from an underbluffing profile often warrant a tight response. This is conditional, not a population fact.')],
 'The Cost of Raise-Fold Poker': [
  ('Preflop','9♠ T♠','', 'HJ','You have lost $70 in small pots. MoleculeMike ($80 stack) opens to $15 UTG.',('Fold','Call $15','3-bet $45'),'Fold','A short stack limits implied odds. A loss streak is not a reason to defend marginal suited connectors.'),
  ('Flop','A♦ Q♣','K♠ 5♦ 5♣','BTN','You opened $7, big blind called, then checked. You missed; the pot is small and rake matters.',('Check','Bet $10','Bet $24'),'Check','Avoid spending $10 to fight for a small pot without a credible fold-equity hypothesis.')],
 'When to Fight for Small Pots': [
  ('Preflop','A♥ J♥','', 'BTN','Two players limp $2; both frequently fold to isolation raises. Action on you.',('Fold','Overlimp $2','Raise $14'),'Raise $14','Position, hand strength, and observed overfolding support a value-oriented isolation raise.'),
  ('Turn','Q♠ J♠','A♦ 7♣ 2♥ 4♠','BTN','You checked behind the flop; the big blind checks the turn again and has shown frequent turn folds.',('Check','Bet $12','Bet $45'),'Bet $12','A delayed probe can exploit an opponent who overfolds, with some equity if called. Size to the actual pot.')],
 'Capitalizing on Strong Hands': [
  ('Preflop','Q♠ Q♥','', 'SB','UTG+1 raises to $6; CO calls. You have $1 posted and $400 effective.',('Fold','Call $5','3-bet $32'),'3-bet $32','Value 3-bet out of position to deny cheap multiway entry; $32 is an illustrative sizing, not a solved optimum.'),
  ('Flop','A♠ K♠','A♦ K♦ 6♣','BTN','You raised and the big blind called. They check on a board where you have top two pair.',('Check','Bet $15','Bet $65'),'Bet $15','A value bet can start building a pot against continuing aces and draws. Adjust size to pot and opponent.')],
 'Session Discipline and Mental Game': [
  ('Preflop','J♣ 8♦','', 'UTG','You are down $100 after two hours and have folded the last eight hands.',('Fold','Open $15','Limp $2'),'Fold','Being down does not justify widening a poor UTG hand. Decide whether to keep playing based on game quality and focus.'),
  ('Flop','K♦ Q♣','5♠ 4♦ 2♣','BTN','You missed again and feel tempted to bluff a regular who has called most flop bets.',('Check','Bet $10','Bet $35'),'Check','Without a credible fold-equity estimate, a frustration-driven bluff may compound the cost of a cold stretch.')],
}

PERSONAS = ('HelenaHomie','MoleculeMike','SantiNobu','PedaltotheMetalLisa')
SUITS = {'♠':'#111827','♣':'#111827','♥':'#dc2626','♦':'#dc2626'}

def card_html(card):
    card=card.strip()
    if not card or card == '—': return ''
    suit=card[-1] if card[-1] in SUITS else ''
    rank=card[:-1] if suit else card
    return f'<span class="hc-card" style="color:{SUITS.get(suit,"#111827")}">{html.escape(rank+suit)}</span>'

def scenario(seed:int, lesson:str, variant:int=0):
    """Deterministic generation for replay/tests; avoid exact repeats until deck exhaustion."""
    if lesson not in LESSONS: raise ValueError('Unknown lesson')
    rng=random.Random(seed)
    idx=variant%len(LESSONS[lesson])
    street,hand,board,position,question,actions,baseline,reason=LESSONS[lesson][idx]
    persona=next((name for name in PERSONAS if name in question), rng.choice(PERSONAS))
    stack=rng.choice((120,200,300,400,500))
    # Do not vary specific dollar amounts in the text: doing so would create inconsistent pots.
    # These are scenario labels, not fully reconstructed hand histories.
    return dict(id=f'{seed}:{variant}',lesson=lesson,street=street,hand=hand,board=board,
                position=position,question=question,actions=actions,baseline=baseline,
                reason=reason,persona=persona,stack=stack,
                pot=None, hypothetical=True)

def visual_table(s):
    board=''.join(card_html(c) for c in s['board'].split()) if s['board'] else '<span class="hc-muted">Preflop · no board</span>'
    hero=''.join(card_html(c) for c in s['hand'].split())
    opponent=html.escape(s['persona'])
    position=html.escape(s['position'])
    st.markdown('''<style>
    .hc-felt{background:radial-gradient(ellipse at center,#23835c 0%,#155a43 70%,#0b3b30 100%);border:10px solid #443225;border-radius:45% / 30%;min-height:300px;max-width:760px;margin:8px auto 16px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:20px 10px;box-shadow:inset 0 0 0 3px #c6a976,0 6px 22px #0003;color:white}
    .hc-seat{background:#142a2b;border:1px solid #b7b7a5;border-radius:12px;padding:6px 14px;font-size:13px;text-align:center;color:white;max-width:85%}
    .hc-board{display:flex;align-items:center;justify-content:center;gap:4px;min-height:80px;flex-wrap:wrap}
    .hc-card{display:inline-flex;background:#fdfcf8;border:2px solid #dedede;border-radius:7px;min-width:38px;height:55px;align-items:center;justify-content:center;font-weight:800;font-size:22px;margin:2px;box-shadow:0 3px 3px #0004}
    .hc-muted{color:#d7ede1;font-size:14px}
    .hc-title{font-size:13px;color:#d7ede1;text-align:center}
    </style>''',unsafe_allow_html=True)
    st.markdown(f'''<div class="hc-felt"><div class="hc-seat">{opponent}<div class="hc-title">Opponent · modeled profile</div></div><div><div class="hc-board">{board}</div><div class="hc-title">{html.escape(s['street'])} · $1/$2 · $800 gross pot cap</div></div><div class="hc-seat">YOU · {position}<div>{hero}</div><div class="hc-title">Illustrative training scenario</div></div></div>''',unsafe_allow_html=True)

def _new_hand(lesson):
    k='hc_serial'; st.session_state[k]=st.session_state.get(k,0)+1
    # seed is random, and serial ensures different situation selection when possible
    seed=random.SystemRandom().randrange(1,2**31)
    st.session_state['hc_hand']=scenario(seed,lesson,st.session_state[k])
    st.session_state['hc_answer']=None

def render_helena_course(db):
    st.header(TITLE)
    st.caption('Interactive decision drills · hypothetical variations · no solver-backed EV claims')
    lesson=st.selectbox('Choose a lesson',list(LESSONS),key='hc_lesson')
    a,b=st.columns([1,2]); a.metric('Lessons',len(LESSONS))
    try:
        records=[r for r in db.rows('decisions') if r['source']=='montana_practice' and '"course": "helena_cash"' in (r.get('context') or '')]
    except Exception: records=[]
    b.metric('Course decisions saved',len(records))
    if st.session_state.get('hc_active_lesson')!=lesson or 'hc_hand' not in st.session_state:
        st.session_state['hc_active_lesson']=lesson; _new_hand(lesson)
    s=st.session_state['hc_hand']
    st.subheader(lesson)
    st.info(s['question'])
    st.caption(f'Variation #{st.session_state["hc_serial"]} · {s["persona"]}. Specific opponent frequencies are not verified.')
    visual_table(s)
    st.markdown('**Your decision**')
    if st.session_state.get('hc_answer') is None:
        cols=st.columns(len(s['actions']))
        for col,action in zip(cols,s['actions']):
            if col.button(action,key='hc_act_'+action,use_container_width=True,type='secondary'):
                st.session_state['hc_answer']=action
                if 'hc_session' not in st.session_state: st.session_state['hc_session']=db.start_session('montana_practice',{'course':'helena_cash'})
                db.decision(st.session_state['hc_session'],'montana_practice',s['street'],action,
                    {'course':'helena_cash','lesson':lesson,'scenario_id':s['id'],'persona':s['persona'],'hypothetical':True,'baseline':s['baseline'],'matches_baseline':action==s['baseline']},
                    feedback=s['reason'])
                st.rerun()
    else:
        answer=st.session_state['hc_answer']
        st.write(f'**You chose:** {answer}')
        st.write(f'**Suggested baseline:** {s["baseline"]}')
        st.write(s['reason'])
        st.caption('Baseline means a qualitative coaching default under the stated assumptions, not a solver verdict or proven EV optimum.')
        if answer!=s['baseline']:
            st.write('**Alternative-action review:** Your choice may be reasonable under different ranges, frequencies, or sizing. Identify what evidence would justify it.')
        else:
            st.write('**Alternative-action review:** Other actions can be justified if the opponent or table assumptions differ.')
        st.write('**Next practice:** Try a different opponent and compare whether the decision changes.')
        if st.button('Next random hand',type='primary',key='hc_next'):
            _new_hand(lesson); st.rerun()
    with st.expander('About these exercises and assumptions'):
        st.write('These are scenario-based decision drills, not a full-deck simulation or a replacement for the playable table. They use illustrative opponent profiles and stack labels. Pot odds are intentionally not calculated when required wager and contribution data are missing. They do not infer EV from wins or losses.')
        st.write('The A4s versus a $25 3-bet situation is inspired by a real observation; position, suits, stacks and other details in these exercises are hypothetical.')
        st.write('Saved decisions use the existing Montana practice source and carry a course tag so they can be filtered separately in the Leak Finder.')

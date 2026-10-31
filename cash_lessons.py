"""Montana cash-game lesson room. Qualitative coaching, NOT a GTO/EV solver.

Designed as an additive module for the existing Streamlit application.
"""
from __future__ import annotations
import json
import random
import uuid

LESSONS = {
    'Preflop Discipline': [
        dict(id='pf1', street='Preflop', position='UTG', hand='A♠ 9♦', board='—', pot=3, stack=400,
             action='Eight-handed $1/$2. You are first to act. Blinds are $1/$2; no straddle.',
             options=['Fold','Open to $6','Limp $2'], preferred=['Fold'],
             feedback={'Fold':'A9o is usually outside a disciplined eight-handed UTG opening range. You avoid difficult dominated-ace spots.',
                       'Open to $6':'A9o is a loose UTG open at a full table; later-position callers often dominate your ace.',
                       'Limp $2':'Open-limping creates a weak, uncapped multiway range and makes postflop play difficult.'},
             takeaway='Start with position-aware ranges; do not confuse a playable hand with a profitable early-position open.', leak='preflop_range'),
        dict(id='pf2', street='Preflop', position='BTN', hand='A♥ J♥', board='—', pot=7, stack=400,
             action='Eight-handed $1/$2. UTG+1 limps $2, HJ limps $2, CO folds. Action on you. Blinds are live.',
             options=['Fold','Overlimp $2','Isolate to $14'], preferred=['Isolate to $14'],
             feedback={'Fold':'AJs is strong on the button against two limpers. Folding generally forfeits profitable opportunities.',
                       'Overlimp $2':'Position and suitedness make a limp viable in some unusually sticky lineups, but you forgo isolation value.',
                       'Isolate to $14':'A value-oriented isolation raise can narrow the field and build a pot in position. Adjust sizing to callers.'},
             takeaway='Value-isolate limpers in position; adjust to table calling behavior.', leak='isolation'),
        dict(id='pf3', street='Preflop', position='BB', hand='K♣ 8♦', board='—', pot=8, stack=400,
             action='Eight-handed $1/$2. UTG folds, HJ limps $2, CO folds, BTN limps $2, SB completes $1. You have posted $2.',
             options=['Check','Raise to $16','Fold'], preferred=['Check'],
             feedback={'Check':'Checking preserves a free option with a marginal offsuit hand in a multiway pot.',
                       'Raise to $16':'An isolation raise is high variance with K8o against three limpers who may call.',
                       'Fold':'With no additional amount to call, folding forfeits your free flop.'},
             takeaway='In the big blind, distinguish a free check from a paid call.', leak='blind_defense'),
        dict(id='pf4', street='Preflop', position='CO', hand='Q♠ T♠', board='—', pot=3, stack=400,
             action='Eight-handed $1/$2. Action folds to you in the cutoff.',
             options=['Fold','Open to $6','Limp $2'], preferred=['Open to $6'],
             feedback={'Fold':'QTs is typically strong enough to open from the cutoff, although extreme opponents can affect this.',
                       'Open to $6':'A reasonable positional open that can win blinds or play a suited, connected hand in position.',
                       'Limp $2':'Open-limping gives up fold equity and leaves the blinds an inexpensive entry.'},
             takeaway='Expand opening ranges as position improves.', leak='preflop_range'),
    ],
    '3-Bet and 4-Bet Pots': [
        dict(id='3b1', street='Preflop', position='SB', hand='Q♠ Q♥', board='—', pot=15, stack=400,
             action='Eight-handed $1/$2. UTG+1 opens to $6, CO calls $6. You have $1 posted in the small blind. Action on you.',
             options=['Fold','Call $5','3-bet to $22','3-bet to $32'], preferred=['3-bet to $32'],
             feedback={'Fold':'QQ is far too strong to fold to a small open and one call.',
                       'Call $5':'Flatting keeps ranges wide but often creates a difficult out-of-position multiway pot.',
                       '3-bet to $22':'This is the historical sizing. It offers attractive odds to both opponents and can invite multiway play.',
                       '3-bet to $32':'A larger out-of-position value 3-bet can charge the opener and caller more. It is a study baseline, not a proven EV-optimal amount.'},
             takeaway='Against an open plus caller, consider a larger out-of-position value 3-bet.', leak='three_bet_sizing'),
        dict(id='3b2', street='Preflop', position='BTN', hand='A♠ K♠', board='—', pot=31, stack=400,
             action='Eight-handed $1/$2. HJ opens to $7, CO 3-bets to $21, you are on the button. Blinds have not acted.',
             options=['Fold','Cold-call $21','4-bet to $55'], preferred=['4-bet to $55'],
             feedback={'Fold':'AKs generally has enough equity and blockers to continue against reasonable ranges.',
                       'Cold-call $21':'Cold-calling may be appropriate versus some tight 3-bet ranges; it can invite multiway play.',
                       '4-bet to $55':'A reasonable value/semi-bluff 4-bet baseline versus non-nit ranges. Against extreme nits, adjust.'},
             takeaway='A strong blocker hand can 4-bet for value and fold equity; opponent range matters.', leak='four_bet'),
        dict(id='3b3', street='Preflop', position='HJ', hand='J♦ J♣', board='—', pot=41, stack=400,
             action='Eight-handed $1/$2. You opened to $8; a conservative BTN 3-bets to $30. Blinds fold. Action returns to you; $22 more to call.',
             options=['Fold','Call $22','4-bet to $85'], preferred=['Call $22'],
             feedback={'Fold':'Folding JJ may be too tight without evidence of an exceptionally strong 3-bet range.',
                       'Call $22':'Calling retains weaker hands and avoids inflating the pot against a conservative 3-betting range.',
                       '4-bet to $85':'A 4-bet can isolate a very strong continuing range and is not automatically best against a nit.'},
             takeaway='Choose 4-bet ranges based on the opponent, not hand strength alone.', leak='three_bet_defense'),
    ],
    'Multiway Postflop Play': [
        dict(id='mw1', street='Flop', position='SB', hand='Q♠ Q♥', board='5♣ 6♦ 7♠', pot=66, stack=378,
             action='Three-way 3-bet pot. You are the preflop 3-bettor, first to act; both opponents called your $22 preflop. Pot $66, before rake.',
             options=['Check','Bet $20','Bet $45'], preferred=['Check','Bet $20'],
             feedback={'Check':'A check protects your checking range on a connected board that can hit both callers; you can evaluate their actions.',
                       'Bet $20':'A small bet may extract value and deny some equity, but both opponents have many connected holdings. Plan for calls and raises.',
                       'Bet $45':'A large bet risks bloating a multiway pot on a board that interacts strongly with callers’ ranges.'},
             takeaway='An overpair is not invulnerable on a low, connected, multiway flop.', leak='multiway_overpair'),
        dict(id='mw2', street='Flop', position='CO', hand='A♣ K♣', board='K♦ 8♠ 7♠', pot=42, stack=380,
             action='Four players saw the flop in a single-raised pot. Checks to you in the cutoff; button remains to act.',
             options=['Check','Bet $15','Bet $40'], preferred=['Check','Bet $15'],
             feedback={'Check':'Pot control is defensible with top pair against several ranges on a coordinated flop.',
                       'Bet $15':'Small value/protection betting can be reasonable, but draws and two-pair combinations are present.',
                       'Bet $40':'Near-pot betting into three opponents may isolate stronger hands and build an unwieldy pot.'},
             takeaway='Multiway ranges are stronger; reduce automatic c-betting and plan future streets.', leak='multiway_cbet'),
        dict(id='mw3', street='Flop', position='BB', hand='5♥ 5♠', board='K♠ K♣ 5♦', pot=46.50, stack=392.25,
             action='Three-way 3-bet pot. You checked, preflop 3-bettor checked, third player bet 7.5 BB ($15). Action on you. This is a concept exercise inspired by a Pluribus hand, not a Montana replay.',
             options=['Fold','Call $15','Check-raise to $55'], preferred=['Call $15','Check-raise to $55'],
             feedback={'Fold':'You have a full house. Folding is not reasonable against an ordinary bet.',
                       'Call $15':'Slow-playing can preserve bluffs and weaker holdings and keep the preflop 3-bettor involved.',
                       'Check-raise to $55':'Raising builds value against Kx and other continuing hands. A historical Pluribus action is not proof this is always best.'},
             takeaway='Evaluate trapping versus immediate value; a strong hand can use both lines.', leak='value_vs_trap'),
    ],
}


def scenario(scenario_id):
    for group, entries in LESSONS.items():
        for item in entries:
            if item['id'] == scenario_id:
                return group, item
    raise KeyError(scenario_id)


def evaluate(item, choice):
    if choice not in item['options']:
        raise ValueError('Unknown action')
    return {'preferred': choice in item['preferred'], 'explanation': item['feedback'][choice],
            'takeaway': item['takeaway'], 'leak': item['leak'] if choice not in item['preferred'] else None}


def render_cash_lessons(db=None):
    import streamlit as st
    st.header('Cash Game Lessons · v1.3')
    st.caption('Montana $1/$2 study spots · 8-handed · $800 gross-pot cap including rake. Coaching heuristics, not verified GTO or calculated EV.')
    group = st.selectbox('Choose lesson', list(LESSONS), key='lesson_group_v13')
    mode = st.radio('Training mode', ['Guided lesson', 'Random challenge'], horizontal=True, key='lesson_mode_v13')
    state = st.session_state
    signature = (group, mode)
    if state.get('lesson_signature_v13') != signature:
        state.lesson_signature_v13 = signature
        state.lesson_idx_v13 = 0
        state.lesson_answer_v13 = None
    items = LESSONS[group]
    if mode == 'Guided lesson':
        idx = min(state.lesson_idx_v13, len(items)-1)
    else:
        if 'lesson_random_v13' not in state or state.get('lesson_random_group_v13') != group:
            state.lesson_random_v13 = random.randrange(len(items))
            state.lesson_random_group_v13 = group
        idx = state.lesson_random_v13
    item = items[idx]
    st.progress((idx+1)/len(items) if mode=='Guided lesson' else 0)
    st.subheader(f'{group} · Scenario {idx+1 if mode=="Guided lesson" else "random"}')
    a,b,c = st.columns(3)
    a.metric('Position', item['position'])
    b.metric('Gross pot (scenario)', f'${item["pot"]:,.2f}')
    c.metric('Stack (scenario)', f'${item["stack"]:,.2f}')
    st.markdown(f'**Your hand:** {item["hand"]}  ·  **Board:** {item["board"]}  ·  **Street:** {item["street"]}')
    st.write(item['action'])
    st.caption('Scenario amounts are illustrative and are not dynamically recomputed. Full-hand play remains in the Practice Table.')
    selection = st.radio('Your decision', item['options'], key=f'lesson_choice_{item["id"]}', disabled=state.lesson_answer_v13 is not None)
    if state.lesson_answer_v13 is None:
        if st.button('Lock decision and get feedback', type='primary', key='lesson_reveal_v13'):
            result = evaluate(item, selection)
            state.lesson_answer_v13 = {'choice': selection, **result}
            if db is not None:
                if 'lesson_session_v13' not in state:
                    state.lesson_session_v13 = db.start_session('montana_practice', {'trainer':'cash_lessons_v1.3'})
                db.decision(state.lesson_session_v13, 'montana_practice', item['street'], selection,
                            context={'trainer':'cash_lessons_v1.3','scenario_id':item['id'],'lesson':group,'position':item['position'],'options':item['options']},
                            feedback=json.dumps(result))
            st.rerun()
    else:
        answer = state.lesson_answer_v13
        if answer['preferred']:
            st.success('Reasonable baseline action for this study scenario.')
        else:
            st.warning('Worth reviewing against the suggested baseline.')
        st.write(f'**Your action:** {answer["choice"]}')
        st.write(answer['explanation'])
        st.info(f'**Key lesson:** {answer["takeaway"]}')
        st.caption('Other actions can be profitable against different ranges. No solver-backed EV or guaranteed optimal action is claimed.')
        if st.button('Next scenario' if mode=='Guided lesson' else 'New random scenario', key='lesson_next_v13'):
            state.lesson_answer_v13 = None
            if mode=='Guided lesson':
                state.lesson_idx_v13 = (idx+1) % len(items)
            else:
                state.lesson_random_v13 = random.choice([n for n in range(len(items)) if n != idx]) if len(items)>1 else idx
            st.rerun()
    if db is not None:
        rows = []
        for r in db.rows('decisions'):
            try: ctx = json.loads(r['context'] or '{}')
            except (ValueError, TypeError): continue
            if r['source']=='montana_practice' and ctx.get('trainer')=='cash_lessons_v1.3':
                rows.append(r)
        st.divider()
        st.subheader('Lesson progress')
        st.metric('Recorded lesson decisions', len(rows))
        st.caption('These are coaching-baseline decisions, not GTO accuracy or Pluribus prediction accuracy. Download the complete backup from the sidebar.')

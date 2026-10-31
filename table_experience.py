"""Presentation shell for the existing eight-handed table; does not alter its game logic."""
import streamlit as st

CAP_CENTS = 80000

def remaining_cap(gross_pot):
    """Gross pot includes rake already removed from the felt."""
    cents = round(float(gross_pot) * 100)
    if cents < 0:
        raise ValueError('Pot cannot be negative')
    return max(0, CAP_CENTS - cents) / 100


def equal_contribution_headroom(gross_pot, participants):
    """Illustrative equal matched contributions; not a multiway betting adjudicator."""
    if participants < 2:
        raise ValueError('At least two participants required')
    return remaining_cap(gross_pot) / participants


def render_cap_explainer():
    with st.expander('Montana $800 pot-cap calculator', expanded=False):
        st.caption('Gross pot includes rake already set aside. The equal-share estimate assumes no unequal outstanding bets, dead money, or side pots.')
        pot = st.number_input('Current gross pot ($)', min_value=0.0, max_value=800.0, value=750.0, step=1.0, key='v14_cap_pot')
        players = st.number_input('Players matching new contributions', min_value=2, max_value=8, value=2, step=1, key='v14_cap_players')
        st.metric('Room to cap', f'${remaining_cap(pot):,.2f}')
        st.write(f'Equal additional contribution per player: **${equal_contribution_headroom(pot, players):,.2f}**')
        st.caption('A player may announce a larger wager. The dealer can state the effective amount to call. Do not use this estimate to adjudicate unequal bets or side pots.')


def render_practice_shell(db, render_existing_table):
    st.header('♠ Montana Practice Table')
    st.caption('Eight-handed $1/$2 practice · $800 gross-pot cap including rake · opponent decisions are heuristics, not GTO.')
    a,b,c = st.columns(3)
    a.metric('Small / big blind', '$1 / $2')
    b.metric('Pot cap', '$800')
    c.metric('Rake', '10%, max $6')
    mode = st.radio('Training mode', ['Free Play', 'Coach after decisions', 'Challenge (review later)'], horizontal=True, key='v14_mode')
    st.info('Use the existing table below to play. The coach is a study journal, not an automatic EV solver. It does not change opponent actions or reveal hidden cards.')
    render_existing_table(db)
    with st.expander('Decision review notebook', expanded=mode == 'Coach after decisions'):
        st.write('Record a decision you just made and what you were thinking. This stays separate from Pluribus prediction accuracy and solver EV.')
        with st.form('v14_reflection', clear_on_submit=True):
            street = st.selectbox('Street', ['Preflop','Flop','Turn','River'])
            action = st.selectbox('Your action', ['Fold','Check','Call','Bet','Raise'])
            situation = st.text_area('Situation (position, cards, board, opponents, pot and action)')
            rationale = st.text_area('Why did you choose that action?')
            category = st.selectbox('Concept to study', ['Preflop range','3-bet sizing','Multiway play','Value betting','Bluff catching','Pot-cap math','Other'])
            save = st.form_submit_button('Save decision reflection')
        if save:
            if not situation.strip():
                st.warning('Describe the situation before saving.')
            else:
                if 'practice_session' not in st.session_state:
                    st.session_state.practice_session = db.start_session('montana_practice')
                db.decision(st.session_state.practice_session,'montana_practice',street,action,
                            {'origin':'manual_reflection','situation':situation,'rationale':rationale,'study_category':category},
                            feedback='Self-review; no EV calculation or action grade.')
                st.success('Reflection saved to the shared training database. Export a backup to retain it.')
    render_cap_explainer()
    with st.expander('Original QQ hand · historical review'):
        st.write('UTG+1 opens $6; CO calls; hero 3-bets QQ from SB to $22; both call. Flop 5-6-7 rainbow: hero bets $20, both call. Turn 4: hero checks, UTG+1 bets, CO raises, hero folds. Opponents held 78 and 88.')
        st.caption('Exact turn sizes unavailable; no invented EV or pot odds.')

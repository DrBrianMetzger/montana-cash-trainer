"""Montana Cash Game Trainer 1.1 — unified application."""
import json
import streamlit as st
from training_db import TrainingDB, uid, now
from personas import DEFAULTS, default_profile, validate_profile, POSITIONS, RANGE_TYPES
from game_engine import Game
from pluribus_trainer import render_pluribus_trainer
from gto_library import render_gto_library, KEY as GTO_KEY

st.set_page_config(page_title='Montana Cash Game Trainer',page_icon='♠',layout='wide')
db=TrainingDB()

# Existing modules keep their own widget/session state; DB mirrors their durable records.
if 'pb_results' not in st.session_state: st.session_state.pb_results={}
if GTO_KEY not in st.session_state: st.session_state[GTO_KEY]=db.references()
if 'pb_session' not in st.session_state: st.session_state.pb_session=db.start_session('pluribus_prediction')
if 'gto_session' not in st.session_state: st.session_state.gto_session=db.start_session('gto_exact')
if 'practice_session' not in st.session_state: st.session_state.practice_session=db.start_session('montana_practice')

# Restore saved Pluribus predictions into the original module's session state.
if not st.session_state.get('pb_db_loaded'):
    for r in db.rows('pluribus_predictions'):
        st.session_state.pb_results[r['hand_key']]={'guess':r['guess'],'actual':r['actual'],'street':r['street'],'hand':r['hand_key'].split('|')[0]}
    st.session_state.pb_db_loaded=True

st.title('♠ Montana Cash Game Trainer')
st.caption('Version 1.1 · historical study, prediction training, and shared data foundation')
sections=['Montana Practice Table','Pluribus Prediction Trainer','GTO+ Strategy Library','Opponent Lab — coming next','Leak Finder — coming next','Study Academy — coming later']
with st.sidebar:
    st.header('Training rooms')
    page=st.radio('Navigate',sections,key='navigation')
    st.divider()
    st.caption('Local SQLite storage on Streamlit Community Cloud is temporary. Export backups regularly.')
    st.download_button('Download complete backup',db.backup(),file_name='montana_training_backup.json',mime='application/json')
    uploaded=st.file_uploader('Restore complete backup',type=['json'],key='full_restore')
    if uploaded and st.button('Restore shared database'):
        try:
            count=db.restore(uploaded.getvalue());st.session_state[GTO_KEY]=db.references()
            st.session_state.pb_db_loaded=False
            st.success(f'Merged {count} records; reload to refresh predictions.')
        except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc: st.error(str(exc))

if page=='Montana Practice Table':
    st.header('Montana Practice Table')
    st.warning('The original QQ hand is preserved as a historical review, not an interactive replay. The small engine below is a separate rules-tested heads-up foundation, not a complete Montana multiway simulator.')
    with st.expander('Historical QQ hand — original exercise',expanded=True):
        st.write('UTG+1 opened to $6; CO called; hero 3-bet QQ from SB to $22; both called. Flop 5-6-7 rainbow: hero bet $20, both called. Turn 4: hero checked, UTG+1 bet, CO raised, hero folded. UTG+1 showed 78 and CO showed 88.')
        st.caption('Exact turn bet and raise sizes were not recorded. Historical analysis only; no invented pot odds or EV.')
    st.subheader('Decision-dependent engine · foundation')
    if 'game' not in st.session_state: st.session_state.game=Game()
    game=st.session_state.game
    if st.button('New practice hand'):
        st.session_state.game=Game();st.session_state.practice_session=db.start_session('montana_practice');st.rerun()
    a,b,c=st.columns(3);a.metric('Pot (gross)',f'${game.pot:.2f}');b.metric('Hero remaining',f'${game.hero_stack:.2f}');c.metric('To call',f'${game.amount_to_call():.2f}')
    st.write(f'**Street:** {game.street} · **Turn:** {game.to_act} · **Pot cap:** $800 gross, including rake')
    if game.ended: st.success(game.outcome)
    elif game.to_act=='hero':
        options=game.legal();choice=st.selectbox('Hero action',options)
        amount=None
        if choice in ('Bet','Raise'):
            minimum=2.0 if choice=='Bet' else game.villain_street+game.min_raise
            amount=st.number_input('Bet amount (bet: dollars; raise: total street contribution)',min_value=float(minimum),value=float(minimum),step=1.0)
        if st.button('Apply hero action',type='primary'):
            try:
                before={'pot':game.pot,'to_call':game.amount_to_call(),'street':game.street}
                game.act(choice,amount)
                db.decision(st.session_state.practice_session,'montana_practice',before['street'],choice,dict(before,amount=amount,after_pot=game.pot),hand_id=None)
                st.rerun()
            except ValueError as exc: st.error(str(exc))
    else:
        st.info('Select a scripted opponent response for engine testing. Personas do not yet act autonomously.')
        to_call=max(0,game.hero_street-game.villain_street)
        response=st.selectbox('Opponent response', ['Fold','Call'] if to_call>0 else ['Check','Bet'])
        opp_amount=st.number_input('Opponent bet ($)',min_value=2.0,value=2.0) if response=='Bet' else None
        if st.button('Apply opponent response'):
            try: game.opponent(response,opp_amount);st.rerun()
            except ValueError as exc: st.error(str(exc))
    st.code('\n'.join(game.history) or 'No actions yet',language=None)
    st.caption('No automatic board runout, rake deduction, multiway opponent logic, or cap-overflow handling is claimed in this foundation.')
elif page=='Pluribus Prediction Trainer':
    render_pluribus_trainer()
    # Original trainer writes session state on reveal; synchronize by stable hand/action key.
    for key,r in st.session_state.pb_results.items():
        db.save_prediction(st.session_state.pb_session,key,r['guess'],r['actual'],r['street'],{'hand':r.get('hand')})
elif page=='GTO+ Strategy Library':
    render_gto_library()
    for item in st.session_state[GTO_KEY]: db.save_reference(item)
    st.caption('References are mirrored to the shared SQLite database. GTO exact-practice decisions are not scored as EV loss without verified EV data.')
elif page=='Opponent Lab — coming next':
    st.header('Opponent Lab · profile editor foundation')
    name=st.selectbox('Opponent',list(DEFAULTS))
    saved={r['id']:json.loads(r['profile']) for r in db.rows('personas')}
    profile=saved.get(name,default_profile(name))
    with st.form(f'profile_{name}'):
        description=st.text_input('Description',value=profile['description'])
        notes=st.text_area('Notes',value=profile.get('notes',''))
        pos=st.selectbox('Position',POSITIONS)
        ranges={kind:st.text_input(kind.replace('_',' ').title()+' range (text, not validated by solver)',value=profile['ranges'][pos][kind]) for kind in RANGE_TYPES}
        st.caption('Leave tendencies blank when not measured. Values are percentages, not GTO outputs.')
        tendencies={k:st.text_input(k.replace('_',' ').title()+' (%)',value='' if v is None else str(v)) for k,v in profile['tendencies'].items()}
        adapt=st.checkbox('Allow future adaptation',value=profile['adaptation']['enabled'])
        speed=st.slider('Future adaptation speed',0.0,1.0,float(profile['adaptation']['speed']),0.05)
        if st.form_submit_button('Save profile'):
            try:
                profile['description']=description;profile['notes']=notes;profile['ranges'][pos].update(ranges)
                profile['tendencies']={k:(float(v) if v.strip() else None) for k,v in tendencies.items()}
                profile['adaptation'].update(enabled=adapt,speed=speed)
                validate_profile(profile)
                db.insert('personas',{'id':name,'name':name,'profile':json.dumps(profile),'updated_utc':now()},replace=True)
                st.success('Profile saved in SQLite. Export a backup to preserve it across redeployments.')
            except (ValueError,TypeError,KeyError) as exc: st.error(str(exc))
    st.info('The 13×13 range grid and playable opponents are reserved for the next release.')
elif page=='Leak Finder — coming next':
    st.header('Leak Finder · foundation')
    rows=db.rows('decisions')
    st.write(f'{len(rows)} decisions recorded in the shared database.')
    for source in ('montana_practice','pluribus_prediction','gto_exact','live_review'):
        st.metric(source.replace('_',' ').title(),sum(r['source']==source for r in rows))
    st.caption('Sources remain separate. Pluribus prediction accuracy is not poker EV; GTO frequency is not EV loss.')
else:
    st.header('Study Academy · coming later')
    st.info('Curriculum and guided lessons are reserved for a later release.')

"""Adaptive drill room: reuse existing Helena felt/table and shared decision DB."""
import streamlit as st
from helena_course import visual_table
from drill_engine import categories, generate, parse_records, pick_category, record_context, summary

KEY='mct17'

def _next(category):
    state=st.session_state
    recent=state.get(KEY+'_recent', [])
    item=generate(category, recent_ids=recent)
    state[KEY+'_recent']=(recent+[item['id']])[-15:]
    state[KEY+'_hand']=item
    state[KEY+'_answer']=None
    state[KEY+'_category']=category

def render_adaptive_drills(db):
    st.header('🎯 Adaptive Drills · Version 1.7')
    st.caption('Strategically curated, randomized scenarios · opponent hypotheses · not verified GTO or EV')
    records=parse_records(db)
    stats=summary(records)
    a,b,c=st.columns(3)
    a.metric('Decisions practiced',len(records))
    b.metric('Baseline agreement', f"{sum(bool(r.get('matches_baseline')) for r in records)}/{len(records)}")
    c.metric('Categories due',sum(x['due'] for x in stats.values()))
    options=['Recommended for me']+categories()
    selected=st.selectbox('Training focus',options,key=KEY+'_select')
    category=pick_category(records) if selected=='Recommended for me' else selected
    if selected=='Recommended for me':
        st.caption(f'Recommended focus: **{category}** (due review, unpracticed category, or additional repetition).')
    if KEY+'_hand' not in st.session_state or (selected!='Recommended for me' and st.session_state.get(KEY+'_category')!=category):
        _next(category)
    item=st.session_state[KEY+'_hand']
    st.subheader(item['lesson'])
    st.info(item['question'])
    visual_table(item)
    st.caption(f"Opponent: {item['persona']} · {item['position']} · ${item['stack']} effective (illustrative) · {item['source_label']}")
    if item.get('pot') is not None:
        a,b=st.columns(2)
        a.metric('Gross pot',f"${item['pot']}")
        b.metric('Remaining to cap',f"${max(0,800-item['pot'])}")
    if st.session_state.get(KEY+'_answer') is None:
        confidence=st.select_slider('How confident are you?', options=['Low','Medium','High'],value='Medium',key=KEY+'_confidence')
        cols=st.columns(len(item['actions']))
        for i,(col,action) in enumerate(zip(cols,item['actions'])):
            if col.button(action,key=f'{KEY}_act_{i}',use_container_width=True):
                context=record_context(item,action,confidence,records)
                if KEY+'_session' not in st.session_state:
                    st.session_state[KEY+'_session']=db.start_session('montana_practice',{'course':'adaptive_drills'})
                db.decision(st.session_state[KEY+'_session'],'montana_practice',item['street'],action,context,feedback=item['reason'])
                st.session_state[KEY+'_answer']={'action':action,'context':context}
                st.rerun()
    else:
        answer=st.session_state[KEY+'_answer']
        st.write('**Your action:**',answer['action'])
        st.write('**Suggested coaching baseline:**',item['baseline'])
        st.write(item['reason'])
        st.caption('This is qualitative guidance under stated assumptions. A different opponent range can justify a different action. Agreement is not solver accuracy.')
        st.write('**Next review scheduled:**',answer['context']['review_due'])
        if st.button('Next randomized decision',type='primary',key=KEY+'_next'):
            next_cat=pick_category(parse_records(db)) if selected=='Recommended for me' else selected
            _next(next_cat)
            st.rerun()
    with st.expander('Practice progress by concept'):
        if not stats: st.info('Your progress appears here after the first decision.')
        else:
            st.dataframe([{'Category':k,'Decisions':v['attempts'],'Baseline matches':v['baseline_matches'],'Due for review':bool(v['due'])} for k,v in stats.items()],hide_index=True,use_container_width=True)
        st.caption('Review dates are saved in the existing decision database; export a backup regularly. The scheduling system is an initial heuristic, not a validated mastery estimate.')

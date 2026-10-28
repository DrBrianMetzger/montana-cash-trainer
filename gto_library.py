"""GTO+ screenshot library module for Streamlit.
Call render_gto_library() from an existing Streamlit application.
No OCR, solver decoding, or automatic GTO claims are made.
"""
import base64
import json
import uuid
from datetime import datetime, timezone
import streamlit as st

KEY = 'gto_plus_library_v1'
ACTIONS = ['Check', 'Bet 25%', 'Bet 33%', 'Bet 50%', 'Bet 75%', 'Bet 100%', 'Bet 125%', 'Other']

def _state():
    if KEY not in st.session_state:
        st.session_state[KEY] = []
    return st.session_state[KEY]

def _normalize(raw):
    if not isinstance(raw, list):
        raise ValueError('Expected a JSON list of saved solutions.')
    out = []
    for entry in raw:
        if not isinstance(entry, dict) or not isinstance(entry.get('board'), str):
            raise ValueError('Each solution must contain a board.')
        if not isinstance(entry.get('frequencies'), dict):
            raise ValueError('Each solution must contain a frequencies dictionary.')
        freqs = {str(k): float(v) for k, v in entry['frequencies'].items()}
        if any(v < 0 or v > 100 for v in freqs.values()) or abs(sum(freqs.values())-100)>1.5:
            raise ValueError('Action frequencies must total approximately 100%.')
        clean = dict(entry)
        clean['frequencies'] = freqs
        clean['id'] = str(entry.get('id') or uuid.uuid4().hex)
        out.append(clean)
    return out

def render_gto_library():
    st.header('GTO+ Screenshot Library')
    st.caption('Reference-based practice and strategy calibration. Screenshots are not automatically decoded or solved.')
    library = _state()
    tab_add, tab_practice, tab_patterns, tab_data = st.tabs(['Add solution', 'Exact practice', 'Strategy patterns', 'Backup / restore'])

    with tab_add:
        st.write('Upload a GTO+ strategy screenshot, then transcribe the frequencies for one specific hand combination and decision node.')
        with st.form('gto_add_form', clear_on_submit=False):
            shot = st.file_uploader('GTO+ screenshot (PNG/JPG)', type=['png','jpg','jpeg'])
            name = st.text_input('Solution name', placeholder='QQT LJ vs BTN 25BB')
            board = st.text_input('Board (cards with suits)', placeholder='Qd Qc Td')
            hero = st.text_input('Exact hero hand', placeholder='As Js')
            matchup = st.text_input('Positions', placeholder='LJ vs BTN')
            game = st.selectbox('Game type', ['Cash', 'Tournament chip EV', 'Tournament ICM', 'Other / unknown'])
            depth = st.number_input('Effective stack (BB)', min_value=1.0, max_value=1000.0, value=25.0)
            pot = st.number_input('Pot at decision (BB)', min_value=0.0, value=5.0)
            street = st.selectbox('Street', ['Flop','Turn','River'])
            node = st.text_input('Action history / decision node', placeholder='Preflop LJ raise, BTN call; LJ to act')
            texture = st.selectbox('Board texture', ['Paired', 'Dry', 'Two-tone', 'Monotone', 'Connected', 'Other'])
            st.markdown('**Actions and frequencies for the exact selected hand**')
            st.caption('Enter up to four action labels and their solver frequencies. Use 0 for unavailable actions; total must equal 100%.')
            defaults = [('Check', 100.0), ('Bet 33%', 0.0), ('Bet 75%', 0.0), ('Other', 0.0)]
            entries=[]
            for idx,(label,freq) in enumerate(defaults):
                a,b=st.columns([2,1])
                with a: action=st.text_input(f'Action {idx+1}', value=label, key=f'gtol_action_{idx}')
                with b: percentage=st.number_input(f'Frequency {idx+1} (%)', min_value=0.0, max_value=100.0, value=freq, step=1.0, key=f'gtol_pct_{idx}')
                entries.append((action.strip(),percentage))
            ev_text=st.text_input('Optional action EVs, in BB (JSON)', placeholder='{"Check": 1.25, "Bet 33%": 1.23}')
            notes=st.text_area('Strategy notes / solver assumptions', placeholder='Ranges, rake, pot cap, bet tree, exploitative adjustments...')
            verified=st.checkbox('I checked these values against the GTO+ strategy grid')
            submitted=st.form_submit_button('Save reference')
        if submitted:
            try:
                if not name.strip() or not board.strip() or not hero.strip() or not matchup.strip() or not node.strip():
                    raise ValueError('Complete name, board, hero hand, positions, and action history.')
                if not shot:
                    raise ValueError('Upload a screenshot to support this reference.')
                frequencies={}
                for label, value in entries:
                    if label:
                        if label in frequencies: raise ValueError('Action labels must be unique.')
                        frequencies[label]=value
                if abs(sum(frequencies.values())-100)>0.5:
                    raise ValueError('Action frequencies must total 100%.')
                ev=json.loads(ev_text) if ev_text.strip() else {}
                if not isinstance(ev,dict) or any(k not in frequencies for k in ev):
                    raise ValueError('EV JSON must map existing action names to numbers.')
                ev={k:float(v) for k,v in ev.items()}
                item=dict(id=uuid.uuid4().hex,name=name.strip(),board=board.strip(),hero=hero.strip(),matchup=matchup.strip(),game=game,depth=depth,pot=pot,street=street,node=node.strip(),texture=texture,frequencies=frequencies,ev=ev,notes=notes,verified=verified,created=datetime.now(timezone.utc).isoformat(),image_name=shot.name,image_mime=shot.type,image_b64=base64.b64encode(shot.getvalue()).decode('ascii'))
                library.append(item)
                st.success('Reference added to the current session. Export a backup to keep it permanently.')
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                st.error(str(exc))

    with tab_practice:
        if not library:
            st.info('Add a screenshot reference first.')
        else:
            chosen=st.selectbox('Select a saved solver decision', range(len(library)), format_func=lambda i: library[i].get('name','Untitled')+' — '+library[i].get('hero',''))
            item=library[chosen]
            st.write(f"**{item['board']}** · {item.get('matchup','')} · {item.get('hero','')} · {item.get('street','')}")
            st.caption(f"{item.get('node','')} | {item.get('game','')} | {item.get('depth','?')} BB effective")
            if not item.get('verified'):
                st.warning('This reference has not been marked verified against GTO+.')
            options=list(item['frequencies'])
            decision=st.radio('What would you do?', options, key='gto_practice_action')
            if st.button('Reveal solver comparison'):
                st.write('**Solver action frequencies (transcribed)**')
                for action, freq in item['frequencies'].items():
                    st.write(f'{action}: {freq:.1f}%')
                    st.progress(min(max(freq/100,0),1))
                st.write(f'Your selected action: **{decision}** ({item["frequencies"].get(decision,0):.1f}% solver frequency).')
                if item.get('ev') and decision in item['ev']:
                    best=max(item['ev'].values())
                    loss=best-item['ev'][decision]
                    st.write(f'EV of selected action: {item["ev"][decision]:.3f} BB; gap to highest listed EV: {loss:.3f} BB.')
                    st.caption('EV comparison uses only the supplied action EVs; it is not a newly calculated solution.')
                else:
                    st.info('No per-action EV available. Frequency alone does not measure EV loss.')
                if item.get('image_b64'):
                    st.image(base64.b64decode(item['image_b64']), caption='Original GTO+ screenshot')

    with tab_patterns:
        if not library:
            st.info('Strategy patterns will appear as you add verified references.')
        else:
            verified=[x for x in library if x.get('verified')]
            st.metric('Saved references',len(library))
            st.metric('Verified references',len(verified))
            st.caption('Descriptive library index only. No extrapolated GTO claims or automatic strategy tuning.')
            for x in library:
                with st.expander(f"{x.get('name','Untitled')} · {x.get('texture','')} · {x.get('hero','')}"):
                    st.write(f"Board: {x.get('board','')} | {x.get('matchup','')} | {x.get('game','')}")
                    st.write(x.get('frequencies',{}))
                    st.write(x.get('notes',''))

    with tab_data:
        st.warning('Streamlit Community Cloud local/session data may disappear after a restart. Download a backup after adding references. Images embedded in JSON make files larger.')
        st.download_button('Download full library (JSON, including screenshots)',data=json.dumps(library,indent=2),file_name='gto_plus_library.json',mime='application/json')
        restore=st.file_uploader('Restore previously downloaded library JSON',type=['json'],key='gto_restore')
        if restore and st.button('Import / merge backup'):
            try:
                incoming=_normalize(json.load(restore))
                existing={x['id'] for x in library}
                new=[x for x in incoming if x['id'] not in existing]
                library.extend(new)
                st.success(f'Imported {len(new)} new references.')
            except (ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
                st.error(f'Invalid library file: {exc}')
        if library:
            idx=st.selectbox('Remove a reference',range(len(library)),format_func=lambda i:library[i].get('name','Untitled'))
            if st.button('Delete selected reference'):
                library.pop(idx)
                st.rerun()

if __name__ == '__main__':
    st.set_page_config(page_title='GTO+ Strategy Library',layout='wide')
    render_gto_library()

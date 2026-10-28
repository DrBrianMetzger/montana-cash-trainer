"""Pluribus historical decision trainer. Import with render_pluribus_trainer().
No live Pluribus model, EV claims, or counterfactual continuation.
"""
import io
import random
import urllib.request
import urllib.error
import json
import tomllib
import zipfile
import streamlit as st

SAMPLE = '''variant = 'NT'
ante_trimming_status = true
antes = [0, 0, 0, 0, 0, 0]
blinds_or_straddles = [50, 100, 0, 0, 0, 0]
min_bet = 100
starting_stacks = [10000, 10000, 10000, 10000, 10000, 10000]
actions = ['d dh p1 5c2c', 'd dh p2 Ac3s', 'd dh p3 Js8h', 'd dh p4 5h5s', 'd dh p5 As9s', 'd dh p6 JhJc', 'p3 f', 'p4 cbr 250', 'p5 cbr 775', 'p6 cc', 'p1 f', 'p2 f', 'p4 cc', 'd db KsKc5d', 'p4 cc', 'p5 cc', 'p6 cbr 750', 'p4 cbr 2737', 'p5 f', 'p6 f']
hand = 32
players = ['MrBlue', 'MrPink', 'Eddie', 'Pluribus', 'Bill', 'MrWhite']
finishing_stacks = [9950, 9900, 10000, 12450, 9225, 8475]
'''
SAMPLE2 = '''variant = 'NT'
ante_trimming_status = true
antes = [0, 0, 0, 0, 0, 0]
blinds_or_straddles = [50, 100, 0, 0, 0, 0]
min_bet = 100
starting_stacks = [10000, 10000, 10000, 10000, 10000, 10000]
actions = ['d dh p1 AsAc', 'd dh p2 Kh7c', 'd dh p3 Kc9s', 'd dh p4 4hQc', 'd dh p5 Qh2s', 'd dh p6 3d6h', 'p3 f', 'p4 f', 'p5 f', 'p6 f', 'p1 cbr 250', 'p2 cc', 'd db Kd6d7h', 'p1 cbr 375', 'p2 cbr 1312', 'p1 cc', 'd db Js', 'p1 cc', 'p2 cbr 2343', 'p1 cc', 'd db Qs', 'p1 cc', 'p2 cbr 6095', 'p1 f']
hand = 19
players = ['MrWhite', 'MrBlue', 'MrPink', 'Eddie', 'Pluribus', 'Bill']
finishing_stacks = [6095, 13905, 10000, 10000, 10000, 10000]
'''

def parse_hand(data, name):
    h = tomllib.loads(data)
    if h.get('variant') != 'NT' or not isinstance(h.get('actions'), list):
        raise ValueError('Expected a no-limit Texas hold’em .phh file with actions.')
    if not isinstance(h.get('players'), list) or not h['players']:
        raise ValueError('Missing player names.')
    if not isinstance(h.get('blinds_or_straddles'), list):
        raise ValueError('Missing blind information.')
    h['_name'] = name
    return h

def parse_uploads(upload):
    if upload is None:
        return []
    blob = upload.getvalue()
    if len(blob) > 15_000_000:
        raise ValueError('Maximum upload size is 15 MB.')
    if upload.name.lower().endswith('.zip'):
        hands=[]
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            entries=[i for i in z.infolist() if i.filename.lower().endswith('.phh') and not i.is_dir()]
            if len(entries)>1500:
                raise ValueError('Upload at most 1,500 PHH files at a time.')
            for i in entries:
                if i.file_size>100_000:
                    continue
                try: hands.append(parse_hand(z.read(i).decode('utf-8'), i.filename))
                except (ValueError,UnicodeDecodeError): continue
        if not hands: raise ValueError('No valid .phh hands found in ZIP.')
        return hands
    return [parse_hand(blob.decode('utf-8'),upload.name)]

def player_action(a):
    p=a.split()
    if len(p)<2 or not p[0].startswith('p') or not p[0][1:].isdigit(): return None
    return int(p[0][1:])-1,p[1],p[2] if len(p)>2 else None

def readable(a,bb):
    p=player_action(a)
    if p is None:return a
    _,kind,value=p
    if kind=='f':return 'Fold'
    if kind=='cc':return 'Check / call'
    if kind=='cbr':return f'Bet / raise to {int(value)/bb:g} BB' if value and value.isdigit() else 'Bet / raise'
    return a

def board_at(actions,idx):
    board=''
    for a in actions[:idx]:
        if a.startswith('d db '):board+=a[5:].strip()
    return ' '.join(board[i:i+2] for i in range(0,len(board),2)) or 'Preflop'

def hole_for(actions,seat):
    for a in actions:
        if a.startswith(f'd dh p{seat+1} '):
            s=a.split()[-1]
            return ' '.join(s[i:i+2] for i in range(0,len(s),2))
    return 'Not recorded'


BASE_URL = "https://raw.githubusercontent.com/uoftcprg/phh-dataset/main/data/pluribus"

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_github_hand(relative_path):
    # Restrict fetching to the fixed, public dataset origin.
    import re
    if not re.fullmatch(r"[0-9]+/[0-9]+\.phh", relative_path):
        raise ValueError("Enter a path such as 97/32.phh")
    url = f"{BASE_URL}/{relative_path}"
    req = urllib.request.Request(url, headers={"User-Agent": "MontanaCashTrainer/2.2"})
    with urllib.request.urlopen(req, timeout=12) as response:
        data = response.read(100_001)
    if len(data)>100_000:
        raise ValueError("File exceeds the 100 KB limit")
    return parse_hand(data.decode("utf-8"), f"GitHub {relative_path}")

def action_class(action):
    p = player_action(action)
    return {"f":"Fold", "cc":"Check / call", "cbr":"Bet / raise"}.get(p[1], "Other") if p else "Other"

def street_at(actions, idx):
    n = sum(1 for a in actions[:idx] if a.startswith('d db '))
    return ["Preflop", "Flop", "Turn", "River"][min(n,3)]

def reasoning(h, at, actual, seat, bb):
    street=street_at(h['actions'],at)
    cls=action_class(actual)
    context={
      'Fold':'Folding avoids investing additional chips when the expected return from continuing may be inadequate.',
      'Check / call':'Checking or calling can preserve weaker hands in the opponent range, control pot size, or realize equity.',
      'Bet / raise':'Betting or raising can generate value, fold equity, or deny opponents the chance to realize their equity cheaply.'
    }.get(cls,'Review the action in its full betting context.')
    caveat=('Preflop position, prior raises, stack depth, and players remaining are important.' if street=='Preflop'
            else 'Board texture, range advantage, blockers, previous bets, and remaining opponents are important.')
    return f"**Possible strategic rationale (not Pluribus internal reasoning):** {context} {caveat} One observed action does not establish its strategy frequency or prove alternatives wrong."

def render_pluribus_trainer():
    st.header('Pluribus Prediction Trainer · v2.2')
    st.caption('Predict the recorded Pluribus action, reveal it, then study the context. Historical data, not a live AI or EV solver.')
    if 'pb_hands' not in st.session_state:
        st.session_state.pb_hands=[parse_hand(SAMPLE,'Published sample 97/32.phh'),parse_hand(SAMPLE2,'Published sample 97/19.phh')]
    if 'pb_results' not in st.session_state: st.session_state.pb_results={}
    if 'pb_index' not in st.session_state: st.session_state.pb_index=0
    if 'pb_cursor' not in st.session_state: st.session_state.pb_cursor=0
    if 'pb_answer' not in st.session_state: st.session_state.pb_answer=None
    with st.expander('Load more historical hands from GitHub',expanded=False):
        st.write('The app fetches only the selected hand. No bulk download or GitHub account is required.')
        path=st.text_input('Dataset path',value='97/32.phh',help='Relative to data/pluribus, e.g. 97/19.phh')
        if st.button('Fetch hand from GitHub',key='pb_fetch'):
            try:
                hand=fetch_github_hand(path.strip())
                if not any(x['_name']==hand['_name'] for x in st.session_state.pb_hands):
                    st.session_state.pb_hands.append(hand)
                st.session_state.pb_index=next(i for i,x in enumerate(st.session_state.pb_hands) if x['_name']==hand['_name'])
                st.session_state.pb_cursor=0
                st.session_state.pb_answer=None
                st.success(f"Loaded {path}")
                st.rerun()
            except (ValueError,UnicodeDecodeError,urllib.error.URLError,TimeoutError) as exc:
                st.error(f'Could not load hand: {exc}')
        st.markdown('[Browse Pluribus dataset on GitHub](https://github.com/uoftcprg/phh-dataset/tree/main/data/pluribus)')
        uploaded=st.file_uploader('Or upload .phh / ZIP',type=['phh','zip'],key='pb_upload')
        if uploaded and st.button('Import uploaded hands',key='pb_import'):
            try:
                imported=parse_uploads(uploaded)
                st.session_state.pb_hands.extend(imported)
                st.session_state.pb_index=len(st.session_state.pb_hands)-len(imported)
                st.session_state.pb_cursor=0
                st.session_state.pb_answer=None
                st.success(f'Imported {len(imported)} hands into this session.')
                st.rerun()
            except (ValueError,UnicodeDecodeError,zipfile.BadZipFile) as exc: st.error(str(exc))
    hands=st.session_state.pb_hands
    idx=st.selectbox('Choose historical hand',range(len(hands)),index=min(st.session_state.pb_index,len(hands)-1),format_func=lambda i:f'{hands[i]["_name"]} — hand {hands[i].get("hand","?")}',key='pb_hand_select_v22')
    if idx!=st.session_state.pb_index:
        st.session_state.pb_index=idx;st.session_state.pb_cursor=0;st.session_state.pb_answer=None
    h=hands[idx]; players=h['players']
    seats=[i for i,name in enumerate(players) if name=='Pluribus']
    if not seats:
        st.warning('No Pluribus seat found. Select another hand for Pluribus prediction training.')
        return
    seat=seats[0]
    bb=max([float(x) for x in h['blinds_or_straddles'] if float(x)>0] or [100])
    decisions=[(i,a) for i,a in enumerate(h['actions']) if (p:=player_action(a)) is not None and p[0]==seat]
    if not decisions: st.info('No Pluribus decisions in this hand.');return
    cursor=min(st.session_state.pb_cursor,len(decisions)-1)
    at,actual=decisions[cursor]
    street=street_at(h['actions'],at)
    st.subheader(f'Predict Pluribus · Decision {cursor+1}/{len(decisions)} · {street}')
    st.write(f'**Pluribus hole cards:** {hole_for(h["actions"],seat)} · **Board:** {board_at(h["actions"],at)}')
    st.write(f'**Starting stack:** {float(h["starting_stacks"][seat])/bb:g} BB · **Players:** {len(players)} at start')
    previous=[]
    for action in h['actions'][:at]:
        p=player_action(action)
        if p is not None and 0<=p[0]<len(players): previous.append(f'{players[p[0]]}: {readable(action,bb)}')
        elif action.startswith('d db '):previous.append(f'Board dealt: {action[5:]}')
    st.markdown('**Recorded action history before this decision**')
    st.code('\n'.join(previous[-22:]) or 'No player actions yet',language=None)
    st.caption('Check/call is a combined category in PHH. The three prediction categories are not guaranteed to be legal alternatives at every node.')
    key=f'{h["_name"]}|{h.get("hand","")}|{seat}|{at}'
    answer=st.radio('What will Pluribus do?', ['Fold','Check / call','Bet / raise'],key=f'pb_pred_{idx}_{seat}_{cursor}',disabled=st.session_state.pb_answer is not None)
    if st.session_state.pb_answer is None:
        if st.button('Lock prediction and reveal',key='pb_reveal_v22',type='primary'):
            st.session_state.pb_answer=answer
            st.session_state.pb_results[key]={'guess':answer,'actual':action_class(actual),'street':street,'hand':h['_name']}
            st.rerun()
    else:
        result=st.session_state.pb_results.get(key)
        guess=st.session_state.pb_answer
        correct=guess==action_class(actual)
        (st.success if correct else st.warning)('Correct prediction!' if correct else 'Different from the historical action.')
        st.markdown(f'**Your prediction:** {guess}  \n**Recorded Pluribus action:** {readable(actual,bb)}')
        st.info(reasoning(h,at,actual,seat,bb))
        st.caption('A mismatch measures prediction accuracy, not whether your action would have lower EV. If you changed the action, later recorded actions would no longer be a valid continuation.')
        c1,c2=st.columns(2)
        with c1:
            if st.button('Next Pluribus decision',disabled=cursor+1>=len(decisions),key='pb_next_v22'):
                st.session_state.pb_cursor=cursor+1;st.session_state.pb_answer=None;st.rerun()
        with c2:
            if st.button('Restart this hand',key='pb_restart_v22'):
                st.session_state.pb_cursor=0;st.session_state.pb_answer=None;st.rerun()
    st.divider()
    st.subheader('Prediction accuracy')
    results=list(st.session_state.pb_results.values())
    if results:
        hits=sum(x['guess']==x['actual'] for x in results)
        a,b,c=st.columns(3)
        a.metric('Predictions',len(results));b.metric('Correct',hits);c.metric('Accuracy',f'{100*hits/len(results):.1f}%')
        bystreet={}
        for x in results:
            n,k=bystreet.get(x['street'],(0,0))
            bystreet[x['street']]=(n+1,k+int(x['guess']==x['actual']))
        st.dataframe([{'Street':s,'Predictions':n,'Accuracy':f'{100*k/n:.1f}%'} for s,(n,k) in bystreet.items()],hide_index=True,use_container_width=True)
        st.download_button('Download prediction history (JSON)',data=json.dumps(results,indent=2),file_name='pluribus_predictions.json',mime='application/json')
    else:st.caption('Make your first prediction to start tracking accuracy.')
    st.caption('Source: University of Toronto PHH dataset, Pluribus subset. Github-loaded hands are cached for 24 hours; prediction history is session-only unless downloaded.')

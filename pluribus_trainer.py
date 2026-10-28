"""Pluribus historical decision trainer. Import with render_pluribus_trainer().
No live Pluribus model, EV claims, or counterfactual continuation.
"""
import io
import random
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

def render_pluribus_trainer():
    st.header('Pluribus Historical Challenge')
    st.caption('Practice decisions from recorded six-player hands. Not a live Pluribus AI or an EV solver.')
    if 'pb_hands' not in st.session_state:
        st.session_state.pb_hands=[parse_hand(SAMPLE,'Published sample 97/32.phh'),parse_hand(SAMPLE2,'Published sample 97/19.phh')]
    uploaded=st.file_uploader('Add historical .phh hand or ZIP of .phh files',type=['phh','zip'],key='pb_upload')
    if uploaded and st.button('Import hand histories',key='pb_import'):
        try:
            imported=parse_uploads(uploaded)
            st.session_state.pb_hands.extend(imported)
            st.session_state.pb_index=len(st.session_state.pb_hands)-len(imported)
            st.session_state.pb_cursor=0
            st.session_state.pb_answer=None
            st.success(f'Imported {len(imported)} hands for this session.')
        except (ValueError,UnicodeDecodeError,zipfile.BadZipFile) as exc:
            st.error(str(exc))
    hands=st.session_state.pb_hands
    if 'pb_index' not in st.session_state:st.session_state.pb_index=0
    idx=st.selectbox('Choose historical hand',range(len(hands)),index=min(st.session_state.pb_index,len(hands)-1),format_func=lambda i:f'{hands[i]["_name"]} — hand {hands[i].get("hand","?")}',key='pb_hand_select')
    if idx!=st.session_state.pb_index:
        st.session_state.pb_index=idx
        st.session_state.pb_cursor=0
        st.session_state.pb_answer=None
    h=hands[idx]
    players=h['players']
    seats=[i for i,a in enumerate(players) if a=='Pluribus']
    if not seats:
        st.warning('This hand does not contain a Pluribus seat; you can still replay another player.')
        seats=list(range(len(players)))
    seat=st.selectbox('Take the seat of',seats,format_func=lambda i:f'Seat {i+1}: {players[i]}',key=f'pb_seat_{idx}')
    bb=max([float(x) for x in h['blinds_or_straddles'] if float(x)>0] or [100])
    decisions=[(i,a) for i,a in enumerate(h['actions']) if (p:=player_action(a)) is not None and p[0]==seat]
    if not decisions:
        st.info('No recorded decisions for this seat. Select another hand.')
        return
    if 'pb_cursor' not in st.session_state:st.session_state.pb_cursor=0
    if 'pb_answer' not in st.session_state:st.session_state.pb_answer=None
    cursor=min(st.session_state.pb_cursor,len(decisions)-1)
    at,actual=decisions[cursor]
    st.markdown(f'**Decision {cursor+1} of {len(decisions)}** · **{board_at(h["actions"],at)}**')
    st.write(f'Your hole cards: **{hole_for(h["actions"],seat)}** · Effective starting stack: {float(h["starting_stacks"][seat])/bb:g} BB')
    st.write('**Previous recorded actions:**')
    previous=[]
    for action in h['actions'][:at]:
        p=player_action(action)
        if p is not None:previous.append(f'{players[p[0]]}: {readable(action,bb)}')
        elif action.startswith('d db '):previous.append(f'Board: {action[5:]}')
    st.code('\n'.join(previous[-18:]) or 'No actions yet',language=None)
    st.caption('Bet/raise figures are recorded target contribution amounts, displayed in BB; they are not guaranteed to be legal alternatives in a changed action tree.')
    answer=st.radio('What would you do?', ['Fold','Check / call','Bet / raise'],key=f'pb_choice_{idx}_{seat}_{cursor}')
    size=None
    if answer=='Bet / raise':size=st.number_input('Your intended bet / raise target (BB)',min_value=0.5,value=3.0,step=0.5,key=f'pb_size_{idx}_{seat}_{cursor}')
    if st.button('Reveal historical action',key='pb_reveal'):
        st.session_state.pb_answer=(answer,size)
    if st.session_state.pb_answer is not None:
        st.success(f'Historical action by {players[seat]}: **{readable(actual,bb)}**')
        st.write(f'Your choice: **{answer}**'+(f' to {size:g} BB' if size is not None else ''))
        st.info('This is a comparison with a recorded action, not proof your decision is incorrect or an EV calculation. Changing the action would change subsequent game states.')
        c1,c2=st.columns(2)
        with c1:
            if st.button('Next decision',disabled=cursor+1>=len(decisions)):
                st.session_state.pb_cursor=cursor+1
                st.session_state.pb_answer=None
                st.rerun()
        with c2:
            if st.button('Restart hand'):
                st.session_state.pb_cursor=0
                st.session_state.pb_answer=None
                st.rerun()
    st.caption('Data: University of Toronto PHH dataset, Pluribus subset (Brown & Sandholm 2019). Sample hands 97/32 and 97/19. Uploaded hands remain in session memory only.')

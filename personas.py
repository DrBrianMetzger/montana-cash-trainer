"""Editable profile data only; no simulated GTO or autonomous persona behavior."""
import copy
from training_db import now

DEFAULTS={
 'SantiNobu':('GTO-oriented, observant and exploitative','adaptive'),
 'PedaltotheMetalLisa':('High-frequency bettor and multi-street barreler','aggressive'),
 'MoleculeMike':('Conservative, value-heavy, infrequent bluffer','conservative'),
 'HelenaHomie':('Tight-aggressive positionally aware regular','tag'),
}
POSITIONS=('UTG','HJ','CO','BTN','SB','BB')
RANGE_TYPES=('open','three_bet','four_bet','call_open','call_three_bet')

def default_profile(name):
    description,style=DEFAULTS[name]
    return {'name':name,'description':description,'style':style,'ranges':{p:{r:'' for r in RANGE_TYPES} for p in POSITIONS},
            'tendencies':{'flop_cbet':None,'turn_aggression':None,'river_aggression':None,'bluff_frequency':None,'value_bet_frequency':None,'bet_size_sensitivity':None},
            'adaptation':{'enabled':False,'speed':0.0,'notes':''},'notes':'Ranges and frequencies are uncalibrated until entered by the user.'}

def validate_profile(profile):
    if not isinstance(profile,dict) or not isinstance(profile.get('name'),str): raise ValueError('Invalid profile')
    for pos in POSITIONS:
        for kind in RANGE_TYPES:
            if not isinstance(profile['ranges'][pos][kind],str): raise ValueError('Ranges must be text until grid editor is implemented')
    for key,value in profile['tendencies'].items():
        if value is not None and not (0<=float(value)<=100): raise ValueError(f'{key} must be 0–100%')
    return copy.deepcopy(profile)

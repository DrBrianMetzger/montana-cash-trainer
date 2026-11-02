"""MCT 1.7 adaptive, source-labelled drill selection. No poker EV claims."""
from __future__ import annotations
import hashlib
import json
import random
from datetime import date, timedelta
from helena_course import LESSONS, scenario, a4_scenario

SOURCE = 'heuristic_coaching'

def categories():
    return list(LESSONS) + ['A4s versus a tight 3-bettor']

def generate(category, seed=None, variant=None, recent_ids=()):
    """Select a reproducible scenario, reducing immediate exact repeats."""
    if category not in categories():
        raise ValueError('Unknown drill category')
    rng = random.Random(seed) if seed is not None else random.SystemRandom()
    for _ in range(15):
        number = rng.randrange(1, 2**31)
        if category == 'A4s versus a tight 3-bettor':
            stage = rng.choice(('Preflop', 'Flop')) if variant is None else ('Preflop' if variant % 2 == 0 else 'Flop')
            item = a4_scenario(number, stage)
        else:
            idx = rng.randrange(len(LESSONS[category])) if variant is None else variant
            item = scenario(number, category, idx)
        if item['id'] not in recent_ids:
            break
    item['source_type'] = SOURCE
    item['source_label'] = 'Qualitative coaching baseline — not solver verified'
    item['concept_id'] = category + ':' + str((idx if category != 'A4s versus a tight 3-bettor' else stage))
    item['difficulty'] = 'Foundation'
    item['cap'] = 800
    return item

def due_date(today, correct, prior_streak):
    """Conservative spacing: incorrect tomorrow; correct 1/3/7/14 days."""
    days = 1 if not correct else (1, 3, 7, 14)[min(max(prior_streak, 0), 3)]
    return (today + timedelta(days=days)).isoformat()

def parse_records(db):
    records=[]
    for row in db.rows('decisions'):
        try: context=json.loads(row.get('context') or '{}')
        except (ValueError, TypeError): continue
        if context.get('course') == 'adaptive_drills':
            records.append(context)
    return records

def summary(records, today=None):
    """Descriptive agreement with baseline, not GTO accuracy or EV."""
    today = today or date.today()
    out={}
    for record in records:
        cat=record.get('category')
        if cat not in categories(): continue
        bucket=out.setdefault(cat, {'attempts':0,'baseline_matches':0,'due':0,'last_due':None})
        bucket['attempts']+=1
        bucket['baseline_matches']+=bool(record.get('matches_baseline'))
        due=record.get('review_due')
        if due:
            bucket['last_due']=due
    for bucket in out.values():
        bucket['due']=int(bool(bucket['last_due'] and bucket['last_due']<=today.isoformat()))
    return out

def pick_category(records, rng=None, today=None):
    rng=rng or random.SystemRandom()
    data=summary(records,today)
    due=[c for c in categories() if data.get(c,{}).get('due')]
    if due: return rng.choice(due)
    unseen=[c for c in categories() if c not in data]
    if unseen: return rng.choice(unseen)
    # Favor under-practiced and lower baseline-agreement categories, not outcomes.
    weights=[]
    for c in categories():
        x=data[c]
        weights.append((1+max(0,x['attempts']-x['baseline_matches']))/(1+x['attempts']))
    return rng.choices(categories(), weights=weights, k=1)[0]

def record_context(drill, action, confidence, history, today=None):
    today=today or date.today()
    previous=[r for r in history if r.get('concept_id')==drill['concept_id']]
    previous_streak=0
    for r in reversed(previous):
        if r.get('matches_baseline'): previous_streak+=1
        else: break
    matched=action==drill['baseline']
    return {'course':'adaptive_drills','category':drill['lesson'],
            'concept_id':drill['concept_id'],'scenario_id':drill['id'],
            'source_type':drill['source_type'],'source_label':drill['source_label'],
            'persona':drill['persona'],'street':drill['street'],
            'action':action,'baseline':drill['baseline'],'matches_baseline':matched,
            'confidence':confidence,'review_due':due_date(today,matched,previous_streak),
            'hypothetical':True}

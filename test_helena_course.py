import sys
from unittest.mock import MagicMock
sys.modules.setdefault("streamlit", MagicMock())
from helena_course import LESSONS, scenario, card_html

def test_eight_lessons_two_situations_each():
    assert len(LESSONS)==8
    assert all(len(v)>=2 for v in LESSONS.values())

def test_randomized_and_alternating_situations():
    for lesson in LESSONS:
        a=scenario(42,lesson,1)
        b=scenario(42,lesson,2)
        assert a['question']!=b['question']
        assert a['baseline'] in a['actions']
        assert b['baseline'] in b['actions']

def test_determinism_and_sanitization():
    a=scenario(42,next(iter(LESSONS)),2)
    assert a==scenario(42,next(iter(LESSONS)),2)
    assert '<script>' not in card_html('<script>')

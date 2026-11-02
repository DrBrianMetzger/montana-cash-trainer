# Helena Cash Course — add-on for Montana Cash Game Trainer v1.4

## Install in GitHub (no terminal required)

1. Open your existing Montana Cash Trainer GitHub repository.
2. Upload `helena_course.py` to the same folder as `app.py`.
3. Replace your existing `app.py` with the provided updated `app.py` **only if you are running the v1.4 `app.py` from our prior package**. If you've made changes since then, merge the three small edits described below instead.
4. Keep `table_ui.py`, `table_experience.py`, `cash_lessons.py`, `training_db.py`, `game_engine.py`, `personas.py`, `pluribus_trainer.py`, and `gto_library.py` as they are. **Do not delete or overwrite them.**
5. Commit changes; refresh the Streamlit app. No new requirements.

## If you prefer to merge into your current app.py

Add this import:

```python
from helena_course import render_helena_course
```

Add `'Helena Cash Course'` to the `sections` list used by sidebar navigation.

Before the Pluribus page branch, add:

```python
elif page == 'Helena Cash Course':
    render_helena_course(db)
```

## Scope and caveats

- Eight lessons with **two distinct base situations each**, alternating to avoid back-to-back duplicate questions within a lesson. Opponent identity and illustrative stack vary across generated hands; not every draw is a fundamentally new strategic spot.
- Graphical felt, hole cards, board, opponent, and action buttons. Action buttons do not reveal a recommended answer before selection.
- Decision records are stored in existing `decisions` table with `source=montana_practice` and `context.course=helena_cash`, compatible with current backup/restore.
- This is a **decision drill**, not a full-hand simulation. No EV calculations, card runouts, pot-rake accounting, or real bankroll statistics are claimed. The more complex cold-deck simulator and leak classification remain later milestones.
- Some example actions are intentionally marginal. Coaching baselines are qualitative and depend on assumptions; they are not GTO frequencies.
- The source spec's A4s/$25 3-bet is represented as a hypothetical version because several historical details are unknown.

## Run tests (optional)

`pytest -q test_helena_course.py`

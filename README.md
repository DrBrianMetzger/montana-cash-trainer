# Montana Cash Game Trainer v1.3 — integrated lesson update

This is a **two-file update** to your **currently deployed v1.2** application, NOT a complete replacement repository.

## Installation (GitHub web interface)
1. Back up your current app using **Download complete backup**.
2. Upload `app.py` and `cash_lessons.py` to the repository root, replacing `app.py`.
3. Keep all other existing modules **unchanged**, especially `table_ui.py`, `training_db.py`, `game_engine.py`, `personas.py`, `pluribus_trainer.py`, and `gto_library.py`.
4. Commit and refresh https://mctpoker.streamlit.app.
5. Choose **Cash Game Lessons** in the left sidebar.

## Included
- New left-nav Cash Game Lessons entry with 10 guided or randomized scenarios: Preflop Discipline, 3-Bet and 4-Bet Pots, Multiway Postflop Play.
- Existing playable `render_table(db)` retained.
- Existing QQ review, legacy test engine, Pluribus, GTO+, profile editor, Leak Finder, and database backup/restore retained.
- Lesson decisions recorded in the shared decisions table with `source=montana_practice` and `context.trainer=cash_lessons_v1.3`.

## Limitations
- Coaching recommendations are qualitative, not solver-verified optimal actions or EV measurements.
- Scenario pot amounts are illustrative; these are **decision drills**, not simulated hand continuations.
- Local SQLite is not durable on Streamlit Community Cloud; export backup regularly.
- The user's current `table_ui.py` was not supplied, so the existing playable table was not independently tested here. The package deliberately does not replace it.

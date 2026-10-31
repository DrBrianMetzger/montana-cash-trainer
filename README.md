# Montana Cash Game Trainer — v1.3 lesson-room add-on

## Why this is an add-on rather than a replacement `app.py`
The current deployed v1.2 beta includes an eight-handed playable table. Its actual source files were **not supplied** in this turn. The only available full application source is the older v1.1 archive. Replacing your current `app.py` with a rebuilt v1.1 file would erase the v1.2 playable table. This release therefore provides a self-contained v1.3 lesson room that can be added to the existing navigation **without replacing the existing engine or modules**.

## Install (GitHub web interface)
1. Back up your current Streamlit data using the application's **Download complete backup** button.
2. Upload `cash_lessons.py` into the repository root (same folder as `app.py`).
3. Edit the **existing v1.2** `app.py` in GitHub. Add this import alongside its other imports:

   `from cash_lessons import render_cash_lessons`

4. Add `'Cash Game Lessons'` to the existing left-sidebar navigation options. Keep every existing option intact.
5. In the existing page-selection `if` / `elif` chain, add a new branch **before** the final `else`:

   ```python
   elif page == 'Cash Game Lessons':
       render_cash_lessons(db)
   ```

   This assumes the v1.2 app retains the v1.1 `db = TrainingDB()` variable. If the database object has been renamed, pass the new variable; alternatively `render_cash_lessons()` runs without database logging (session feedback only).
6. Commit changes and refresh Streamlit.

## What this release does
- Adds three lesson categories: Preflop Discipline, 3-Bet and 4-Bet Pots, Multiway Postflop Play.
- Offers 10 defined study spots, guided or randomized within each category.
- Shows hero hand, position, pot, stack, board, context, and explicit actions.
- Locks a decision before showing action-specific coaching and a transferable takeaway.
- Saves each completed lesson decision into the existing shared SQLite `decisions` table with source `montana_practice` and context tag `trainer=cash_lessons_v1.3`.
- Keeps lesson records distinct from Pluribus prediction and GTO+ solver exercises.
- Works with existing database full-backup JSON; SQLite remains ephemeral on Streamlit Community Cloud.

## Limits
- Scenarios are fixed decision spots, not a dynamically played full hand. Your current v1.2 Practice Table remains the free-play area.
- The coaching is qualitative, not a solver output, estimated EV, or universal optimal strategy.
- Scenario pot figures are approximate gross chip amounts before any rake adjustment; these lessons do not attempt to simulate rake/cap edge cases.
- Opponent Lab's 13×13 range editor and true range-driven opponents are not part of v1.3.
- Full deployment verification requires testing in your actual Streamlit application.

## Tests
Run `python -m pytest tests/test_lessons.py` in an environment with `pytest` and `streamlit` installed. Existing application tests should also be run after merging.

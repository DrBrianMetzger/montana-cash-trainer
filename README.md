# Montana Cash Game Trainer v1.7 — Adaptive Drills

## Installation (GitHub browser, no terminal required)

1. Back up your current GitHub `app.py` first. The included `app.py` is based on the **current code you pasted** and includes the v1.6 Solver Explorer integration. If your GitHub copy has changed, merge the indicated navigation changes rather than replacing it.
2. Upload `drill_engine.py` and `adaptive_drills.py` into the **same repository folder as `app.py`**.
3. Upload the included `app.py` (or merge the changes). It adds **Adaptive Drills** to the sidebar and a **Solver Explorer** tab inside GTO+ Strategy Library.
4. Keep your existing `helena_course.py`, `table_ui.py`, `table_experience.py`, `cash_lessons.py`, `training_db.py`, `gto_library.py`, and all other current modules. The new room reuses `helena_course.visual_table` and your existing `TrainingDB` decision API.
5. **Important:** This `app.py` imports `solver_explorer`. Ensure your v1.6 `solver_explorer.py`, `solver_repository.py`, `solver_import.py`, `solver_models.py`, `range_matrix.py`, and `combo_explorer.py` are all in the repository. If you have not installed v1.6, remove the `solver_explorer` import and its tab branch until you do.
6. Commit; Streamlit Cloud should redeploy automatically. No additional pip requirements are needed for v1.7 beyond your current Streamlit installation.

## What works

- New sidebar room **Adaptive Drills**, with eight Helena topics plus A4s versus a tight three-bettor.
- Randomized question selection, suit permutations and illustrative stack/opponent context, reusing the existing felt visualization and action buttons.
- Source-labelled **qualitative coaching**, never represented as verified solver EV.
- Decisions saved through your existing database; per-concept review dates, confidence and baseline agreement tracked.
- Simple recommended-category selection: due review first, then unseen, then weighted practice. Review intervals of 1/3/7/14 days are *heuristics*, not validated spaced-repetition mastery estimates.

## Limitations and safety of the learning data

- The **16 original strategic templates plus A4s variations** are still the source of drills; this release is not a full legal-action hand generator, GTO solver, or realistic 100-hand simulation. Some suit permutations create visually different questions without materially different strategy.
- Existing Helena template question wording and baseline sizing are preserved rather than dynamically recomputed. Stack labels are illustrative. The source course does not supply a complete betting state, so this release does **not** fabricate legal pot odds, precise EV, or pot-cap bet sizes.
- A baseline disagreement is **not** automatically a poker leak. Actual session results, solver prediction, and heuristic coaching remain distinct.
- Local SQLite on Streamlit Community Cloud can be ephemeral. Export the existing complete backup frequently.

## Developer tests

`python -m pytest test_adaptive_drills.py -q`

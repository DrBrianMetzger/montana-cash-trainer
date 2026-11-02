# Montana Cash Game Trainer v1.6 — Solver Intelligence (Phase 1 + Phase 2 MVP)

## What is included

- `solver_models.py`: 169 starting-hand classes, exact combos, blockers, Montana compatibility warning
- `solver_import.py`: strict versioned JSON validation
- `solver_repository.py`: independent SQLite storage, import/export backups
- `range_matrix.py`: 13×13 action-frequency display and combo-weighted class summaries
- `combo_explorer.py`: exact combo frequency, weight, optional equity and action EV
- `solver_explorer.py`: Streamlit UI for importing and exploring stored solutions
- `app.py`: reference integration into the existing **GTO+ Strategy Library** section
- `tests/`: synthetic fixture and automated tests (not real solver output)

## Install (minimal and safe)

1. **Back up your current GitHub `app.py`** before changing it. The provided `app.py` is based on the latest source available in this conversation (`helena-course-build/app.py`), not a verified live GitHub checkout. If your deployed `app.py` differs, merge the three small integration edits below instead of overwriting it.
2. Upload these six new files into the repository root: `solver_models.py`, `solver_import.py`, `solver_repository.py`, `range_matrix.py`, `combo_explorer.py`, `solver_explorer.py`.
3. In your current `app.py`, add the import:
   `from solver_explorer import render_solver_explorer`
4. Replace only the `elif page=='GTO+ Strategy Library':` block with:

```python
elif page=='GTO+ Strategy Library':
    library_tab, solver_tab = st.tabs(['Screenshot Library', 'Solver Explorer'])
    with library_tab:
        render_gto_library()
        for item in st.session_state[GTO_KEY]:
            db.save_reference(item)
        st.caption('Screenshot references are stored separately from imported structured solver data.')
    with solver_tab:
        render_solver_explorer()
```

5. Commit. Open GTO+ Strategy Library > Solver Explorer. Your existing Streamlit dependency is sufficient; do **not** replace a more complete `requirements.txt` with the minimal example in this package.
6. Download solver-library backups regularly. Local SQLite on Streamlit Community Cloud is ephemeral.

## Supported import format

The importer accepts **only** `mct.solver.v1` structured JSON. It does not decode native GTO+ `.gto2` files. The existing `.gto2` project files supplied in this conversation were not reverse engineered or imported. The fixture `tests/synthetic_fixture.json` documents the schema but is **synthetic**, not solver data, and the UI rejects its import.

For real solutions, obtain a documented structured export or transcribe independently verified exact-combination values with full assumptions and source provenance into this schema. The `source.verification` value is user-supplied provenance, not cryptographic or third-party authentication. All percentages are in 0–100 units; equity is in 0–1 units; EV is in BB; range weights are in 0–1 units.

The matrix is a readable MVP, not yet a segmented frequency heatmap. It shows the most frequent action in each populated hand class. Exact combinations appear in a table below. Tree navigation is limited to listing stored child IDs. Guess the Solver, filters, editable opponent comparisons, and Montana-specific solving are future phases.

## Testing

From the project directory: `python -m unittest discover -s tests -v`

Eight tests passed in the packaged source. This package has not been deployed or end-to-end tested against your current live repository.

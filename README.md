# Montana Cash Game Trainer — Version 1.1

Unified Streamlit application with six navigation destinations. The Montana practice foundation, historical Pluribus prediction module, and screenshot-backed GTO+ library remain distinct.

## Deploy on Streamlit Community Cloud

1. Open your `montana-cash-trainer` GitHub repository.
2. Upload **all root-level `.py` files** and `requirements.txt` from this package, replacing files with matching names. Keep `tests/` and this README in the repository as well.
3. In Streamlit Community Cloud, set the main file to `app.py`. Redeploy or reboot the app.
4. Open each navigation section. Export a **complete backup** using the sidebar before and after entering new data.

## Storage and backup

SQLite (`trainer.sqlite3`) is a **local working database**, not durable cloud storage. Streamlit Community Cloud can erase it on restart/redeploy, and concurrent replicas are not coordinated. Session state also disappears. Download the **complete backup JSON** from the sidebar; restore it using the adjacent uploader. GTO+ screenshots are embedded in the backup as base64, so backups can be large. Existing GTO+ library JSON export/restore remains available in its own tab.

The original GTO+ and Pluribus modules are preserved, with a database synchronization adapter in `app.py`. Existing session-only data from an earlier deployed version must be exported there before replacement; this release cannot recover deleted Streamlit session data.

## Scope and limitations

- **Montana practice:** preserves the original QQ hand as historical review. The separate heads-up engine supports fold, call, check, bet, raise and selected opponent responses. It is **not** yet a six-player Montana simulation, does not deal community cards, does not determine showdown winners, and does not apply rake. The engine refuses a wager that would bring the gross pot to or above $800 until house procedures are clarified. The $800 cap includes rake, and no maximum buy-in is assumed.
- **Pluribus:** preserves the original prediction workflow, GitHub hand fetch, and accuracy by street. Predictions are mirrored into SQLite. This version does **not** claim reconstructed legal actions, positions, effective stacks or pot sizes; those remain a future parsing task, rather than presenting unverified values.
- **GTO+:** screenshot uploads, exact frequencies, optional verified action EV, practice, notes and original JSON backup/restore remain. References and screenshots are mirrored to SQLite. Individual GTO practice clicks are **not yet logged** to the shared decision table; frequencies are not treated as EV loss.
- **Opponent Lab:** editable, uncalibrated text ranges and tendencies for four personas. No autonomous strategies or 13×13 editor yet.
- **Leak Finder:** separate source counts only; no unverified leak diagnoses.

## Test locally

`python -m pytest -q`

## Open questions before implementing Montana cap handling

If a wager would exceed the $800 gross pot cap: is it reduced to the maximum legal amount, disallowed entirely, or handled differently? Does the house count rake already taken when checking the cap? How are unmatched chips returned, and what happens if a call reaches the cap? Until clarified, the engine **rejects** such wagers rather than inventing house rules.

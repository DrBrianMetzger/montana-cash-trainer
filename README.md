# Montana Cash Game Trainer — Version 1.2 beta

This release extends the deployed v1.1 app without replacing its Pluribus and GTO+ modules.

## New: experimental multiway practice
- 4–9 seats; default 8.
- Optional **Add House Shill** checkbox, occupying an existing seat. The shill is a dealer out of the box, with $200 house-funded buy-in, blinds, conservative heuristics, and automatic $200 rebuy when broke. House funding and rake are displayed separately.
- Hole cards, board cards, rotating button/blinds, betting streets, fold/call/check/bet/raise, recorded hero decisions, high-hand evaluation, simple side-pot settlement, and 10% rake capped at $6.
- Announced wagers and effective wagers are displayed separately. Gross pot is capped at $800, including rake.

**Beta limitations:** Multiway betting, partial all-ins, uncalled bet returns, cap allocation, and legal raise reopening are simplified. Do not use this as an authoritative Montana casino payout calculator. Opponent decisions are deliberately basic heuristics, not solver-based or calibrated; opponent tendencies entered in Opponent Lab do not yet drive the table. This is not yet the promised graphical 13×13 range editor. The house shill's displayed net is the simulated stack minus cumulative house funding, not a business profit-and-loss statement.

## Preserved
- Historical QQ review and original heads-up engine (legacy testing).
- Pluribus Prediction Trainer, hand imports, accuracy and database mirror.
- GTO+ screenshot library, reference uploads, exact practice, JSON backup and restore.
- SQLite database, separate decision sources, Opponent Lab text profile editor, Leak Finder foundation.

## Deploy from GitHub browser
1. Export a full database backup and GTO+ library JSON from your currently running app. Local Streamlit Community Cloud SQLite is **not durable**.
2. Download and extract the release ZIP.
3. In the GitHub repository root, upload all files from inside `montana-v1_2` (including `table_engine.py` and `table_ui.py`), replacing the existing `app.py`, `personas.py`, and other files. Do not nest the directory in the repo.
4. Commit changes to the branch used by Streamlit Community Cloud. Its main file remains `app.py`.
5. Open your app, use the Montana Practice Table, set eight seats and check Add House Shill, then click Start / reset table.
6. After a redeploy, restore your full database backup if necessary. The original GTO+ library also supports its own JSON restore.

## Local automated checks
`python -m pytest -q` (pytest included in requirements).

## Next milestone
Graphical 13×13 range editor, configurable preflop/3-bet ranges wired to opponent actions, improved live pot-cap semantics and realistic multiway action order.

# Montana Cash Game Trainer — v1.0 demonstration

An original Streamlit poker training prototype. **This is a scripted educational demonstration, not a poker solver or a fully validated Montana betting engine.**

## Run locally

Install Python 3.10+ and run:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The SQLite database `trainer.sqlite3` is created on first launch. Each submitted decision is saved locally. The displayed future actions and pots remain scripted even when the user chooses a different line. Four personas are selectable labels only, not functional AI opponents.

## GitHub and Streamlit Community Cloud

1. Create a new GitHub repository and upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore`.
2. In Streamlit Community Cloud, create an app connected to that repository and select `app.py` as the entry point.
3. **Persistence caveat:** SQLite files on Community Cloud may be lost on redeployment/restart. Use external persistent storage before relying on saved progress in a hosted application.

## Known limitations

- Montana's $800 total-pot cap, rake, promotional drops, and pot-limit enforcement are not yet implemented.
- No live betting validation, side pots, random dealing, hand evaluator, equity calculation, or GTO solver.
- Hero's choices do not change the pre-scripted next state.
- Turn bet and raise amounts are unknown; no exact pot odds are claimed.
- The scripted flop pot assumes a $66 total after three players contribute $22 each, ignoring rake and blinds bookkeeping detail. The scripted turn pot assumes three $20 flop contributions.

## Next milestone

Confirm local betting procedures, then implement a separately tested legal-action and $800-cap engine before enabling dynamic hands.

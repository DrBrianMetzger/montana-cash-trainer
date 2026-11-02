# Helena Cash Game Course — incremental update

This package updates the **Helena Cash Course** within Montana Cash Game Trainer. It preserves the existing left navigation and the `render_table(db)` integration. This is a scenario drill, not a replacement for the multiway poker engine.

## Install (GitHub web interface)

1. Download and extract this ZIP.
2. Open your existing Montana Cash Trainer GitHub repository.
3. Upload `helena_course.py` in the same folder as `app.py`, replacing the old version.
4. Your existing app.py **already has** the `Helena Cash Course` navigation item and `from helena_course import render_helena_course`. If that is what is deployed, **do not replace app.py**. A compatible reference copy is included only for comparison.
5. Keep `table_ui.py`, `training_db.py`, `personas.py`, `pluribus_trainer.py`, `gto_library.py`, and the other working modules unchanged.
6. Commit and refresh https://mctpoker.streamlit.app/.

If your app.py does NOT already have the course, add:

```python
from helena_course import render_helena_course
```

Add `'Helena Cash Course'` to the sidebar `sections` list, then before the Pluribus branch:

```python
elif page == 'Helena Cash Course':
    render_helena_course(db)
```

## Changes

- Eight existing lessons, with two base situations each.
- More varied visual card presentation through reproducible, consistent suit permutations, plus randomized modeled opponent labels and stack context. The same underlying strategic spot may recur; it is not an unlimited hand generator.
- Featured **A4s versus tight 3-bettor** lesson with alternating preflop and flop decisions, and explicitly hypothetical position, effective stack, bet sizing and action history.
- A4s pot calculations assume $1/$2 blinds, $8 open, $25 three-bet, blinds folding and no other contributions. Flop bets are either $18 or $53 into a $53 gross pot. Rake is part of gross pot, but actual rake-set-aside accounting is not simulated in these drills.
- Visual table, large action buttons, optional gross pot and $800-cap remaining display, and decision explanations.
- Course practice history grouped by lesson; matches to illustrative coaching baseline are **not EV scores** or proof of leaks.
- Existing decision records are saved to the `decisions` table with `context.course='helena_cash'`.

## Scope

This increment does **not** implement the 30–100 hand cold-deck simulator, full betting engine, accurate session bankroll/rake/tip accounting, statistical leak detection, or verified solver EV. These require more complete engine integration and should not be simulated using invented hand outcomes.

## Tests

`pytest -q test_helena_course.py` (five tests passed during package creation).

No new Python dependencies beyond those already used by your app.

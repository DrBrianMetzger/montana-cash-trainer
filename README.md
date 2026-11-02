# Montana visual table_ui.py (standalone fallback)

Upload `table_ui.py` beside `app.py` in your GitHub repository. It satisfies `from table_ui import render_table` and displays an eight-seat graphical poker table with four interactive decision drills.

**Important:** This is a *visual scenario trainer*, not the original Version 1.2 multiway game engine. It does not play complete hands, perform betting-round transitions, adjudicate all-ins/side pots, or automatically grade decisions. Do not overwrite an existing working `table_ui.py` without backing it up. If the live application already displays the playable Version 1.2 table, your repository almost certainly contains an existing `table_ui.py` that should be retained and upgraded instead.

No additional packages or changes to `app.py` are required. The function signature is `render_table(db)`.

1) High-level (10–15s)
- Introduce the pain point: screenshots pile up with no context.
- Goal: auto-triage screenshots into actionable, searchable notes.

2) Show setup (30s)
- Show `config.yaml` defaults and `.env` with `OPENAI_API_KEY`.
- In terminal: activate venv, `pip install -r requirements.txt`.

3) Run watcher (30s)
- `python -m src.main watch ~/Desktop`.
- Point it at the folder where your screenshots are saved (e.g., `~/Desktop` on macOS). Then take a screenshot.

4) See results (1–2 min)
- Terminal logs show detection and analysis.
- In Finder: image renamed in place to a slugified title (collision-safe). A hidden sidecar `.FILENAME.triaged` is created.
- Open the generated markdown note saved next to the image: show summary, tags, and task checklist.

5) Walkthrough (1–2 min)
- Explain pipeline: detect → analyze → organize → document.
- Briefly show `src/analyzer.py` prompt and JSON schema.
- Show `src/main.py` commands (watch with folder arg, analyze single file).


6) Wrap-up (15–20s)
- Time saved and reduced friction.
- Future: routing rules and task manager integration.





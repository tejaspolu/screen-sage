## ScreenSage

This agent watches the folder where your screenshots are saved (e.g., `~/Desktop`) for new screenshots, uses an AI vision model to summarize and extract tasks/tags, then renames the image and creates a linked markdown note. It eliminates the manual chore of sorting and remembering why you captured a screenshot.

### Features
- Auto-detect new screenshots in a specified folder
- Vision + LLM analysis to produce structured JSON (title, summary, tasks, tags, sensitivity)
- Intelligent rename in place with collision-safe unique names
- Hidden sidecar marker file to prevent double-processing
- Create a rich markdown note (saved next to the image) with the image reference, metadata, and checklist tasks
- CLI for one-off processing and a watcher for continuous background use

### Quick Start

1) Clone and set up the project

```bash
git clone <your-fork-or-repo-url> screensage
cd screensage
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Set environment variables

If `.env.example` exists, copy it; otherwise create `.env` with the keys below:

```bash
echo "OPENAI_API_KEY=\nVISION_MODEL=gpt-4o" > .env
```

Required:
- `OPENAI_API_KEY`: your OpenAI API key

Optional:
- `VISION_MODEL` (default: `gpt-4o`)

4) Configure (optional)

Edit `config.yaml` to change defaults like `watch_dir` and `vision_model` if you prefer.

5) Run the watcher (enter the folder where your screenshots go)

```bash
python -m src.main watch ~/Desktop
```

Or process a single image:

```bash
python -m src.main analyze /path/to/screenshot.png
```

### What happens when a screenshot appears
1. The watcher detects a new image in the specified folder
2. The analyzer sends a base64 version to the vision model with strong JSON instructions
3. The response is validated and normalized
4. The file is renamed in place (slugified title; collision-safe suffix) and a hidden sidecar `.FILENAME.triaged` is written
5. A markdown note is created alongside the image with a link to it and a task checklist

### Configuration
See `config.yaml` for defaults and `src/config.py` for loading order:
1. Defaults in `config.yaml`
2. Environment variables via `.env`

### Safety & Privacy
### macOS Permissions
- If nothing happens when you take a screenshot, grant Terminal/VS Code Full Disk Access and Files and Folders permissions (System Settings → Privacy & Security).
- Ensure the app has access to the folder you are watching. Restart the watcher after changing permissions.

- A `sensitivity` flag is included in the analysis result; if `true`, the note is marked accordingly.
- Images are not uploaded anywhere except to the configured AI provider.



### Uninstall / Stop
- To stop the watcher, Ctrl+C the terminal running `python -m src.main watch`.
- If you accidentally started multiple background watchers, you can stop them with:

```bash
pkill -f "src.main watch" || true
```

### License
MIT



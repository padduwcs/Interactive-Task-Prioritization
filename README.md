# First Things First

A desktop app for prioritizing tasks through pairwise comparison. Add tasks, compare them two at a time, and get a sorted priority list that can be edited, reordered, copied, marked done, and restored on the next launch.

Built with Python and PyQt6.

## Highlights

| Area | Support |
| --- | --- |
| Task writing | Multi-line Markdown input with rendered preview |
| Sorting | Interactive merge sort with O(n log n) comparisons |
| Results | Edit, copy, add, reorder, and mark tasks done |
| Layout | Light/dark themes, responsive cards, long-content scrolling |
| Persistence | Sorted result and done states are saved locally |
| Packaging | PyInstaller Windows build via `First Things First.spec` |

## Markdown Workflow

Task fields show Markdown source while you are editing. After the field loses focus, the app renders the task as formatted text. Clicking into the field again switches back to Markdown source for editing.

Markdown rendering is used in:

- Input task cards after editing
- Pairwise comparison cards
- Sorted result cards

The stored task text remains Markdown source, so editing, saving, and copying keep the original formatting syntax.

## Requirements

- Python 3.10 or newer
- PyQt6
- PyInstaller, only when building the Windows app

Runtime dependencies are listed in `requirements.txt`.

## Setup

```bash
git clone https://github.com/padduwcs/Interactive-Task-Prioritization.git
cd Interactive-Task-Prioritization
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

With conda:

```bash
conda create -n first-things-first python=3.12
conda activate first-things-first
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

In this workspace, the maintained local environment is:

```powershell
conda activate deskApp
python main.py
```

## Controls

| View | Action |
| --- | --- |
| Input | `Ctrl+N` adds a task |
| Input | `Ctrl+Enter` starts sorting |
| Comparison | Left/right arrows focus a task |
| Comparison | `Enter` selects the focused task |
| Result | Drag tasks to reorder |
| Result | `Add Task`, `Edit`, `Copy`, `Copy All`, and `Restart` manage the list |
| Global | `F1` or `?` opens keyboard help |
| Global | `Dark` / `Light` toggles the theme |

## Saved State

Sorted results and checkbox states are saved automatically.

Default state location:

- Windows: `%APPDATA%\First Things First\task_state.json`
- macOS/Linux: `~/.first-things-first/task_state.json`

## Tests

```bash
python -m unittest discover -s tests -p "*_tests.py"
```

For headless environments:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python -m unittest discover -s tests -p "*_tests.py"
```

The theme palette can also be reviewed from the terminal:

```bash
python preview_themes.py
python preview_themes.py --theme dark
python preview_themes.py --no-color
```

## Build Windows App

Install PyInstaller if needed:

```bash
python -m pip install pyinstaller
```

Build:

```bash
pyinstaller -y "First Things First.spec"
```

Using the local conda environment:

```powershell
conda run -n deskApp python -m PyInstaller -y "First Things First.spec"
```

Output:

```text
dist/First Things First/First Things First.exe
```

Pin `First Things First.exe` to the taskbar after launching it once.

## Project Structure

```text
.
|-- main.py                     # App controller and entry point
|-- ui_components.py            # PyQt6 widgets, styling, Markdown rendering
|-- sorter_logic.py             # Interactive merge sort generator
|-- state_store.py              # Local persistence
|-- theme_design.py             # Light/dark palette tokens and contrast checks
|-- preview_themes.py           # Terminal theme preview
|-- First Things First.spec     # PyInstaller build configuration
|-- app_icon.ico                # Windows app icon
|-- requirements.txt            # Runtime dependencies
|-- tests/                      # Unit tests
`-- README.md                   # Project documentation
```

## Repository Hygiene

Ignored local artifacts include:

- `build/`
- `dist/`
- `__pycache__/`
- `.venv/`
- `tests/.tmp_state/`

Only source, tests, app metadata, and documentation are tracked.

## License

MIT

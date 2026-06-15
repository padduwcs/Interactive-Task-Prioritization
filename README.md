# First Things First

A desktop app for prioritizing tasks through an interactive merge sort workflow. Add your tasks, compare them two at a time, and get a sorted priority list that can be edited, reordered, copied, and marked as done.

Built with Python and PyQt6.

## Features

- Multi-line task input with optional descriptions
- Interactive merge sort with O(n log n) comparison complexity
- Keyboard navigation for sorting and comparison
- Progress indicator while sorting
- Persistent sorted results between app launches
- Completion checkboxes with visual done states
- Copy, edit, reorder, and add tasks directly in the result list
- Copy the full prioritized list as numbered text
- Help dialog with keyboard shortcuts

## Requirements

- Python 3.10 or newer
- pip

Runtime Python dependencies are listed in `requirements.txt`.

## Setup

Clone the repository:

```bash
git clone https://github.com/padduwcs/Interactive-Task-Prioritization.git
cd Interactive-Task-Prioritization
```

Create and activate a Python environment. Any standard Python environment manager works.

Using `venv`:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Or using conda:

```bash
conda create -n first-things-first python=3.12
conda activate first-things-first
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

If you are using conda, activate the environment first, then run the same command.

## Keyboard Shortcuts

Input view:

- `Ctrl+N`: Add a new task
- `Ctrl+Enter`: Start sorting

Comparison view:

- `Left Arrow`: Focus the left task
- `Right Arrow`: Focus the right task
- `Enter`: Select the focused task

Result view:

- Drag tasks to manually reorder the sorted list
- Click a checkbox to mark a task as done
- Use `Copy` to copy one task
- Use `Edit` to update one task
- Use `Copy All` to copy the full numbered list
- Use `Add Task` to append a task after sorting
- Use `Restart` to clear the saved result and start over

Global:

- `F1`: Show keyboard shortcut help
- `?` button: Show keyboard shortcut help

## Saved State

Sorted results and checkbox states are saved automatically. On the next launch, the app opens the saved result list.

Default state location:

- Windows: `%APPDATA%\First Things First\task_state.json`
- macOS/Linux: `~/.first-things-first/task_state.json`

## Tests

Run the unit tests:

```bash
python -m unittest discover -s tests -p "*_tests.py"
```

For headless environments, set Qt to offscreen mode before running tests.

Windows PowerShell:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
python -m unittest discover -s tests -p "*_tests.py"
```

macOS/Linux:

```bash
QT_QPA_PLATFORM=offscreen python -m unittest discover -s tests -p "*_tests.py"
```

## Build Windows Executable

Building an executable is optional and requires PyInstaller:

```bash
python -m pip install pyinstaller
pyinstaller "First Things First.spec"
```

The executable is generated at:

```text
dist/First Things First/First Things First.exe
```

## Project Structure

```text
.
|-- main.py                   # Application entry point and logic controller
|-- ui_components.py          # PyQt6 UI components and widgets
|-- sorter_logic.py           # Interactive merge sort generator algorithm
|-- state_store.py            # Local persistence for sorted results
|-- First Things First.spec   # PyInstaller Windows build configuration
|-- requirements.txt          # Runtime Python dependencies
|-- tests/                    # Unit tests
`-- README.md                 # Project documentation
```

## Algorithm

The app uses an interactive merge sort algorithm that:

- Yields comparison pairs to the user interface
- Receives user choices through `generator.send()`
- Minimizes comparisons with O(n log n) complexity
- Keeps the UI responsive through generator-based control flow

## License

MIT

# Interactive Task Prioritization

A modern desktop application for prioritizing tasks using an interactive merge sort algorithm. Built with Python and PyQt6.

## Features

- **Multi-line Task Input**: Add tasks with descriptions directly in the GUI
- **Interactive Merge Sort**: Algorithmically efficient O(n log n) sorting with user comparisons
- **Keyboard Shortcuts**: Full keyboard navigation for sorting and comparison
- **Visual Feedback**: 
  - Green highlight for completed tasks
  - Strikethrough text for done items
  - Progress indicator during sorting
- **Independent Completion Tracking**: Mark any result task as done in any order
- **Persistent Results**: Keep the sorted list and completion state between app launches
- **Result Actions**: Copy one task, edit task details, or copy the full prioritized list
- **Auto-scroll**: Smooth scrolling for long task lists
- **Help Dialog**: Compact help button and keyboard shortcut reference

## Installation

### Requirements
- Python 3.10+
- PyQt6

### Setup

1. Clone the repository:
```bash
git clone https://github.com/padduwcs/Interactive-Task-Prioritization.git
cd "First Things First"
```

2. Create a conda environment (recommended):
```bash
conda create -n deskApp python=3.12
conda activate deskApp
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

Or if using conda:
```bash
conda run -n deskApp python main.py
```

## Keyboard Shortcuts

### Input View
- **Ctrl+N**: Add new task
- **Ctrl+Enter**: Start sorting

### Comparison View
- **Left Arrow**: Focus left button
- **Right Arrow**: Focus right button
- **Enter**: Select focused task

### Result View
- **Click checkbox**: Mark task as done (green highlight)
- **Copy**: Copy one task
- **Edit**: Update one task's content/details
- **Copy All**: Copy every task as a numbered list
- **Restart button**: Go back to input view

Sorted results and checkbox states are saved automatically. The next app launch opens the saved result list. Use **Restart** to clear the saved state and start over.

### Global
- **F1**: Show keyboard shortcuts help
- **? button**: Show keyboard shortcuts help

## Tests

Run the unit tests:
```bash
python -m unittest discover -s tests -p "*_tests.py"
```

## Build Windows App

Build the desktop app executable with the bundled icon:
```bash
pyinstaller "First Things First.spec"
```

The executable is generated at:
```text
dist/First Things First/First Things First.exe
```

## Project Structure

```
.
├── main.py              # Application entry point and logic controller
├── ui_components.py     # PyQt6 UI components and widgets
├── sorter_logic.py      # Interactive merge sort generator algorithm
├── First Things First.spec # PyInstaller Windows build configuration
├── requirements.txt     # Runtime Python dependencies
├── tests/               # Unit tests for core logic
└── README.md            # This file
```

## Algorithm

The application uses an **Interactive Merge Sort** algorithm that:
- Yields comparison pairs to the user interface
- Receives user choices via generator.send()
- Minimizes comparisons with O(n log n) complexity
- Maintains non-blocking UI through generator-based control flow

## Technical Highlights

- **Generator-based sorting**: Non-blocking UI with coroutine pattern
- **Modern PyQt6 UI**: Responsive, accessible interface with custom widgets
- **Professional code structure**: Separation of concerns with dedicated modules

## License

MIT

## Author

Developer

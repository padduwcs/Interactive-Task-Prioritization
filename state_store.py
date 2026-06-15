"""Local persistence for the task prioritization application."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable


STATE_VERSION = 1
APP_DIR_NAME = 'First Things First'
STATE_FILE_NAME = 'task_state.json'


def default_state_path() -> Path:
    appdata = os.getenv('APPDATA')
    if appdata:
        base_dir = Path(appdata) / APP_DIR_NAME
    else:
        base_dir = Path.home() / f'.{APP_DIR_NAME.lower().replace(" ", "-")}'

    return base_dir / STATE_FILE_NAME


class TaskStateStore:
    def __init__(self, path: Path | str | None = None):
        self.path = Path(path) if path is not None else default_state_path()

    def load(self) -> dict | None:
        try:
            with self.path.open('r', encoding='utf-8') as state_file:
                data = json.load(state_file)
        except (FileNotFoundError, OSError, json.JSONDecodeError):
            return None

        return self._normalize_state(data)

    def save_result(self, sorted_tasks: Iterable[tuple[int, str]], done_states: Iterable[bool] | None = None) -> bool:
        done_list = list(done_states) if done_states is not None else []
        task_items = []

        for index, task in enumerate(sorted_tasks):
            task_items.append(
                {
                    'text': task[1],
                    'done': bool(done_list[index]) if index < len(done_list) else False,
                }
            )

        state = {
            'version': STATE_VERSION,
            'view': 'result',
            'sorted_tasks': task_items,
        }

        return self._save_state(state)

    def delete(self) -> bool:
        try:
            self.path.unlink()
        except FileNotFoundError:
            return True
        except OSError:
            return self._save_state({'version': STATE_VERSION, 'view': 'result', 'sorted_tasks': []})

        return True

    def _save_state(self, state: dict) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.path.with_suffix(f'{self.path.suffix}.tmp')
            with tmp_path.open('w', encoding='utf-8') as state_file:
                self._write_state_data(state_file, state)
            try:
                tmp_path.replace(self.path)
            except OSError:
                with self.path.open('w', encoding='utf-8') as state_file:
                    self._write_state_data(state_file, state)
                try:
                    tmp_path.unlink(missing_ok=True)
                except OSError:
                    pass
        except OSError:
            return False

        return True

    def _normalize_state(self, data) -> dict | None:
        if not isinstance(data, dict):
            return None
        if data.get('version') != STATE_VERSION or data.get('view') != 'result':
            return None

        sorted_tasks = data.get('sorted_tasks')
        if not isinstance(sorted_tasks, list):
            return None

        normalized_tasks = []
        for item in sorted_tasks:
            if not isinstance(item, dict) or not isinstance(item.get('text'), str):
                return None
            normalized_tasks.append({'text': item['text'], 'done': bool(item.get('done', False))})

        return {
            'version': STATE_VERSION,
            'view': 'result',
            'sorted_tasks': normalized_tasks,
        }

    def _write_state_data(self, state_file, state: dict):
        json.dump(state, state_file, ensure_ascii=False, indent=2)
        state_file.write('\n')

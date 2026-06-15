import sys
from pathlib import Path
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from sorter_logic import interactive_merge_sort, estimate_merge_sort_comparisons
from state_store import TaskStateStore
from ui_components import TaskSorterWindow


def resource_path(relative_path: str) -> Path:
    base_path = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))
    return base_path / relative_path


def load_app_icon() -> QIcon:
    icon_path = resource_path('app_icon.ico')
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


class TaskSorterApp:
    def __init__(self, app_icon: QIcon | None = None, state_store: TaskStateStore | None = None):
        self.window = TaskSorterWindow()
        if app_icon is not None and not app_icon.isNull():
            self.window.setWindowIcon(app_icon)
        self.state_store = state_store or TaskStateStore()
        self.sort_generator = None
        self.current_step = 0
        self.estimated_steps = 0
        self.result_tasks = []
        self.result_done_states = []
        self._connect_signals()
        self._restore_saved_state()

    def _connect_signals(self):
        self.window.add_task_button.clicked.connect(self.window.add_task_input)
        self.window.start_button.clicked.connect(self._on_start_sort)
        self.window.restart_button.clicked.connect(self._on_restart)
        self.window.button_a.clicked.connect(lambda: self._on_task_chosen(self.window.button_a.task))
        self.window.button_b.clicked.connect(lambda: self._on_task_chosen(self.window.button_b.task))
        self.window.result_completion_changed.connect(self._on_result_completion_changed)
        self.window.result_text_changed.connect(self._on_result_text_changed)
        self.window.result_order_changed.connect(self._on_result_order_changed)
        self.window.result_task_added.connect(self._on_result_task_added)

    def _on_start_sort(self):
        tasks = self.window.gather_tasks()

        if not tasks:
            self.window.set_input_hint('Please add at least one task before sorting.')
            return

        self.task_items = tasks
        self.current_step = 0
        self.estimated_steps = estimate_merge_sort_comparisons(len(self.task_items))

        if self.estimated_steps == 0:
            self.sort_generator = None
            self._show_result(self.task_items)
            return

        self.sort_generator = interactive_merge_sort(self.task_items)
        self.window.show_comparison_view()
        self._advance_sorter()

    def _advance_sorter(self, chosen_task=None):
        try:
            if chosen_task is None:
                pair = next(self.sort_generator)
            else:
                pair = self.sort_generator.send(chosen_task)

            self.current_step += 1
            self.window.update_progress(self.current_step, self.estimated_steps)
            self.window.update_comparison_pair(*pair)

        except StopIteration as stop:
            sorted_tasks = stop.value
            self._show_result(sorted_tasks)

    def _on_task_chosen(self, chosen_task):
        if self.sort_generator is None:
            return
        self._advance_sorter(chosen_task)

    def _on_restart(self):
        self.sort_generator = None
        self.current_step = 0
        self.estimated_steps = 0
        self.result_tasks = []
        self.result_done_states = []
        self.state_store.delete()
        self.window.reset()

    def _on_result_completion_changed(self, index: int, is_done: bool):
        if index < 0 or index >= len(self.result_done_states):
            return

        self.result_done_states[index] = is_done
        self.state_store.save_result(self.result_tasks, self.result_done_states)

    def _on_result_text_changed(self, index: int, task_text: str):
        if index < 0 or index >= len(self.result_tasks):
            return

        original_index = self.result_tasks[index][0]
        self.result_tasks[index] = (original_index, task_text)
        self.state_store.save_result(self.result_tasks, self.result_done_states)

    def _on_result_order_changed(self, tasks: list[tuple[int, str]], done_states: list[bool]):
        self.result_tasks = list(tasks)
        self.result_done_states = list(done_states)
        self.state_store.save_result(self.result_tasks, self.result_done_states)

    def _on_result_task_added(self, task_text: str):
        next_task_id = max((task[0] for task in self.result_tasks), default=-1) + 1
        self.result_tasks.append((next_task_id, task_text))
        self.result_done_states.append(False)
        self.window.show_result_view(self.result_tasks, self.result_done_states)
        self.state_store.save_result(self.result_tasks, self.result_done_states)

    def _show_result(self, sorted_tasks: list[tuple[int, str]], done_states: list[bool] | None = None, persist: bool = True):
        self.result_tasks = list(sorted_tasks)
        self.result_done_states = (
            list(done_states)
            if done_states is not None
            else [False for _ in self.result_tasks]
        )
        self.window.show_result_view(self.result_tasks, self.result_done_states)

        if persist:
            self.state_store.save_result(self.result_tasks, self.result_done_states)

    def _restore_saved_state(self):
        state = self.state_store.load()
        if not state:
            return

        saved_tasks = state.get('sorted_tasks', [])
        if not saved_tasks:
            return

        sorted_tasks = [(index, item['text']) for index, item in enumerate(saved_tasks)]
        done_states = [bool(item.get('done', False)) for item in saved_tasks]
        self._show_result(sorted_tasks, done_states, persist=False)

    def run(self):
        self.window.show()


def main():
    app = QApplication(sys.argv)
    app_icon = load_app_icon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)
    sorter_app = TaskSorterApp(app_icon)
    sorter_app.run()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

import sys
from PyQt6.QtWidgets import QApplication

from sorter_logic import interactive_merge_sort, estimate_merge_sort_comparisons
from ui_components import TaskSorterWindow


class TaskSorterApp:
    def __init__(self):
        self.window = TaskSorterWindow()
        self.sort_generator = None
        self.current_step = 0
        self.estimated_steps = 0
        self._connect_signals()

    def _connect_signals(self):
        self.window.add_task_button.clicked.connect(self.window.add_task_input)
        self.window.start_button.clicked.connect(self._on_start_sort)
        self.window.restart_button.clicked.connect(self._on_restart)
        self.window.button_a.clicked.connect(lambda: self._on_task_chosen(self.window.button_a.task))
        self.window.button_b.clicked.connect(lambda: self._on_task_chosen(self.window.button_b.task))

    def _on_start_sort(self):
        tasks = self.window.gather_tasks()

        if not tasks:
            self.window.set_input_hint('Please add at least one task before sorting.')
            return

        self.task_items = tasks
        self.sort_generator = interactive_merge_sort(self.task_items)
        self.current_step = 0
        self.estimated_steps = estimate_merge_sort_comparisons(len(self.task_items))

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
            self.window.show_result_view(sorted_tasks)

    def _on_task_chosen(self, chosen_task):
        if self.sort_generator is None:
            return
        self._advance_sorter(chosen_task)

    def _on_restart(self):
        self.sort_generator = None
        self.current_step = 0
        self.estimated_steps = 0
        self.window.reset()

    def run(self):
        self.window.show()


def main():
    app = QApplication(sys.argv)
    sorter_app = TaskSorterApp()
    sorter_app.run()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

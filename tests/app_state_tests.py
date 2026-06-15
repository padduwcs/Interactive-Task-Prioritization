import os
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt6.QtWidgets import QApplication

from main import TaskSorterApp


def get_app():
    return QApplication.instance() or QApplication([])


class FakeStateStore:
    def __init__(self):
        self.saved = []

    def load(self):
        return None

    def save_result(self, sorted_tasks, done_states=None):
        self.saved.append((list(sorted_tasks), list(done_states or [])))
        return True

    def delete(self):
        return True


class TaskSorterAppStateTests(unittest.TestCase):
    def setUp(self):
        self.app = get_app()

    def test_editing_result_text_updates_saved_state(self):
        store = FakeStateStore()
        sorter_app = TaskSorterApp(state_store=store)

        sorter_app._show_result([(0, 'Original task')], [False])
        sorter_app._on_result_text_changed(0, 'Original task\nMore details')

        self.assertEqual(sorter_app.result_tasks, [(0, 'Original task\nMore details')])
        self.assertEqual(store.saved[-1], ([(0, 'Original task\nMore details')], [False]))


if __name__ == '__main__':
    unittest.main()

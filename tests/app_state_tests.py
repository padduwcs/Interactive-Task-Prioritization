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

    def test_manual_reorder_updates_saved_state(self):
        store = FakeStateStore()
        sorter_app = TaskSorterApp(state_store=store)

        sorter_app._show_result([(0, 'First'), (1, 'Second')], [False, True])
        sorter_app._on_result_order_changed([(1, 'Second'), (0, 'First')], [True, False])

        self.assertEqual(sorter_app.result_tasks, [(1, 'Second'), (0, 'First')])
        self.assertEqual(sorter_app.result_done_states, [True, False])
        self.assertEqual(store.saved[-1], ([(1, 'Second'), (0, 'First')], [True, False]))

    def test_adding_result_task_appends_and_saves(self):
        store = FakeStateStore()
        sorter_app = TaskSorterApp(state_store=store)

        sorter_app._show_result([(3, 'Existing')], [False])
        sorter_app._on_result_task_added('New task')

        self.assertEqual(sorter_app.result_tasks, [(3, 'Existing'), (4, 'New task')])
        self.assertEqual(sorter_app.result_done_states, [False, False])
        self.assertEqual(store.saved[-1], ([(3, 'Existing'), (4, 'New task')], [False, False]))


if __name__ == '__main__':
    unittest.main()

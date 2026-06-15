import os
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt6.QtWidgets import QApplication

from ui_components import ResultTaskWidget, TaskSorterWindow


def get_app():
    return QApplication.instance() or QApplication([])


class ResultTaskWidgetTests(unittest.TestCase):
    def setUp(self):
        self.app = get_app()

    def test_completion_checkbox_updates_only_its_own_task(self):
        first = ResultTaskWidget(1, 'First task')
        second = ResultTaskWidget(2, 'Second task')

        first.checkbox.setChecked(True)
        self.app.processEvents()

        self.assertTrue(first.checkbox.isChecked())
        self.assertIn('✓', first.checkbox.text())
        self.assertTrue(first.task_label.font().strikeOut())
        self.assertIn('border: 1px solid #10b981', first.main_container.styleSheet())

        self.assertFalse(second.checkbox.isChecked())
        self.assertNotIn('✓', second.checkbox.text())
        self.assertFalse(second.task_label.font().strikeOut())
        self.assertIn('border: 1px solid #cbd5e1', second.main_container.styleSheet())


class TaskSorterWindowTests(unittest.TestCase):
    def setUp(self):
        self.app = get_app()

    def test_has_compact_help_button(self):
        window = TaskSorterWindow()

        self.assertEqual(window.help_button.text(), '?')
        self.assertEqual(window.help_button.toolTip(), 'Keyboard shortcuts (F1)')

    def test_progress_and_help_text_use_enter_and_f1_labels(self):
        window = TaskSorterWindow()

        window.update_progress(2, 5)
        help_text = window.shortcuts_help_text()

        self.assertEqual(window.progress_label.text(), 'Comparison Step: 2 / 5')
        self.assertIn('Ctrl+Enter', help_text)
        self.assertIn('Enter</b> - Select focused task', help_text)
        self.assertIn('F1', help_text)
        self.assertNotIn('Shift+?', help_text)
        self.assertNotIn('Return', help_text)

    def test_result_view_restores_done_state_and_emits_changes(self):
        window = TaskSorterWindow()
        events = []
        window.result_completion_changed.connect(lambda index, checked: events.append((index, checked)))

        window.show_result_view([(0, 'First task'), (1, 'Second task')], [False, True])
        self.app.processEvents()

        first_widget = window.result_list.itemWidget(window.result_list.item(0))
        second_widget = window.result_list.itemWidget(window.result_list.item(1))
        self.assertFalse(first_widget.checkbox.isChecked())
        self.assertTrue(second_widget.checkbox.isChecked())
        self.assertEqual(events, [])

        first_widget.checkbox.setChecked(True)
        self.app.processEvents()

        self.assertEqual(events, [(0, True)])

    def test_result_view_has_copy_edit_and_copy_all_actions(self):
        window = TaskSorterWindow()
        window.show_result_view([(0, 'First task'), (1, 'Second task\nWith details')], [False, False])
        self.app.processEvents()

        first_widget = window.result_list.itemWidget(window.result_list.item(0))
        self.assertEqual(first_widget.copy_button.text(), 'Copy')
        self.assertEqual(first_widget.edit_button.text(), 'Edit')
        self.assertEqual(window.copy_all_button.text(), 'Copy All')

        self.app.clipboard().clear()
        first_widget.copy_button.click()
        self.assertEqual(self.app.clipboard().text(), 'First task')

        window.copy_all_button.click()
        self.assertEqual(self.app.clipboard().text(), '1. First task\n\n2. Second task\nWith details')

    def test_result_items_expand_for_long_content(self):
        window = TaskSorterWindow()
        long_task = 'Important task ' + ('with more details ' * 40)

        window.show_result_view([(0, long_task)], [False])
        self.app.processEvents()

        self.assertGreater(window.result_list.item(0).sizeHint().height(), 82)


if __name__ == '__main__':
    unittest.main()

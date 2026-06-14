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


if __name__ == '__main__':
    unittest.main()

"""PyQt6 UI components for the task prioritization application."""

from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QFrame,
    QCheckBox,
    QSizePolicy,
    QDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer


class TaskInputWidget(QFrame):
    def __init__(self, task_number: int):
        super().__init__()
        self.task_number = task_number
        self._build_ui()
        self.setObjectName('taskInputFrame')

    def _build_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet('background: white; border-radius: 16px;')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        self.index_label = QLabel(str(self.task_number))
        self.index_label.setObjectName('taskIndexLabel')
        layout.addWidget(self.index_label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('Task title and description...')
        self.text_edit.setObjectName('taskTextEdit')
        self.text_edit.setMinimumHeight(110)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.text_edit)

    def set_number(self, value: int):
        self.task_number = value
        self.index_label.setText(str(value))

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()

    def focus_text(self):
        self.text_edit.setFocus()


class ResultTaskWidget(QWidget):
    def __init__(self, sequence: int, task_text: str):
        super().__init__()
        self._build_ui(sequence, task_text)

    def _build_ui(self, sequence: int, task_text: str):
        self.main_container = QWidget()
        self.main_container.setStyleSheet('background: white; border-radius: 12px; padding: 0px;')
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.addWidget(self.main_container)

        container_layout = QHBoxLayout(self.main_container)
        container_layout.setContentsMargins(12, 10, 12, 10)
        container_layout.setSpacing(16)

        self.index_label = QLabel(str(sequence))
        self.index_label.setObjectName('resultIndexLabel')
        self.index_label.setMaximumWidth(30)
        container_layout.addWidget(self.index_label)

        self.task_label = QLabel(task_text)
        self.task_label.setWordWrap(True)
        self.task_label.setObjectName('resultTaskLabel')
        self.task_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.task_label.setMinimumHeight(40)
        container_layout.addWidget(self.task_label, stretch=1)

        self.checkbox = QCheckBox()
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setMinimumWidth(24)
        self.checkbox.stateChanged.connect(self._toggle_strikethrough)
        container_layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignVCenter)

    def _toggle_strikethrough(self, state: int):
        font = self.task_label.font()
        is_checked = state == Qt.CheckState.Checked
        font.setStrikeOut(is_checked)
        self.task_label.setFont(font)

        if is_checked:
            self.main_container.setStyleSheet('background: #d1fae5; border-radius: 12px; padding: 0px;')
        else:
            self.main_container.setStyleSheet('background: white; border-radius: 12px; padding: 0px;')


class TaskSorterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Task Prioritization')
        self.setMinimumSize(820, 720)
        self.task_inputs = []
        self._build_ui()
        self._apply_styles()
        self._setup_shortcuts()
        self.add_task_input()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(18)

        self.title_label = QLabel('Interactive Task Prioritization')
        self.title_label.setObjectName('titleLabel')
        self.main_layout.addWidget(self.title_label)

        self.description_label = QLabel(
            'Add tasks with optional multi-line descriptions, then sort them by priority through pairwise comparisons.'
        )
        self.description_label.setWordWrap(True)
        self.description_label.setObjectName('descriptionLabel')
        self.main_layout.addWidget(self.description_label)

        self.input_widget = QWidget()
        input_layout = QVBoxLayout(self.input_widget)
        input_layout.setSpacing(16)
        input_layout.setContentsMargins(0, 0, 0, 0)

        self.task_input_area = QScrollArea()
        self.task_input_area.setWidgetResizable(True)
        self.task_input_area.setObjectName('taskInputArea')
        self.task_input_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.task_input_container = QWidget()
        self.task_input_layout = QVBoxLayout(self.task_input_container)
        self.task_input_layout.setSpacing(14)
        self.task_input_layout.setContentsMargins(0, 0, 0, 0)
        self.task_input_layout.addStretch()
        self.task_input_area.setWidget(self.task_input_container)
        input_layout.addWidget(self.task_input_area)

        self.input_buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(self.input_buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(14)

        self.add_task_button = QPushButton('Add New Task')
        self.add_task_button.setObjectName('secondaryButton')
        self.add_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_task_button.setFixedHeight(48)
        buttons_layout.addWidget(self.add_task_button)

        self.start_button = QPushButton('Start Sorting')
        self.start_button.setObjectName('primaryButton')
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setFixedHeight(48)
        buttons_layout.addWidget(self.start_button)

        input_layout.addWidget(self.input_buttons_widget)
        self.main_layout.addWidget(self.input_widget)

        self.comparison_widget = QWidget()
        self.comparison_widget.setVisible(False)
        self._build_comparison_widget()
        self.main_layout.addWidget(self.comparison_widget)

        self.result_widget = QWidget()
        self.result_widget.setVisible(False)
        self._build_result_widget()
        self.main_layout.addWidget(self.result_widget)

    def _build_comparison_widget(self):
        layout = QVBoxLayout(self.comparison_widget)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_label = QLabel('Comparison Step: 0 / ~0')
        self.progress_label.setObjectName('progressLabel')
        layout.addWidget(self.progress_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.question_label = QLabel('Which task is more important?')
        self.question_label.setObjectName('questionLabel')
        layout.addWidget(self.question_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button_row = QHBoxLayout()
        button_row.setSpacing(16)

        self.button_a = QPushButton('Task A')
        self.button_b = QPushButton('Task B')
        for button in (self.button_a, self.button_b):
            button.setObjectName('comparisonButton')
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            button.setMinimumHeight(180)
            button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            button_row.addWidget(button)

        layout.addLayout(button_row)

    def _build_result_widget(self):
        layout = QVBoxLayout(self.result_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.result_list = QListWidget()
        self.result_list.setObjectName('resultList')
        self.result_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.result_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        layout.addWidget(self.result_list)

        self.restart_button = QPushButton('Restart')
        self.restart_button.setObjectName('secondaryButton')
        self.restart_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_button.setFixedHeight(48)
        layout.addWidget(self.restart_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #f3f4f6;
                color: #111827;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            #titleLabel {
                font-size: 26px;
                font-weight: 700;
                color: #111827;
            }
            #descriptionLabel {
                font-size: 14px;
                color: #4b5563;
                margin-bottom: 8px;
            }
            QScrollArea#taskInputArea {
                border: none;
                background: transparent;
            }
            QFrame#taskInputFrame {
                border: 1px solid #d1d5db;
                border-radius: 20px;
                background: white;
                padding: 0px;
            }
            QLabel#taskIndexLabel {
                font-size: 13px;
                font-weight: 700;
                color: #2563eb;
            }
            QTextEdit#taskTextEdit {
                border: 1px solid #e2e8f0;
                border-radius: 14px;
                padding: 12px;
                font-size: 14px;
                min-height: 120px;
            }
            QPushButton#primaryButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 700;
                padding: 0 24px;
            }
            QPushButton#primaryButton:hover {
                background: #1d4ed8;
            }
            QPushButton#secondaryButton {
                background: white;
                color: #1f2937;
                border: 1px solid #d1d5db;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 700;
                padding: 0 22px;
            }
            QPushButton#secondaryButton:hover {
                border-color: #93c5fd;
                background: #f8fbff;
            }
            QLabel#progressLabel {
                font-size: 15px;
                font-weight: 700;
                color: #111827;
            }
            QLabel#questionLabel {
                font-size: 18px;
                font-weight: 700;
                color: #111827;
            }
            QPushButton#comparisonButton {
                background: white;
                color: #111827;
                border: 2px solid #dc2626;
                border-radius: 20px;
                font-size: 16px;
                font-weight: 700;
                padding: 22px;
                text-align: left;
            }
            QPushButton#comparisonButton:hover {
                border-color: #f87171;
            }
            QPushButton#comparisonButton:focus {
                border-color: #16a34a;
                outline: none;
                border-width: 3px;
            }
            QListWidget#resultList {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 20px;
                padding: 10px;
            }
            QLabel#resultIndexLabel {
                font-size: 14px;
                font-weight: 700;
                color: #2563eb;
                min-width: 24px;
            }
            QLabel#resultTaskLabel {
                font-size: 15px;
                color: #111827;
            }
            """
        )

    def _setup_shortcuts(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        new_task_action = QAction(self)
        new_task_action.setShortcut(QKeySequence('Ctrl+N'))
        new_task_action.triggered.connect(lambda: self.add_task_input(True))
        self.addAction(new_task_action)

        start_sort_action = QAction(self)
        start_sort_action.setShortcut(QKeySequence('Ctrl+Return'))
        start_sort_action.triggered.connect(self.start_button.click)
        self.addAction(start_sort_action)

        left_action = QAction(self)
        left_action.setShortcut(QKeySequence(Qt.Key.Key_Left))
        left_action.triggered.connect(self.focus_left_button)
        self.addAction(left_action)

        right_action = QAction(self)
        right_action.setShortcut(QKeySequence(Qt.Key.Key_Right))
        right_action.triggered.connect(self.focus_right_button)
        self.addAction(right_action)

        enter_action = QAction(self)
        enter_action.setShortcut(QKeySequence(Qt.Key.Key_Return))
        enter_action.triggered.connect(self.select_focused_button)
        self.addAction(enter_action)

        numpad_enter_action = QAction(self)
        numpad_enter_action.setShortcut(QKeySequence(Qt.Key.Key_Enter))
        numpad_enter_action.triggered.connect(self.select_focused_button)
        self.addAction(numpad_enter_action)

        help_action = QAction(self)
        help_action.setShortcut(QKeySequence('Shift+?'))
        help_action.triggered.connect(self.show_shortcuts_help)
        self.addAction(help_action)

    def add_task_input(self, focus_text: bool = True):
        index = len(self.task_inputs) + 1
        task_widget = TaskInputWidget(index)
        self.task_inputs.append(task_widget)

        self.task_input_layout.insertWidget(self.task_input_layout.count() - 1, task_widget)

        if focus_text:
            task_widget.focus_text()
            # Schedule scroll to happen after layout is updated
            QTimer.singleShot(100, lambda: self.task_input_area.ensureWidgetVisible(task_widget, 0, 50))

    def gather_tasks(self) -> list[tuple[int, str]]:
        tasks = []
        for index, task_widget in enumerate(self.task_inputs, start=1):
            task_text = task_widget.get_text()
            if task_text:
                tasks.append((index - 1, task_text))
        return tasks

    def set_input_hint(self, message: str):
        self.description_label.setText(message)

    def show_comparison_view(self):
        self.input_widget.setVisible(False)
        self.comparison_widget.setVisible(True)
        self.result_widget.setVisible(False)
        self.button_a.setFocus()

    def show_result_view(self, sorted_tasks: list[tuple[int, str]]):
        self.comparison_widget.setVisible(False)
        self.input_widget.setVisible(False)
        self.result_widget.setVisible(True)
        self.result_list.clear()

        for sequence, task in enumerate(sorted_tasks, start=1):
            row_widget = ResultTaskWidget(sequence, task[1])
            item = QListWidgetItem(self.result_list)
            item.setSizeHint(row_widget.sizeHint())
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, row_widget)
        
        if self.result_list.count() > 0:
            self.result_list.scrollToTop()

    def update_progress(self, current_step: int, total_steps: int):
        self.progress_label.setText(f'Comparison Step: {current_step} / ~{total_steps}')

    def update_comparison_pair(self, task_a, task_b):
        self.button_a.task = task_a
        self.button_b.task = task_b
        self.button_a.setText(task_a[1])
        self.button_b.setText(task_b[1])
        self.button_a.setFocus()

    def focus_left_button(self):
        if self.comparison_widget.isVisible():
            self.button_a.setFocus()

    def focus_right_button(self):
        if self.comparison_widget.isVisible():
            self.button_b.setFocus()

    def select_focused_button(self):
        if not self.comparison_widget.isVisible():
            return
        focused = self.focusWidget()
        if focused == self.button_a:
            self.button_a.click()
        elif focused == self.button_b:
            self.button_b.click()

    def reset(self):
        self.description_label.setText(
            'Add tasks with optional multi-line descriptions, then sort them by priority through pairwise comparisons.'
        )
        self.comparison_widget.setVisible(False)
        self.result_widget.setVisible(False)
        self.input_widget.setVisible(True)
        self.clear_task_inputs()
        self.add_task_input(True)

    def clear_task_inputs(self):
        while self.task_inputs:
            widget = self.task_inputs.pop()
            widget.setParent(None)
            widget.deleteLater()

    def show_shortcuts_help(self):
        shortcuts_text = """
<b>Keyboard Shortcuts</b><br><br>
<b>Input View:</b><br>
• <b>Ctrl+N</b> - Add new task<br>
• <b>Ctrl+Return</b> - Start sorting<br>
<br>
<b>Comparison View:</b><br>
• <b>Left Arrow</b> - Focus left button<br>
• <b>Right Arrow</b> - Focus right button<br>
• <b>Return / Enter</b> - Select focused task<br>
<br>
<b>Result View:</b><br>
• <b>Click checkbox</b> - Mark task as done (green highlight)<br>
• <b>Restart button</b> - Return to input view<br>
<br>
<b>Global:</b><br>
• <b>?</b> - Show this help dialog
        """
        msg = QMessageBox(self)
        msg.setWindowTitle('Keyboard Shortcuts')
        msg.setText(shortcuts_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setStyleSheet(
            """
            QMessageBox {
                background: white;
            }
            QMessageBox QLabel {
                color: #111827;
            }
            QMessageBox QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: #1d4ed8;
            }
            """
        )
        msg.exec()

"""PyQt6 UI components for the task prioritization application."""

from math import ceil
from string import Template

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
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
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal

from theme_design import THEMES


class TaskInputWidget(QFrame):
    def __init__(self, task_number: int):
        super().__init__()
        self.task_number = task_number
        self._build_ui()
        self.setObjectName('taskInputFrame')

    def _build_ui(self):
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(12)

        self.index_label = QLabel(str(self.task_number))
        self.index_label.setObjectName('taskIndexLabel')
        self.index_label.setFixedSize(34, 34)
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.index_label, alignment=Qt.AlignmentFlag.AlignTop)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('Task title and description...')
        self.text_edit.setObjectName('taskInputTextEdit')
        self.text_edit.setMinimumHeight(92)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.text_edit)

    def set_number(self, value: int):
        self.task_number = value
        self.index_label.setText(str(value))

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()

    def focus_text(self):
        self.text_edit.setFocus()


class DragHandle(QLabel):
    drag_requested = pyqtSignal(object)

    def __init__(self, row_widget):
        super().__init__('::')
        self.row_widget = row_widget
        self._press_pos = None
        self.setObjectName('dragHandle')
        self.setToolTip('Drag to reorder')
        self.setFixedSize(22, 28)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_pos is None or not event.buttons() & Qt.MouseButton.LeftButton:
            super().mouseMoveEvent(event)
            return

        distance = (event.position().toPoint() - self._press_pos).manhattanLength()
        if distance >= QApplication.startDragDistance():
            self._press_pos = None
            self.drag_requested.emit(self.row_widget)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._press_pos = None
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        super().mouseReleaseEvent(event)


class ResultTaskWidget(QFrame):
    def __init__(self, sequence: int, task_text: str, is_done: bool = False, task_id: int | None = None):
        super().__init__()
        self.task_id = task_id if task_id is not None else sequence - 1
        self._build_ui(sequence, task_text)
        if is_done:
            self.checkbox.setChecked(True)

    def _build_ui(self, sequence: int, task_text: str):
        self.main_container = self
        self.setObjectName('resultTaskFrame')
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._set_completed_style(False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.drag_handle = DragHandle(self)
        header_layout.addWidget(self.drag_handle)

        self.index_label = QLabel(str(sequence))
        self.index_label.setObjectName('resultIndexLabel')
        self.index_label.setFixedSize(30, 28)
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.index_label)
        header_layout.addStretch()

        self.copy_button = QPushButton('Copy')
        self.copy_button.setObjectName('smallActionButton')
        self.copy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_button.setFixedSize(58, 28)

        self.edit_button = QPushButton('Edit')
        self.edit_button.setObjectName('smallActionButton')
        self.edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_button.setFixedSize(52, 28)

        self.checkbox = QCheckBox('Done')
        self.checkbox.setObjectName('doneCheckbox')
        self.checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        self.checkbox.setFixedHeight(28)
        self.checkbox.setMinimumWidth(72)
        self.checkbox.toggled.connect(self._toggle_completed)

        header_layout.addWidget(self.copy_button)
        header_layout.addWidget(self.edit_button)
        header_layout.addWidget(self.checkbox)
        layout.addLayout(header_layout)

        self.task_label = QTextEdit()
        self.task_label.setPlainText(task_text)
        self.task_label.setReadOnly(True)
        self.task_label.setFrameShape(QFrame.Shape.NoFrame)
        self.task_label.setObjectName('resultTaskLabel')
        self.task_label.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.task_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.task_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.task_label.setMinimumHeight(42)
        layout.addWidget(self.task_label)

    def task_text(self) -> str:
        return self.task_label.toPlainText()

    def set_task_text(self, task_text: str):
        self.task_label.setPlainText(task_text)

    def set_sequence(self, sequence: int):
        self.index_label.setText(str(sequence))

    def preferred_height(self, available_width: int, max_height: int | None = None) -> int:
        text_width = max(80, available_width - 44)
        document = self.task_label.document().clone()
        document.setTextWidth(text_width)
        text_height = ceil(document.size().height()) + 10
        natural_height = max(112, text_height + 82)
        target_height = natural_height

        if max_height is not None:
            target_height = min(natural_height, max(140, max_height))

        text_view_height = max(42, target_height - 82)
        self.task_label.setFixedHeight(text_view_height)
        if natural_height > target_height:
            self.task_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.task_label.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        return target_height

    def _toggle_completed(self, is_checked: bool):
        font = self.task_label.font()
        font.setStrikeOut(is_checked)
        self.task_label.setFont(font)
        self.checkbox.setText('✓ Done' if is_checked else 'Done')
        self._set_completed_style(is_checked)

    def _set_completed_style(self, is_checked: bool):
        if is_checked:
            self.setObjectName('resultTaskDoneFrame')
        else:
            self.setObjectName('resultTaskFrame')
        self.style().unpolish(self)
        self.style().polish(self)


class SmoothResultListWidget(QListWidget):
    viewport_resized = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(8)
        self._drag_scroll_step = 0
        self._drag_scroll_margin = 64
        self._drag_scroll_timer = QTimer(self)
        self._drag_scroll_timer.setInterval(35)
        self._drag_scroll_timer.timeout.connect(self._continue_drag_scroll)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.viewport_resized.emit()

    def wheelEvent(self, event):
        pixel_delta = event.pixelDelta().y()
        angle_delta = event.angleDelta().y()

        if pixel_delta:
            delta = pixel_delta
        elif angle_delta:
            delta = int(angle_delta / 120 * 28)
        else:
            super().wheelEvent(event)
            return

        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.value() - delta)
        event.accept()

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        self._update_drag_scroll(event.position().toPoint().y())

    def dragLeaveEvent(self, event):
        self._stop_drag_scroll()
        super().dragLeaveEvent(event)

    def dropEvent(self, event):
        self._stop_drag_scroll()
        super().dropEvent(event)

    def _update_drag_scroll(self, y_position: int):
        step = self.drag_scroll_step_for_position(y_position)
        if step == 0:
            self._stop_drag_scroll()
            return

        self._drag_scroll_step = step
        self._continue_drag_scroll()
        if not self._drag_scroll_timer.isActive():
            self._drag_scroll_timer.start()

    def drag_scroll_step_for_position(self, y_position: int) -> int:
        height = self.viewport().height()
        if height <= 0:
            return 0

        margin = min(self._drag_scroll_margin, max(20, height // 3))
        if y_position < margin:
            distance = margin - max(0, y_position)
            return -max(6, int(distance / margin * 28))
        if y_position > height - margin:
            distance = min(height, y_position) - (height - margin)
            return max(6, int(distance / margin * 28))
        return 0

    def _continue_drag_scroll(self):
        if self._drag_scroll_step == 0:
            self._stop_drag_scroll()
            return

        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.value() + self._drag_scroll_step)

    def _stop_drag_scroll(self):
        self._drag_scroll_step = 0
        if self._drag_scroll_timer.isActive():
            self._drag_scroll_timer.stop()


class TaskSorterWindow(QWidget):
    result_completion_changed = pyqtSignal(int, bool)
    result_text_changed = pyqtSignal(int, str)
    result_order_changed = pyqtSignal(list, list)
    result_task_added = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Task Prioritization')
        self.setMinimumSize(820, 720)
        self.current_theme_key = 'light'
        self.task_inputs = []
        self.result_items = []
        self._updating_result_list = False
        self._build_ui()
        self._apply_styles()
        self._setup_shortcuts()
        self.add_task_input()

    def _build_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 24, 24, 24)
        self.main_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        self.title_label = QLabel('Interactive Task Prioritization')
        self.title_label.setObjectName('titleLabel')
        header_layout.addWidget(self.title_label, stretch=1)

        self.theme_button = QPushButton()
        self.theme_button.setObjectName('themeButton')
        self.theme_button.setToolTip('Toggle light/dark theme')
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.setFixedSize(92, 34)
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.help_button = QPushButton('?')
        self.help_button.setObjectName('helpButton')
        self.help_button.setToolTip('Keyboard shortcuts (F1)')
        self.help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_button.setFixedSize(34, 34)
        self.help_button.clicked.connect(self.show_shortcuts_help)
        header_layout.addWidget(self.help_button, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.main_layout.addLayout(header_layout)

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

        self.progress_label = QLabel('Comparison Step: 0 / 0')
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

        self.result_list = SmoothResultListWidget()
        self.result_list.setObjectName('resultList')
        self.result_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.result_list.setSpacing(10)
        self.result_list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.result_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.result_list.setDragDropOverwriteMode(False)
        self.result_list.setDragEnabled(True)
        self.result_list.setAcceptDrops(True)
        self.result_list.setDropIndicatorShown(True)
        self.result_list.setAutoScroll(True)
        self.result_list.setAutoScrollMargin(36)
        self.result_list.viewport_resized.connect(self.update_result_item_sizes)
        self.result_list.model().rowsMoved.connect(self._on_result_rows_moved)
        layout.addWidget(self.result_list)

        result_buttons_layout = QHBoxLayout()
        result_buttons_layout.setContentsMargins(0, 0, 0, 0)
        result_buttons_layout.setSpacing(12)
        result_buttons_layout.addStretch()

        self.add_result_task_button = QPushButton('Add Task')
        self.add_result_task_button.setObjectName('secondaryButton')
        self.add_result_task_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_result_task_button.setFixedHeight(48)
        self.add_result_task_button.clicked.connect(self.add_result_task)
        result_buttons_layout.addWidget(self.add_result_task_button)

        self.copy_all_button = QPushButton('Copy All')
        self.copy_all_button.setObjectName('secondaryButton')
        self.copy_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_all_button.setFixedHeight(48)
        self.copy_all_button.clicked.connect(self.copy_all_results)
        result_buttons_layout.addWidget(self.copy_all_button)

        self.restart_button = QPushButton('Restart')
        self.restart_button.setObjectName('secondaryButton')
        self.restart_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.restart_button.setFixedHeight(48)
        result_buttons_layout.addWidget(self.restart_button)
        layout.addLayout(result_buttons_layout)

    def _apply_styles(self):
        colors = THEMES[self.current_theme_key].colors
        self._sync_theme_button()
        self.setStyleSheet(
            Template(
            """
            QWidget {
                background: $background;
                color: $text;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            #titleLabel {
                font-size: 26px;
                font-weight: 700;
                color: $text;
            }
            #descriptionLabel {
                font-size: 14px;
                color: $text_muted;
                margin-bottom: 8px;
            }
            QScrollArea#taskInputArea {
                border: none;
                background: transparent;
            }
            QFrame#taskInputFrame {
                border: 1px solid $border;
                border-radius: 12px;
                background: $surface;
                padding: 0px;
            }
            QLabel#taskIndexLabel {
                background: $index_bg;
                border: 1px solid $primary;
                border-radius: 17px;
                font-size: 12px;
                font-weight: 700;
                color: $primary;
            }
            QTextEdit#taskInputTextEdit {
                background: transparent;
                color: $text;
                border: none;
                padding: 4px 2px;
                font-size: 14px;
                selection-background-color: $primary;
                selection-color: $primary_text;
            }
            QTextEdit#taskTextEdit {
                background: $surface_alt;
                color: $text;
                border: 1px solid $input_border;
                border-radius: 14px;
                padding: 12px;
                font-size: 14px;
                min-height: 120px;
            }
            QPushButton#primaryButton {
                background: $primary;
                color: $primary_text;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 700;
                padding: 0 24px;
            }
            QPushButton#primaryButton:hover {
                background: $primary_hover;
            }
            QPushButton#secondaryButton {
                background: $surface;
                color: $text;
                border: 1px solid $border;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 700;
                padding: 0 22px;
            }
            QPushButton#secondaryButton:hover {
                border-color: $primary_hover;
                background: $secondary_hover;
            }
            QPushButton#smallActionButton {
                background: $surface_alt;
                color: $text;
                border: 1px solid $input_border;
                border-radius: 8px;
                font-size: 11px;
                font-weight: 700;
                padding: 0px;
            }
            QPushButton#smallActionButton:hover {
                background: $index_bg;
                border-color: $primary_hover;
            }
            QPushButton#themeButton,
            QPushButton#helpButton {
                background: $surface;
                color: $text;
                border: 1px solid $border;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 800;
                padding: 0px;
            }
            QPushButton#themeButton {
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton#themeButton:hover,
            QPushButton#helpButton:hover {
                border-color: $primary_hover;
                background: $index_bg;
            }
            QLabel#progressLabel {
                font-size: 15px;
                font-weight: 700;
                color: $text;
            }
            QLabel#questionLabel {
                font-size: 18px;
                font-weight: 700;
                color: $text;
            }
            QPushButton#comparisonButton {
                background: $surface;
                color: $text;
                border: 2px solid $comparison_border;
                border-radius: 20px;
                font-size: 16px;
                font-weight: 700;
                padding: 22px;
                text-align: left;
            }
            QPushButton#comparisonButton:hover {
                border-color: $comparison_hover;
            }
            QPushButton#comparisonButton:focus {
                border-color: $focus;
                outline: none;
                border-width: 3px;
            }
            QListWidget#resultList {
                background: transparent;
                border: none;
                padding: 2px;
            }
            QListWidget#resultList::item {
                background: transparent;
                border: none;
            }
            QListWidget#resultList::item:selected {
                background: transparent;
            }
            QLabel#dragHandle {
                background: transparent;
                color: $drag_handle;
                border: none;
                font-size: 14px;
                font-weight: 800;
            }
            QFrame#resultTaskFrame {
                background: $surface;
                border: 1px solid $border;
                border-radius: 12px;
            }
            QFrame#resultTaskDoneFrame {
                background: $done_surface;
                border: 1px solid $done_border;
                border-radius: 12px;
            }
            QFrame#resultTaskFrame QLabel#resultTaskLabel,
            QFrame#resultTaskDoneFrame QLabel#resultTaskLabel,
            QFrame#resultTaskFrame QTextEdit#resultTaskLabel,
            QFrame#resultTaskDoneFrame QTextEdit#resultTaskLabel,
            QFrame#resultTaskFrame QLabel#dragHandle,
            QFrame#resultTaskDoneFrame QLabel#dragHandle,
            QFrame#resultTaskFrame QCheckBox#doneCheckbox,
            QFrame#resultTaskDoneFrame QCheckBox#doneCheckbox {
                background: transparent;
            }
            QLabel#resultIndexLabel {
                background: $index_bg;
                border: 1px solid $primary;
                border-radius: 14px;
                font-size: 13px;
                font-weight: 700;
                color: $primary;
            }
            QTextEdit#resultTaskLabel {
                border: none;
                font-size: 15px;
                color: $text;
                padding: 0px;
                selection-background-color: $primary;
                selection-color: $primary_text;
            }
            QTextEdit#resultTaskLabel QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QTextEdit#resultTaskLabel QScrollBar::handle:vertical {
                background: $drag_handle;
                border-radius: 5px;
                min-height: 28px;
            }
            QTextEdit#resultTaskLabel QScrollBar::add-line:vertical,
            QTextEdit#resultTaskLabel QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QCheckBox#doneCheckbox {
                background: transparent;
                color: $text_muted;
                font-size: 12px;
                font-weight: 700;
                spacing: 6px;
            }
            QCheckBox#doneCheckbox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid $drag_handle;
                border-radius: 5px;
                background: $surface;
            }
            QCheckBox#doneCheckbox::indicator:hover {
                border-color: $primary;
            }
            QCheckBox#doneCheckbox::indicator:checked {
                background: $focus;
                border-color: $done_border;
            }
            """
            ).substitute(colors)
        )

    def _sync_theme_button(self):
        if not hasattr(self, 'theme_button'):
            return

        if self.current_theme_key == 'dark':
            self.theme_button.setText('Light')
            self.theme_button.setToolTip('Switch to light theme')
        else:
            self.theme_button.setText('Dark')
            self.theme_button.setToolTip('Switch to dark theme')

    def toggle_theme(self):
        self.current_theme_key = 'dark' if self.current_theme_key == 'light' else 'light'
        self._apply_styles()

    def _setup_shortcuts(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        new_task_action = QAction(self)
        new_task_action.setShortcut(QKeySequence('Ctrl+N'))
        new_task_action.triggered.connect(self.add_task_input_from_shortcut)
        self.addAction(new_task_action)

        start_sort_action = QAction(self)
        start_sort_action.setShortcut(QKeySequence('Ctrl+Return'))
        start_sort_action.triggered.connect(self.start_sort_from_shortcut)
        self.addAction(start_sort_action)

        start_sort_enter_action = QAction(self)
        start_sort_enter_action.setShortcut(QKeySequence('Ctrl+Enter'))
        start_sort_enter_action.triggered.connect(self.start_sort_from_shortcut)
        self.addAction(start_sort_enter_action)

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

        f1_help_action = QAction(self)
        f1_help_action.setShortcut(QKeySequence(Qt.Key.Key_F1))
        f1_help_action.triggered.connect(self.show_shortcuts_help)
        self.addAction(f1_help_action)

    def add_task_input(self, focus_text: bool = True):
        self.reset_input_hint()
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

    def reset_input_hint(self):
        self.description_label.setText(
            'Add tasks with optional multi-line descriptions, then sort them by priority through pairwise comparisons.'
        )

    def add_task_input_from_shortcut(self):
        if self.input_widget.isVisible():
            self.add_task_input(True)

    def start_sort_from_shortcut(self):
        if self.input_widget.isVisible():
            self.start_button.click()

    def show_comparison_view(self):
        self.input_widget.setVisible(False)
        self.comparison_widget.setVisible(True)
        self.result_widget.setVisible(False)
        self.button_a.setFocus()

    def show_result_view(self, sorted_tasks: list[tuple[int, str]], done_states: list[bool] | None = None):
        self.comparison_widget.setVisible(False)
        self.input_widget.setVisible(False)
        self.result_widget.setVisible(True)
        self._updating_result_list = True
        self.result_list.clear()
        self.result_items = []
        done_states = done_states or []

        for sequence, task in enumerate(sorted_tasks, start=1):
            result_index = sequence - 1
            is_done = bool(done_states[result_index]) if result_index < len(done_states) else False
            row_widget = ResultTaskWidget(sequence, task[1], is_done, task[0])
            row_widget.drag_handle.drag_requested.connect(self.start_result_drag)
            row_widget.copy_button.clicked.connect(lambda _, row=row_widget: self.copy_result_task(row))
            row_widget.edit_button.clicked.connect(lambda _, row=row_widget: self.edit_result_task(row))
            row_widget.checkbox.toggled.connect(
                lambda checked, row=row_widget: self._emit_completion_changed(row, checked)
            )
            item = QListWidgetItem(self.result_list)
            self.result_list.addItem(item)
            self.result_list.setItemWidget(item, row_widget)
            self.result_items.append((item, row_widget))

        self.update_result_item_sizes()
        QTimer.singleShot(0, self.update_result_item_sizes)
        self._updating_result_list = False
        
        if self.result_list.count() > 0:
            self.result_list.scrollToTop()

    def copy_result_task(self, row_widget: ResultTaskWidget):
        QApplication.clipboard().setText(row_widget.task_text())

    def start_result_drag(self, row_widget: ResultTaskWidget):
        index = self.index_for_row_widget(row_widget)
        if index is None:
            return

        self.result_list.setCurrentRow(index)
        self.result_list.startDrag(Qt.DropAction.MoveAction)

    def copy_all_results(self):
        task_texts = []
        for index, row_widget in enumerate(self.current_result_rows(), start=1):
            task_texts.append(f'{index}. {row_widget.task_text()}')

        QApplication.clipboard().setText('\n\n'.join(task_texts))

    def add_result_task(self):
        task_text = self.prompt_result_task_text('Add Task')
        if task_text is not None:
            self.result_task_added.emit(task_text)

    def edit_result_task(self, row_widget: ResultTaskWidget):
        index = self.index_for_row_widget(row_widget)
        if index is None:
            return

        updated_text = self.prompt_result_task_text('Edit Task', row_widget.task_text())
        if updated_text is None:
            return

        row_widget.set_task_text(updated_text)
        self.result_text_changed.emit(index, updated_text)
        self.update_result_item_sizes()

    def prompt_result_task_text(self, title: str, initial_text: str = '') -> str | None:
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(520, 360)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        text_edit = QTextEdit()
        text_edit.setPlainText(initial_text)
        text_edit.setObjectName('taskTextEdit')
        layout.addWidget(text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        updated_text = text_edit.toPlainText().strip()
        if not updated_text:
            QMessageBox.warning(self, 'Task is empty', 'Please keep at least some content for this task.')
            return None

        return updated_text

    def current_result_rows(self) -> list[ResultTaskWidget]:
        rows = []
        for row in range(self.result_list.count()):
            row_widget = self.result_list.itemWidget(self.result_list.item(row))
            if row_widget is not None:
                rows.append(row_widget)
        return rows

    def current_result_tasks_and_done_states(self):
        tasks = []
        done_states = []
        for row_widget in self.current_result_rows():
            tasks.append((row_widget.task_id, row_widget.task_text()))
            done_states.append(row_widget.checkbox.isChecked())
        return tasks, done_states

    def index_for_row_widget(self, target_widget: ResultTaskWidget) -> int | None:
        for row, row_widget in enumerate(self.current_result_rows()):
            if row_widget is target_widget:
                return row
        return None

    def _emit_completion_changed(self, row_widget: ResultTaskWidget, is_done: bool):
        index = self.index_for_row_widget(row_widget)
        if index is not None:
            self.result_completion_changed.emit(index, is_done)

    def _on_result_rows_moved(self, *args):
        if not self._updating_result_list:
            QTimer.singleShot(0, self._emit_result_order_changed)

    def _emit_result_order_changed(self):
        if self._updating_result_list:
            return

        self.sync_result_items_from_list()
        tasks, done_states = self.current_result_tasks_and_done_states()
        self.result_order_changed.emit(tasks, done_states)

    def sync_result_items_from_list(self):
        self.result_items = []
        for row in range(self.result_list.count()):
            item = self.result_list.item(row)
            row_widget = self.result_list.itemWidget(item)
            if row_widget is None:
                continue
            row_widget.set_sequence(row + 1)
            self.result_items.append((item, row_widget))
        self.update_result_item_sizes()

    def update_result_item_sizes(self):
        available_width = self.result_list.viewport().width()
        max_item_height = max(160, self.result_list.viewport().height() - 16)
        for item, row_widget in self.result_items:
            target_height = row_widget.preferred_height(available_width, max_item_height)
            row_widget.setFixedHeight(target_height)
            item.setSizeHint(QSize(0, target_height + 4))

    def update_progress(self, current_step: int, total_steps: int):
        self.progress_label.setText(f'Comparison Step: {current_step} / {total_steps}')

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
        self.reset_input_hint()
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

    def shortcuts_help_text(self) -> str:
        return """
<b>Keyboard Shortcuts</b><br><br>
<b>Input View:</b><br>
• <b>Ctrl+N</b> - Add new task<br>
• <b>Ctrl+Enter</b> - Start sorting<br>
<br>
<b>Comparison View:</b><br>
• <b>Left Arrow</b> - Focus left button<br>
• <b>Right Arrow</b> - Focus right button<br>
• <b>Enter</b> - Select focused task<br>
<br>
<b>Result View:</b><br>
• <b>Drag tasks</b> - Manually reorder the sorted list<br>
• <b>Add Task</b> - Add a task to the result list<br>
• <b>Click checkbox</b> - Mark task as done (green highlight)<br>
• <b>Copy</b> - Copy one task<br>
• <b>Edit</b> - Edit one task and save it automatically<br>
• <b>Copy All</b> - Copy every task as a numbered list<br>
• <b>Restart button</b> - Go back to input view<br>
<br>
<b>Global:</b><br>
• <b>F1</b> - Show this help dialog
        """

    def show_shortcuts_help(self):
        shortcuts_text = self.shortcuts_help_text()
        colors = THEMES[self.current_theme_key].colors
        msg = QMessageBox(self)
        msg.setWindowTitle('Keyboard Shortcuts')
        msg.setText(shortcuts_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setStyleSheet(
            Template(
            """
            QMessageBox {
                background: $surface;
            }
            QMessageBox QLabel {
                color: $text;
                background: $surface;
            }
            QMessageBox QPushButton {
                background: $primary;
                color: $primary_text;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: $primary_hover;
            }
            """
            ).substitute(colors)
        )
        msg.exec()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.result_widget.isVisible():
            self.update_result_item_sizes()

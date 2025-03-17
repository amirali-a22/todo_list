import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QListWidget, QListWidgetItem, QMenu)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class TodoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("فهرست وظایف")
        self.setGeometry(100, 100, 350, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Always on top

        # Task storage: list of dicts with text, status, and group info
        self.tasks = []  # {"text": str, "done": bool, "group_id": int}

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        self.header = QPushButton("فهرست وظایف")
        self.header.setStyleSheet("background-color: #4a90e2; color: white; font: bold 18px 'Vazirmatn'; padding: 10px;")
        self.header.setEnabled(False)  # Make it a label-like button
        layout.addWidget(self.header)

        # Input frame
        input_layout = QHBoxLayout()
        self.task_entry = QTextEdit()
        self.task_entry.setStyleSheet("font: 12px 'Vazirmatn'; border: 2px solid #ccc; border-radius: 5px;")
        self.task_entry.setFixedHeight(60)
        self.task_entry.setAlignment(Qt.AlignRight)  # RTL alignment
        input_layout.addWidget(self.task_entry)

        self.add_button = QPushButton("ذخیره")
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; font: bold 10px 'Vazirmatn'; padding: 5px;")
        self.add_button.clicked.connect(self.add_task)
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        # Task list
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("font: 11px 'Vazirmatn'; border: 2px solid #ccc; border-radius: 5px;")
        self.task_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.task_list.setLayoutDirection(Qt.RightToLeft)  # RTL for the list
        layout.addWidget(self.task_list)

        # Buttons frame
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("حذف انتخاب‌شده")
        self.delete_button.setStyleSheet("background-color: #e74c3c; color: white; font: bold 10px 'Vazirmatn'; padding: 5px;")
        self.delete_button.clicked.connect(self.delete_task)
        button_layout.addWidget(self.delete_button)

        self.toggle_button = QPushButton("انجام‌شده/لغو")
        self.toggle_button.setStyleSheet("background-color: #f39c12; color: white; font: bold 10px 'Vazirmatn'; padding: 5px;")
        self.toggle_button.clicked.connect(self.toggle_done)
        button_layout.addWidget(self.toggle_button)

        self.clear_button = QPushButton("حذف همه")
        self.clear_button.setStyleSheet("background-color: #e74c3c; color: white; font: bold 10px 'Vazirmatn'; padding: 5px;")
        self.clear_button.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        # Context menu
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)

        # Double-click to toggle done
        self.task_list.doubleClicked.connect(self.toggle_done)

        # Ctrl+Enter to add task
        self.task_entry.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.task_entry and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.add_task()
                return True
        return super().eventFilter(obj, event)

    def add_task(self):
        task_text = self.task_entry.toPlainText().strip()
        if task_text:
            lines = task_text.splitlines()
            group_id = len(self.tasks) if not self.tasks else max(t["group_id"] for t in self.tasks) + 1
            task_number = len(set(t["group_id"] for t in self.tasks)) + 1
            for i, line in enumerate(lines):
                if line.strip():
                    task = {"text": line.strip(), "done": False, "group_id": group_id}
                    self.tasks.append(task)
                    prefix = f"{task_number}. " if i == 0 else "   "
                    display_text = f"{line.strip()} {'✓' if task['done'] else ' '}{prefix}"
                    item = QListWidgetItem(display_text)
                    item.setTextAlignment(Qt.AlignRight)  # RTL alignment
                    if task["done"]:
                        item.setForeground(QColor("#888888"))
                    self.task_list.addItem(item)
            self.task_entry.clear()
        else:
            QMessageBox.warning(self, "هشدار", "لطفاً یک وظیفه وارد کنید!")

    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "هشدار", "لطفاً حداقل یک وظیفه را انتخاب کنید!")
            return

        selected_groups = set()
        for item in selected_items:
            row = self.task_list.row(item)
            selected_groups.add(self.tasks[row]["group_id"])

        indices_to_delete = []
        for i, task in enumerate(self.tasks):
            if task["group_id"] in selected_groups:
                indices_to_delete.append(i)

        for index in sorted(indices_to_delete, reverse=True):
            self.task_list.takeItem(index)
            self.tasks.pop(index)

        self.renumber_tasks()

    def clear_all(self):
        if not self.tasks:
            QMessageBox.information(self, "اطلاعات", "هیچ وظیفه‌ای برای حذف وجود ندارد!")
            return
        self.task_list.clear()
        self.tasks.clear()

    def toggle_done(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "هشدار", "لطفاً حداقل یک وظیفه را انتخاب کنید!")
            return

        selected_groups = set()
        for item in selected_items:
            row = self.task_list.row(item)
            selected_groups.add(self.tasks[row]["group_id"])

        for i, task in enumerate(self.tasks):
            if task["group_id"] in selected_groups:
                task["done"] = not task["done"]
                task_number = self.get_task_number(task["group_id"])
                is_first_line = i == min([idx for idx, t in enumerate(self.tasks) if t["group_id"] == task["group_id"]])
                prefix = f"{task_number}. " if is_first_line else "   "
                display_text = f"{task['text']} {'✓' if task['done'] else ' '}{prefix}"
                item = self.task_list.item(i)
                item.setText(display_text)
                item.setForeground(QColor("#888888" if task["done"] else "#333333"))
                item.setTextAlignment(Qt.AlignRight)

    def renumber_tasks(self):
        self.task_list.clear()
        group_numbers = {}
        current_number = 1
        for group_id in sorted(set(t["group_id"] for t in self.tasks)):
            group_numbers[group_id] = current_number
            current_number += 1

        for i, task in enumerate(self.tasks):
            task_number = group_numbers[task["group_id"]]
            is_first_line = i == min([idx for idx, t in enumerate(self.tasks) if t["group_id"] == task["group_id"]])
            prefix = f"{task_number}. " if is_first_line else "   "
            display_text = f"{task['text']} {'✓' if task['done'] else ' '}{prefix}"
            item = QListWidgetItem(display_text)
            item.setTextAlignment(Qt.AlignRight)
            item.setForeground(QColor("#888888" if task["done"] else "#333333"))
            self.task_list.addItem(item)

    def get_task_number(self, group_id):
        unique_groups = sorted(set(t["group_id"] for t in self.tasks))
        return unique_groups.index(group_id) + 1

    def show_context_menu(self, position):
        menu = QMenu()
        menu.addAction("حذف", self.delete_task)
        menu.addAction("انجام‌شده/لغو", self.toggle_done)
        menu.addAction("حذف همه", self.clear_all)
        menu.exec_(self.task_list.mapToGlobal(position))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())
"""
Tasks tab UI component - To-Do List management
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QComboBox, QLabel,
    QDialog, QDialogButtonBox, QDateTimeEdit, QCheckBox, QMessageBox,
    QSplitter, QGroupBox, QFormLayout, QProgressBar
)
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime

from ..models.database import Database, TasksModel


class TaskDialog(QDialog):
    """Dialog for creating/editing tasks"""

    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.task_data = task_data
        self.is_edit = task_data is not None

        self.setWindowTitle("Görevi Düzenle" if self.is_edit else "Yeni Görev")
        self.setMinimumSize(500, 450)
        self.setup_ui()

        if self.is_edit:
            self.load_task_data()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Başlık:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Görev başlığı...")
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)

        # Description
        desc_label = QLabel("Açıklama:")
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Görev açıklaması...")
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(desc_label)
        layout.addWidget(self.description_edit)

        # Category and Priority
        meta_layout = QHBoxLayout()

        category_label = QLabel("Kategori:")
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Genel", "İş", "Kişisel", "Alışveriş", "Sağlık", "Eğitim"
        ])
        meta_layout.addWidget(category_label)
        meta_layout.addWidget(self.category_combo)

        priority_label = QLabel("Öncelik:")
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([
            "Düşük", "Orta", "Yüksek", "Acil"
        ])
        self.priority_combo.setCurrentIndex(1)
        meta_layout.addWidget(priority_label)
        meta_layout.addWidget(self.priority_combo)

        layout.addLayout(meta_layout)

        # Status
        status_layout = QHBoxLayout()
        status_label = QLabel("Durum:")
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Beklemede", "Devam Ediyor", "Tamamlandı", "İptal Edildi"
        ])
        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)

        # Due date
        due_date_layout = QHBoxLayout()
        self.due_date_enabled = QCheckBox("Termin Tarihi:")
        self.due_date_edit = QDateTimeEdit()
        self.due_date_edit.setDateTime(QDateTime.currentDateTime().addDays(1))
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        due_date_layout.addWidget(self.due_date_enabled)
        due_date_layout.addWidget(self.due_date_edit)
        layout.addLayout(due_date_layout)

        # Estimated time
        time_layout = QHBoxLayout()
        time_label = QLabel("Tahmini Süre (dakika):")
        self.estimated_minutes = QLineEdit()
        self.estimated_minutes.setPlaceholderText("0")
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.estimated_minutes)
        layout.addLayout(time_layout)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_task_data(self):
        """Load existing task data into form"""
        if self.task_data:
            self.title_edit.setText(self.task_data.get('title', ''))
            self.description_edit.setText(self.task_data.get('description', ''))

            category = self.task_data.get('category', 'Genel')
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

            priority = self.task_data.get('priority', 2)
            self.priority_combo.setCurrentIndex(priority - 1)

            # Status
            status_map = {
                'pending': 0,
                'in_progress': 1,
                'completed': 2,
                'cancelled': 3
            }
            status = self.task_data.get('status', 'pending')
            self.status_combo.setCurrentIndex(status_map.get(status, 0))

            # Due date
            if self.task_data.get('due_date'):
                self.due_date_enabled.setChecked(True)
                due_date = datetime.fromisoformat(self.task_data['due_date'])
                self.due_date_edit.setDateTime(QDateTime(due_date))

            # Estimated minutes
            if self.task_data.get('estimated_minutes'):
                self.estimated_minutes.setText(str(self.task_data['estimated_minutes']))

    def get_task_data(self):
        """Get task data from form"""
        status_map = {
            0: 'pending',
            1: 'in_progress',
            2: 'completed',
            3: 'cancelled'
        }

        data = {
            'title': self.title_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'category': self.category_combo.currentText(),
            'priority': self.priority_combo.currentIndex() + 1,
            'status': status_map[self.status_combo.currentIndex()]
        }

        if self.due_date_enabled.isChecked():
            data['due_date'] = self.due_date_edit.dateTime().toPython()
        else:
            data['due_date'] = None

        if self.estimated_minutes.text().strip():
            try:
                data['estimated_minutes'] = int(self.estimated_minutes.text())
            except ValueError:
                data['estimated_minutes'] = None

        return data


class TasksTab(QWidget):
    """Tasks tab widget"""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.tasks_model = TasksModel(db)
        self.current_task_id = None

        self.setup_ui()
        self.load_tasks()

    def setup_ui(self):
        """Setup tab UI"""
        layout = QVBoxLayout(self)

        # Header with statistics
        header_layout = QHBoxLayout()

        stats_label = QLabel("📊 Görev İstatistikleri")
        header_layout.addWidget(stats_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        header_layout.addWidget(self.progress_bar)

        self.stats_label = QLabel()
        header_layout.addWidget(self.stats_label)

        layout.addLayout(header_layout)

        # Main content
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Tasks list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Filters
        filter_layout = QHBoxLayout()

        self.filter_status = QComboBox()
        self.filter_status.addItems([
            "Tümü", "Beklemede", "Devam Ediyor", "Tamamlandı"
        ])
        self.filter_status.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(self.filter_status)

        self.filter_category = QComboBox()
        self.filter_category.addItems([
            "Tümü", "Genel", "İş", "Kişisel", "Alışveriş", "Sağlık", "Eğitim"
        ])
        self.filter_category.currentTextChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(QLabel("Kategori:"))
        filter_layout.addWidget(self.filter_category)

        left_layout.addLayout(filter_layout)

        # Tasks list
        self.tasks_list = QListWidget()
        self.tasks_list.itemClicked.connect(self.on_task_selected)
        self.tasks_list.itemDoubleClicked.connect(self.edit_task)
        left_layout.addWidget(self.tasks_list)

        # Buttons
        buttons_layout = QHBoxLayout()

        new_btn = QPushButton("➕ Yeni Görev")
        new_btn.clicked.connect(self.add_task)
        buttons_layout.addWidget(new_btn)

        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.clicked.connect(self.edit_task)
        buttons_layout.addWidget(edit_btn)

        complete_btn = QPushButton("✅ Tamamla")
        complete_btn.clicked.connect(self.mark_complete)
        buttons_layout.addWidget(complete_btn)

        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(self.delete_task)
        buttons_layout.addWidget(delete_btn)

        left_layout.addLayout(buttons_layout)

        splitter.addWidget(left_panel)

        # Right panel - Task details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.detail_title = QLabel("Bir görev seçin...")
        font = self.detail_title.font()
        font.setPointSize(14)
        font.setBold(True)
        self.detail_title.setFont(font)
        self.detail_title.setWordWrap(True)
        right_layout.addWidget(self.detail_title)

        self.detail_meta = QLabel()
        self.detail_meta.setWordWrap(True)
        right_layout.addWidget(self.detail_meta)

        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        right_layout.addWidget(self.detail_description)

        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])

        layout.addWidget(splitter)

    def load_tasks(self, status=None, category=None):
        """Load tasks from database"""
        self.tasks_list.clear()

        # Apply filters
        if status and status != "Tümü":
            status_map = {
                'Beklemede': 'pending',
                'Devam Ediyor': 'in_progress',
                'Tamamlandı': 'completed'
            }
            status = status_map.get(status)

        if category and category == "Tümü":
            category = None

        tasks = self.tasks_model.get_tasks(status=status, category=category)

        priority_icons = {
            1: "🔵", 2: "⚪", 3: "🟡", 4: "🔴"
        }

        status_icons = {
            'pending': "⏳",
            'in_progress': "🔄",
            'completed': "✅",
            'cancelled': "❌"
        }

        for task in tasks:
            priority_icon = priority_icons.get(task['priority'], "⚪")
            status_icon = status_icons.get(task['status'], "⏳")
            item_text = f"{status_icon} {priority_icon} {task['title']}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, task['id'])

            # Strike-through for completed tasks
            if task['status'] == 'completed':
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)

            self.tasks_list.addItem(item)

        # Update statistics
        self.update_statistics()

    def update_statistics(self):
        """Update task statistics"""
        all_tasks = self.tasks_model.get_tasks()
        total = len(all_tasks)
        completed = len([t for t in all_tasks if t['status'] == 'completed'])
        pending = len([t for t in all_tasks if t['status'] == 'pending'])
        in_progress = len([t for t in all_tasks if t['status'] == 'in_progress'])

        # Progress bar
        progress = int((completed / total * 100)) if total > 0 else 0
        self.progress_bar.setValue(progress)

        # Stats text
        self.stats_label.setText(
            f"Toplam: {total} | ✅ Tamamlandı: {completed} | "
            f"⏳ Bekliyor: {pending} | 🔄 Devam Ediyor: {in_progress}"
        )

    def on_task_selected(self, item):
        """Handle task selection"""
        task_id = item.data(Qt.UserRole)
        self.current_task_id = task_id

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()

        if row:
            task = dict(row)
            self.detail_title.setText(task['title'])

            # Meta information
            status_names = {
                'pending': 'Beklemede',
                'in_progress': 'Devam Ediyor',
                'completed': 'Tamamlandı',
                'cancelled': 'İptal Edildi'
            }
            priority_names = ["", "Düşük", "Orta", "Yüksek", "Acil"]

            meta_parts = [
                f"📁 {task['category']}",
                f"⭐ {priority_names[task['priority']]}",
                f"🔄 {status_names.get(task['status'], 'Bilinmiyor')}"
            ]

            if task['due_date']:
                due = datetime.fromisoformat(task['due_date'])
                meta_parts.append(f"📅 Termin: {due.strftime('%d.%m.%Y %H:%M')}")

            if task['estimated_minutes']:
                meta_parts.append(f"⏱️ Tahmini: {task['estimated_minutes']} dk")

            created = datetime.fromisoformat(task['created_at'])
            meta_parts.append(f"📝 Oluşturulma: {created.strftime('%d.%m.%Y')}")

            self.detail_meta.setText("\n".join(meta_parts))
            self.detail_description.setText(task['description'] or "Açıklama yok")

    def add_task(self):
        """Add a new task"""
        dialog = TaskDialog(self)
        if dialog.exec():
            task_data = dialog.get_task_data()

            if not task_data['title']:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir başlık girin!")
                return

            self.tasks_model.create_task(**task_data)
            self.load_tasks()
            QMessageBox.information(self, "Başarılı", "Görev başarıyla oluşturuldu!")

    def edit_task(self):
        """Edit selected task"""
        if not self.current_task_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir görev seçin!")
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (self.current_task_id,))
        row = cursor.fetchone()

        if row:
            task = dict(row)
            dialog = TaskDialog(self, task)

            if dialog.exec():
                task_data = dialog.get_task_data()

                if not task_data['title']:
                    QMessageBox.warning(self, "Uyarı", "Lütfen bir başlık girin!")
                    return

                # Update task
                cursor.execute('''
                    UPDATE tasks
                    SET title = ?, description = ?, category = ?,
                        priority = ?, status = ?, due_date = ?,
                        estimated_minutes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    task_data['title'], task_data['description'],
                    task_data['category'], task_data['priority'],
                    task_data['status'], task_data['due_date'],
                    task_data.get('estimated_minutes'), self.current_task_id
                ))

                conn.commit()
                self.load_tasks()
                QMessageBox.information(self, "Başarılı", "Görev başarıyla güncellendi!")

    def mark_complete(self):
        """Mark selected task as complete"""
        if not self.current_task_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir görev seçin!")
            return

        self.tasks_model.update_task_status(self.current_task_id, 'completed')
        self.load_tasks()
        QMessageBox.information(self, "Başarılı", "Görev tamamlandı olarak işaretlendi!")

    def delete_task(self):
        """Delete selected task"""
        if not self.current_task_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir görev seçin!")
            return

        reply = QMessageBox.question(
            self, "Onay", "Bu görevi silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM tasks WHERE id = ?', (self.current_task_id,))
            conn.commit()

            self.current_task_id = None
            self.load_tasks()
            self.detail_title.setText("Bir görev seçin...")
            self.detail_meta.setText("")
            self.detail_description.clear()
            QMessageBox.information(self, "Başarılı", "Görev başarıyla silindi!")

    def on_filter_changed(self):
        """Handle filter change"""
        status = self.filter_status.currentText()
        category = self.filter_category.currentText()

        self.load_tasks(
            status=status if status != "Tümü" else None,
            category=category if category != "Tümü" else None
        )

"""
Notes tab UI component
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QTextEdit, QListWidget, QListWidgetItem, QComboBox, QLabel,
    QDialog, QDialogButtonBox, QDateTimeEdit, QSpinBox, QMessageBox,
    QSplitter, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, QDateTime
from datetime import datetime, timedelta

from ..models.database import Database, NotesModel, RemindersModel


class NoteDialog(QDialog):
    """Dialog for creating/editing notes"""

    def __init__(self, parent=None, note_data=None):
        super().__init__(parent)
        self.note_data = note_data
        self.is_edit = note_data is not None

        self.setWindowTitle("Not Düzenle" if self.is_edit else "Yeni Not")
        self.setMinimumSize(500, 400)
        self.setup_ui()

        if self.is_edit:
            self.load_note_data()

    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Başlık:")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Not başlığı...")
        layout.addWidget(title_label)
        layout.addWidget(self.title_edit)

        # Content
        content_label = QLabel("İçerik:")
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Not içeriği...")
        layout.addWidget(content_label)
        layout.addWidget(self.content_edit)

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
        self.priority_combo.setCurrentIndex(1)  # Default: Orta
        meta_layout.addWidget(priority_label)
        meta_layout.addWidget(self.priority_combo)

        layout.addLayout(meta_layout)

        # Reminder section
        reminder_group = QGroupBox("Hatırlatma")
        reminder_layout = QFormLayout()

        self.reminder_enabled = QComboBox()
        self.reminder_enabled.addItems(["Hayır", "Evet"])
        reminder_layout.addRow("Hatırlatma Ekle:", self.reminder_enabled)

        self.reminder_datetime = QDateTimeEdit()
        self.reminder_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.reminder_datetime.setCalendarPopup(True)
        self.reminder_datetime.setDisplayFormat("dd.MM.yyyy HH:mm")
        reminder_layout.addRow("Tarih/Saat:", self.reminder_datetime)

        self.recurrence_combo = QComboBox()
        self.recurrence_combo.addItems([
            "Tekrar Yok", "Her Gün", "Her Hafta", "Her Ay"
        ])
        reminder_layout.addRow("Tekrar:", self.recurrence_combo)

        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def load_note_data(self):
        """Load existing note data into form"""
        if self.note_data:
            self.title_edit.setText(self.note_data.get('title', ''))
            self.content_edit.setText(self.note_data.get('content', ''))

            category = self.note_data.get('category', 'Genel')
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

            priority = self.note_data.get('priority', 2)
            self.priority_combo.setCurrentIndex(priority - 1)

    def get_note_data(self):
        """Get note data from form"""
        return {
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText().strip(),
            'category': self.category_combo.currentText(),
            'priority': self.priority_combo.currentIndex() + 1
        }

    def get_reminder_data(self):
        """Get reminder data from form"""
        if self.reminder_enabled.currentIndex() == 0:
            return None

        recurrence_map = {
            0: None,
            1: 'daily',
            2: 'weekly',
            3: 'monthly'
        }

        recurrence_type = recurrence_map[self.recurrence_combo.currentIndex()]

        return {
            'reminder_time': self.reminder_datetime.dateTime().toPython(),
            'recurrence_type': recurrence_type,
            'recurrence_interval': 1 if recurrence_type else None
        }


class NotesTab(QWidget):
    """Notes tab widget"""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.notes_model = NotesModel(db)
        self.reminders_model = RemindersModel(db)
        self.current_note_id = None

        self.setup_ui()
        self.load_notes()

    def setup_ui(self):
        """Setup tab UI"""
        layout = QHBoxLayout(self)

        # Splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Notes list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Search and filters
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Not ara...")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Tümü", "Genel", "İş", "Kişisel", "Alışveriş", "Sağlık", "Eğitim"
        ])
        self.filter_combo.currentTextChanged.connect(self.on_filter_changed)
        search_layout.addWidget(self.filter_combo)

        left_layout.addLayout(search_layout)

        # Notes list
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.on_note_selected)
        left_layout.addWidget(self.notes_list)

        # Buttons
        buttons_layout = QHBoxLayout()

        new_btn = QPushButton("➕ Yeni Not")
        new_btn.clicked.connect(self.add_note)
        buttons_layout.addWidget(new_btn)

        edit_btn = QPushButton("✏️ Düzenle")
        edit_btn.clicked.connect(self.edit_note)
        buttons_layout.addWidget(edit_btn)

        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.clicked.connect(self.delete_note)
        buttons_layout.addWidget(delete_btn)

        left_layout.addLayout(buttons_layout)

        splitter.addWidget(left_panel)

        # Right panel - Note details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.detail_title = QLabel("Bir not seçin...")
        self.detail_title.setWordWrap(True)
        font = self.detail_title.font()
        font.setPointSize(14)
        font.setBold(True)
        self.detail_title.setFont(font)
        right_layout.addWidget(self.detail_title)

        self.detail_meta = QLabel()
        right_layout.addWidget(self.detail_meta)

        self.detail_content = QTextEdit()
        self.detail_content.setReadOnly(True)
        right_layout.addWidget(self.detail_content)

        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def load_notes(self, category=None):
        """Load notes from database"""
        self.notes_list.clear()

        if category and category != "Tümü":
            notes = self.notes_model.get_all_notes(category=category)
        else:
            notes = self.notes_model.get_all_notes()

        priority_icons = {
            1: "🔵",  # Düşük
            2: "⚪",  # Orta
            3: "🟡",  # Yüksek
            4: "🔴"   # Acil
        }

        for note in notes:
            icon = priority_icons.get(note['priority'], "⚪")
            item_text = f"{icon} {note['title']} [{note['category']}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, note['id'])
            self.notes_list.addItem(item)

    def on_note_selected(self, item):
        """Handle note selection"""
        note_id = item.data(Qt.UserRole)
        self.current_note_id = note_id
        note = self.notes_model.get_note(note_id)

        if note:
            self.detail_title.setText(note['title'])

            # Meta information
            created = datetime.fromisoformat(note['created_at'])
            priority_names = ["", "Düşük", "Orta", "Yüksek", "Acil"]
            priority = priority_names[note['priority']]

            meta_text = (
                f"📁 Kategori: {note['category']} | "
                f"⭐ Öncelik: {priority} | "
                f"📅 Oluşturulma: {created.strftime('%d.%m.%Y %H:%M')}"
            )
            self.detail_meta.setText(meta_text)

            self.detail_content.setText(note['content'] or "")

    def add_note(self):
        """Add a new note"""
        dialog = NoteDialog(self)
        if dialog.exec():
            note_data = dialog.get_note_data()

            if not note_data['title']:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir başlık girin!")
                return

            # Create note
            note_id = self.notes_model.create_note(**note_data)

            # Create reminder if enabled
            reminder_data = dialog.get_reminder_data()
            if reminder_data:
                self.reminders_model.create_reminder(note_id, **reminder_data)

            # Reload notes
            self.load_notes()
            QMessageBox.information(self, "Başarılı", "Not başarıyla oluşturuldu!")

    def edit_note(self):
        """Edit selected note"""
        if not self.current_note_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir not seçin!")
            return

        note = self.notes_model.get_note(self.current_note_id)
        dialog = NoteDialog(self, note)

        if dialog.exec():
            note_data = dialog.get_note_data()

            if not note_data['title']:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir başlık girin!")
                return

            # Update note
            self.notes_model.update_note(self.current_note_id, **note_data)

            # Reload notes
            self.load_notes()
            QMessageBox.information(self, "Başarılı", "Not başarıyla güncellendi!")

    def delete_note(self):
        """Delete selected note"""
        if not self.current_note_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir not seçin!")
            return

        reply = QMessageBox.question(
            self, "Onay", "Bu notu silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.notes_model.delete_note(self.current_note_id)
            self.current_note_id = None
            self.load_notes()
            self.detail_title.setText("Bir not seçin...")
            self.detail_meta.setText("")
            self.detail_content.clear()
            QMessageBox.information(self, "Başarılı", "Not başarıyla silindi!")

    def on_search(self, text):
        """Handle search"""
        if not text.strip():
            self.load_notes()
            return

        self.notes_list.clear()
        results = self.notes_model.search_notes(text)

        priority_icons = {
            1: "🔵", 2: "⚪", 3: "🟡", 4: "🔴"
        }

        for note in results:
            icon = priority_icons.get(note['priority'], "⚪")
            item_text = f"{icon} {note['title']} [{note['category']}]"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, note['id'])
            self.notes_list.addItem(item)

    def on_filter_changed(self, category):
        """Handle category filter change"""
        self.load_notes(category if category != "Tümü" else None)

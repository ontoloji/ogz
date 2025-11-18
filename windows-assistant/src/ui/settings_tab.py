"""
Settings tab UI component
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QCheckBox, QSpinBox, QPushButton, QFormLayout,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
import json
from pathlib import Path

from ..models.database import Database, SettingsModel


class SettingsTab(QWidget):
    """Settings tab widget"""

    def __init__(self, db: Database, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.settings_model = SettingsModel(db)

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup tab UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Header
        header = QLabel("⚙️ Ayarlar")
        font = header.font()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Appearance settings
        appearance_group = QGroupBox("🎨 Görünüm")
        appearance_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Açık", "Koyu"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        appearance_layout.addRow("Tema:", self.theme_combo)

        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

        # Notification settings
        notification_group = QGroupBox("🔔 Bildirimler")
        notification_layout = QFormLayout()

        self.notification_enabled = QCheckBox()
        notification_layout.addRow("Bildirimleri Etkinleştir:", self.notification_enabled)

        self.notification_sound = QCheckBox()
        notification_layout.addRow("Bildirim Sesi:", self.notification_sound)

        notification_group.setLayout(notification_layout)
        layout.addWidget(notification_group)

        # Outlook settings
        outlook_group = QGroupBox("📅 Outlook Entegrasyonu")
        outlook_layout = QFormLayout()

        self.outlook_sync_enabled = QCheckBox()
        outlook_layout.addRow("Otomatik Senkronizasyon:", self.outlook_sync_enabled)

        self.outlook_sync_interval = QSpinBox()
        self.outlook_sync_interval.setRange(5, 120)
        self.outlook_sync_interval.setSuffix(" dakika")
        outlook_layout.addRow("Senkronizasyon Aralığı:", self.outlook_sync_interval)

        outlook_group.setLayout(outlook_layout)
        layout.addWidget(outlook_group)

        # Pomodoro settings
        pomodoro_group = QGroupBox("🍅 Pomodoro Ayarları")
        pomodoro_layout = QFormLayout()

        self.pomodoro_work_duration = QSpinBox()
        self.pomodoro_work_duration.setRange(1, 60)
        self.pomodoro_work_duration.setSuffix(" dakika")
        pomodoro_layout.addRow("Çalışma Süresi:", self.pomodoro_work_duration)

        self.pomodoro_short_break = QSpinBox()
        self.pomodoro_short_break.setRange(1, 30)
        self.pomodoro_short_break.setSuffix(" dakika")
        pomodoro_layout.addRow("Kısa Mola:", self.pomodoro_short_break)

        self.pomodoro_long_break = QSpinBox()
        self.pomodoro_long_break.setRange(5, 60)
        self.pomodoro_long_break.setSuffix(" dakika")
        pomodoro_layout.addRow("Uzun Mola:", self.pomodoro_long_break)

        self.pomodoro_sessions_until_long_break = QSpinBox()
        self.pomodoro_sessions_until_long_break.setRange(2, 10)
        self.pomodoro_sessions_until_long_break.setSuffix(" oturum")
        pomodoro_layout.addRow("Uzun Molaya Kadar:", self.pomodoro_sessions_until_long_break)

        pomodoro_group.setLayout(pomodoro_layout)
        layout.addWidget(pomodoro_group)

        # Startup settings
        startup_group = QGroupBox("🚀 Başlangıç")
        startup_layout = QFormLayout()

        self.start_with_windows = QCheckBox()
        startup_layout.addRow("Windows ile Başlat:", self.start_with_windows)

        self.minimize_to_tray = QCheckBox()
        startup_layout.addRow("Sistem Tepsisine Küçült:", self.minimize_to_tray)

        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)

        # Data management
        data_group = QGroupBox("💾 Veri Yönetimi")
        data_layout = QVBoxLayout()

        backup_btn_layout = QHBoxLayout()

        backup_btn = QPushButton("📤 Verileri Dışa Aktar")
        backup_btn.clicked.connect(self.export_data)
        backup_btn_layout.addWidget(backup_btn)

        restore_btn = QPushButton("📥 Verileri İçe Aktar")
        restore_btn.clicked.connect(self.import_data)
        backup_btn_layout.addWidget(restore_btn)

        data_layout.addLayout(backup_btn_layout)

        clear_btn = QPushButton("🗑️ Tüm Verileri Temizle")
        clear_btn.clicked.connect(self.clear_data)
        clear_btn.setStyleSheet("background-color: #e74c3c;")
        data_layout.addWidget(clear_btn)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Save button
        save_btn = QPushButton("💾 Ayarları Kaydet")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #27ae60; font-size: 12pt; padding: 10px;")
        layout.addWidget(save_btn)

        layout.addStretch()

    def load_settings(self):
        """Load settings from database"""
        # Theme
        theme = self.settings_model.get_setting('theme', 'light')
        self.theme_combo.setCurrentText("Koyu" if theme == 'dark' else "Açık")

        # Notifications
        self.notification_enabled.setChecked(
            self.settings_model.get_setting('notification_enabled', True)
        )
        self.notification_sound.setChecked(
            self.settings_model.get_setting('notification_sound', True)
        )

        # Outlook
        self.outlook_sync_enabled.setChecked(
            self.settings_model.get_setting('outlook_sync_enabled', False)
        )
        self.outlook_sync_interval.setValue(
            self.settings_model.get_setting('outlook_sync_interval', 30)
        )

        # Pomodoro
        self.pomodoro_work_duration.setValue(
            self.settings_model.get_setting('pomodoro_work_duration', 25)
        )
        self.pomodoro_short_break.setValue(
            self.settings_model.get_setting('pomodoro_short_break', 5)
        )
        self.pomodoro_long_break.setValue(
            self.settings_model.get_setting('pomodoro_long_break', 15)
        )
        self.pomodoro_sessions_until_long_break.setValue(
            self.settings_model.get_setting('pomodoro_sessions_until_long_break', 4)
        )

        # Startup
        self.start_with_windows.setChecked(
            self.settings_model.get_setting('start_with_windows', False)
        )
        self.minimize_to_tray.setChecked(
            self.settings_model.get_setting('minimize_to_tray', True)
        )

    def save_settings(self):
        """Save settings to database"""
        # Theme
        theme = 'dark' if self.theme_combo.currentText() == "Koyu" else 'light'
        self.settings_model.set_setting('theme', theme)

        # Notifications
        self.settings_model.set_setting(
            'notification_enabled', self.notification_enabled.isChecked()
        )
        self.settings_model.set_setting(
            'notification_sound', self.notification_sound.isChecked()
        )

        # Outlook
        self.settings_model.set_setting(
            'outlook_sync_enabled', self.outlook_sync_enabled.isChecked()
        )
        self.settings_model.set_setting(
            'outlook_sync_interval', self.outlook_sync_interval.value()
        )

        # Pomodoro
        self.settings_model.set_setting(
            'pomodoro_work_duration', self.pomodoro_work_duration.value()
        )
        self.settings_model.set_setting(
            'pomodoro_short_break', self.pomodoro_short_break.value()
        )
        self.settings_model.set_setting(
            'pomodoro_long_break', self.pomodoro_long_break.value()
        )
        self.settings_model.set_setting(
            'pomodoro_sessions_until_long_break',
            self.pomodoro_sessions_until_long_break.value()
        )

        # Startup
        self.settings_model.set_setting(
            'start_with_windows', self.start_with_windows.isChecked()
        )
        self.settings_model.set_setting(
            'minimize_to_tray', self.minimize_to_tray.isChecked()
        )

        QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!")

    def on_theme_changed(self, text):
        """Handle theme change"""
        theme = 'dark' if text == "Koyu" else 'light'
        self.main_window.apply_theme(theme)

    def export_data(self):
        """Export data to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Verileri Dışa Aktar",
            "assistant_backup.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            from ..models.database import NotesModel, TasksModel

            notes_model = NotesModel(self.db)
            tasks_model = TasksModel(self.db)

            data = {
                'notes': notes_model.get_all_notes(limit=10000),
                'tasks': tasks_model.get_tasks(),
                'settings': self.settings_model.get_all_settings(),
                'export_date': datetime.now().isoformat()
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            QMessageBox.information(
                self, "Başarılı",
                f"Veriler başarıyla dışa aktarıldı!\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma hatası: {e}")

    def import_data(self):
        """Import data from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Verileri İçe Aktar",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        reply = QMessageBox.question(
            self, "Onay",
            "Mevcut veriler silinecek ve yedekten geri yüklenecek. Devam etmek istiyor musunuz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            from ..models.database import NotesModel, TasksModel

            notes_model = NotesModel(self.db)
            tasks_model = TasksModel(self.db)

            # Import notes
            for note in data.get('notes', []):
                notes_model.create_note(
                    title=note['title'],
                    content=note.get('content', ''),
                    category=note.get('category', 'Genel'),
                    priority=note.get('priority', 2)
                )

            # Import tasks
            for task in data.get('tasks', []):
                tasks_model.create_task(
                    title=task['title'],
                    description=task.get('description', ''),
                    category=task.get('category', 'Genel'),
                    priority=task.get('priority', 2)
                )

            # Import settings
            for key, value in data.get('settings', {}).items():
                self.settings_model.set_setting(key, value)

            QMessageBox.information(
                self, "Başarılı",
                "Veriler başarıyla içe aktarıldı!"
            )

            # Reload settings
            self.load_settings()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma hatası: {e}")

    def clear_data(self):
        """Clear all application data"""
        reply = QMessageBox.question(
            self, "Onay",
            "TÜM VERİLER SİLİNECEK! Bu işlem geri alınamaz.\n\n"
            "Devam etmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Clear all tables
            tables = [
                'notes', 'reminders', 'tasks', 'calendar_events',
                'pomodoro_sessions', 'notification_history'
            ]

            for table in tables:
                cursor.execute(f'DELETE FROM {table}')

            conn.commit()

            QMessageBox.information(
                self, "Başarılı",
                "Tüm veriler temizlendi!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Temizleme hatası: {e}")


from datetime import datetime

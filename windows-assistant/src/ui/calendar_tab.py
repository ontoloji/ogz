"""
Calendar tab UI component - Outlook integration
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from datetime import datetime

from ..models.database import Database
from ..services.outlook_service import OutlookService


class CalendarTab(QWidget):
    """Calendar/Outlook integration tab widget"""

    def __init__(self, db: Database, outlook_service: OutlookService):
        super().__init__()
        self.db = db
        self.outlook = outlook_service

        self.setup_ui()
        self.load_events()

    def setup_ui(self):
        """Setup tab UI"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("📅 Takvim ve Outlook Entegrasyonu")
        font = header.font()
        font.setPointSize(14)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)

        # Authentication status
        status_group = QGroupBox("Bağlantı Durumu")
        status_layout = QVBoxLayout()

        self.status_label = QLabel()
        self.update_status()
        status_layout.addWidget(self.status_label)

        auth_btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("🔗 Outlook'a Bağlan")
        self.connect_btn.clicked.connect(self.connect_outlook)
        auth_btn_layout.addWidget(self.connect_btn)

        self.sync_btn = QPushButton("🔄 Senkronize Et")
        self.sync_btn.clicked.connect(self.sync_events)
        self.sync_btn.setEnabled(self.outlook.is_authenticated)
        auth_btn_layout.addWidget(self.sync_btn)

        status_layout.addLayout(auth_btn_layout)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Events list
        events_label = QLabel("Yaklaşan Etkinlikler:")
        layout.addWidget(events_label)

        self.events_list = QListWidget()
        self.events_list.itemClicked.connect(self.on_event_selected)
        layout.addWidget(self.events_list)

        # Event details
        details_label = QLabel("Etkinlik Detayları:")
        layout.addWidget(details_label)

        self.event_details = QTextEdit()
        self.event_details.setReadOnly(True)
        self.event_details.setMaximumHeight(150)
        layout.addWidget(self.event_details)

        # Instructions
        info_text = """
        ℹ️ Outlook Entegrasyonu Hakkında:

        Bu özellik Microsoft Outlook takviminizdeki etkinlikleri görüntülemenizi sağlar.
        Outlook'a bağlanmak için:

        1. Azure AD'de bir uygulama kaydedin (https://portal.azure.com)
        2. Client ID ve Client Secret alın
        3. Gerekli izinleri verin (Calendars.Read)
        4. "Outlook'a Bağlan" butonuna tıklayın

        Not: Şu anda bu özellik demo modundadır. Gerçek entegrasyon için
        yukarıdaki adımları tamamlamanız gerekmektedir.
        """

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 10pt;")
        layout.addWidget(info_label)

    def update_status(self):
        """Update connection status"""
        if self.outlook.is_authenticated:
            self.status_label.setText("✅ Outlook'a bağlı")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("❌ Outlook'a bağlı değil")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def connect_outlook(self):
        """Connect to Outlook"""
        QMessageBox.information(
            self,
            "Outlook Entegrasyonu",
            "Outlook entegrasyonu için Azure AD uygulama kaydı gereklidir.\n\n"
            "Detaylar için lütfen README.md dosyasındaki Outlook Entegrasyonu "
            "bölümüne bakın.\n\n"
            "Demo amaçlı bu butona tıklanması bağlantıyı simüle edecektir."
        )

        # For demo purposes, mark as authenticated
        # In real implementation, this would trigger OAuth flow
        self.outlook.is_authenticated = True
        self.update_status()
        self.sync_btn.setEnabled(True)

    def sync_events(self):
        """Sync calendar events from Outlook"""
        if not self.outlook.is_authenticated:
            QMessageBox.warning(
                self,
                "Uyarı",
                "Önce Outlook'a bağlanmanız gerekiyor!"
            )
            return

        # Sync events
        count = self.outlook.sync_calendar_events(days_ahead=7)

        if count > 0:
            QMessageBox.information(
                self,
                "Başarılı",
                f"{count} etkinlik senkronize edildi!"
            )
            self.load_events()
        else:
            QMessageBox.information(
                self,
                "Bilgi",
                "Senkronize edilecek yeni etkinlik bulunamadı.\n"
                "(Demo modunda çalışıyorsunuz)"
            )

    def load_events(self):
        """Load events from database"""
        self.events_list.clear()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        now = datetime.now().isoformat()
        cursor.execute('''
            SELECT * FROM calendar_events
            WHERE start_time >= ?
            ORDER BY start_time ASC
            LIMIT 50
        ''', (now,))

        for row in cursor.fetchall():
            event = dict(row)
            start_time = datetime.fromisoformat(event['start_time'])

            item_text = f"{start_time.strftime('%d.%m %H:%M')} - {event['subject']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, event['id'])
            self.events_list.addItem(item)

        if self.events_list.count() == 0:
            item = QListWidgetItem("Yaklaşan etkinlik bulunamadı")
            item.setFlags(Qt.NoItemFlags)
            self.events_list.addItem(item)

    def on_event_selected(self, item):
        """Handle event selection"""
        event_id = item.data(Qt.UserRole)
        if not event_id:
            return

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM calendar_events WHERE id = ?', (event_id,))
        row = cursor.fetchone()

        if row:
            event = dict(row)

            start_time = datetime.fromisoformat(event['start_time'])
            end_time = datetime.fromisoformat(event['end_time'])

            details = f"""
📋 Konu: {event['subject']}

📅 Başlangıç: {start_time.strftime('%d %B %Y, %H:%M')}
📅 Bitiş: {end_time.strftime('%d %B %Y, %H:%M')}

📍 Yer: {event['location'] or 'Belirtilmemiş'}

👤 Düzenleyen: {event['organizer'] or 'Bilinmiyor'}

👥 Katılımcılar: {event['attendees'] or 'Belirtilmemiş'}

📝 Açıklama:
{event['description'] or 'Açıklama yok'}
            """

            self.event_details.setText(details.strip())

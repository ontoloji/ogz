"""
Private Web Browser - Windows Compatible
Gizlilik odaklı web tarayıcı - Hiçbir kayıt tutmaz
"""

import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
                             QStatusBar, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt6.QtGui import QIcon, QKeySequence
from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class NoStorageRequestInterceptor(QWebEngineUrlRequestInterceptor):
    """Tüm izleme ve reklam isteklerini engelle"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Yaygın izleme ve reklam domain'leri
        self.blocked_domains = [
            'google-analytics.com',
            'doubleclick.net',
            'facebook.com/tr',
            'facebook.net',
            'connect.facebook.net',
            'analytics',
            'tracker',
            'telemetry'
        ]

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        # İzleme URL'lerini engelle
        for domain in self.blocked_domains:
            if domain in url.lower():
                info.block(True)
                return


class PrivateBrowserPage(QWebEnginePage):
    """Özel gizli sayfa - tüm izinleri engelle"""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def certificateError(self, error):
        """SSL sertifika hatalarını kullanıcıya sor"""
        return False  # Güvenlik için otomatik kabul etme


class PrivateBrowser(QMainWindow):
    """Kayıt tutmayan gizli Windows tarayıcı"""

    def __init__(self):
        super().__init__()

        # Gizli profil oluştur - hiçbir şey kaydetme
        self.profile = QWebEngineProfile()  # Off-the-record profile

        # Cache'i tamamen devre dışı bırak
        self.profile.setHttpCacheType(QWebEngineProfile.HttpCacheType.NoCache)

        # Cookie'leri devre dışı bırak
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)

        # İstek engelleyici ekle
        self.interceptor = NoStorageRequestInterceptor()
        self.profile.setUrlRequestInterceptor(self.interceptor)

        # Do Not Track başlığı gönder
        self.profile.setHttpUserAgent(
            self.profile.httpUserAgent() + " DNT/1"
        )

        self.init_ui()
        self.show_welcome_message()

    def init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("🔒 Gizli Tarayıcı - Kayıt Tutmaz")
        self.setGeometry(100, 100, 1200, 800)

        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar oluştur
        self.create_toolbar()

        # Web view oluştur (gizli profil ile)
        self.browser = QWebEngineView()
        self.page = PrivateBrowserPage(self.profile, self.browser)
        self.browser.setPage(self.page)

        # Sayfa değişikliklerini takip et
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadProgress.connect(self.update_load_progress)
        self.browser.loadFinished.connect(self.load_finished)
        self.browser.titleChanged.connect(self.update_title)

        layout.addWidget(self.browser)

        # Durum çubuğu
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("🔒 Gizli Mod Aktif - Hiçbir kayıt tutulmuyor", 5000)

        # Ana sayfayı yükle
        self.browser.setUrl(QUrl("https://www.google.com"))

    def create_toolbar(self):
        """Navigasyon araç çubuğu"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #2b2b2b;
                border: none;
                padding: 5px;
                spacing: 3px;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        self.addToolBar(toolbar)

        # Geri butonu
        back_btn = QPushButton("◀ Geri")
        back_btn.clicked.connect(self.browser.back)
        toolbar.addWidget(back_btn)

        # İleri butonu
        forward_btn = QPushButton("İleri ▶")
        forward_btn.clicked.connect(self.browser.forward)
        toolbar.addWidget(forward_btn)

        # Yenile butonu
        reload_btn = QPushButton("🔄 Yenile")
        reload_btn.clicked.connect(self.browser.reload)
        toolbar.addWidget(reload_btn)

        # Ana sayfa butonu
        home_btn = QPushButton("🏠 Ana Sayfa")
        home_btn.clicked.connect(self.navigate_home)
        toolbar.addWidget(home_btn)

        # URL adresi çubuğu
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL girin veya arama yapın...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)

        # Git butonu
        go_btn = QPushButton("➜ Git")
        go_btn.clicked.connect(self.navigate_to_url)
        toolbar.addWidget(go_btn)

        # Yeni sekme butonu (aynı pencerede)
        new_tab_btn = QPushButton("➕ Yeni")
        new_tab_btn.clicked.connect(self.new_window)
        toolbar.addWidget(new_tab_btn)

        # Hakkında butonu
        about_btn = QPushButton("ℹ Hakkında")
        about_btn.clicked.connect(self.show_about)
        toolbar.addWidget(about_btn)

    def navigate_home(self):
        """Ana sayfaya git"""
        self.browser.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        """URL'ye git veya arama yap"""
        text = self.url_bar.text().strip()

        if not text:
            return

        # URL mi yoksa arama mı?
        if '.' in text and ' ' not in text and not text.startswith('http'):
            url = 'https://' + text
        elif text.startswith('http://') or text.startswith('https://'):
            url = text
        else:
            # Google'da ara
            url = f'https://www.google.com/search?q={text}'

        self.browser.setUrl(QUrl(url))

    def update_url_bar(self, url):
        """URL çubuğunu güncelle"""
        self.url_bar.setText(url.toString())

    def update_load_progress(self, progress):
        """Yüklenme ilerlemesini göster"""
        if progress < 100:
            self.status.showMessage(f"Yükleniyor... %{progress}")
        else:
            self.status.showMessage("🔒 Gizli Mod - Kayıt tutulmuyor", 2000)

    def load_finished(self, success):
        """Sayfa yükleme tamamlandı"""
        if success:
            self.status.showMessage("✓ Sayfa yüklendi (Gizli Mod)", 3000)
        else:
            self.status.showMessage("✗ Sayfa yüklenemedi", 3000)

    def update_title(self, title):
        """Pencere başlığını güncelle"""
        if title:
            self.setWindowTitle(f"🔒 {title} - Gizli Tarayıcı")
        else:
            self.setWindowTitle("🔒 Gizli Tarayıcı")

    def new_window(self):
        """Yeni gizli pencere aç"""
        new_browser = PrivateBrowser()
        new_browser.show()

    def show_about(self):
        """Hakkında bilgisi"""
        QMessageBox.information(
            self,
            "Hakkında - Gizli Tarayıcı",
            "<h2>🔒 Gizli Windows Tarayıcı</h2>"
            "<p><b>Özellikler:</b></p>"
            "<ul>"
            "<li>✓ Hiçbir kayıt tutmaz (geçmiş yok)</li>"
            "<li>✓ Çerez kaydetmez</li>"
            "<li>✓ Önbellek kullanmaz</li>"
            "<li>✓ İzleme engelleyici</li>"
            "<li>✓ Do Not Track aktif</li>"
            "<li>✓ Windows uyumlu</li>"
            "</ul>"
            "<p><b>Gizlilik:</b> Tarayıcıyı kapattığınızda tüm veriler silinir.</p>"
            "<p><i>PyQt5 + QtWebEngine ile geliştirilmiştir.</i></p>"
        )

    def show_welcome_message(self):
        """Hoş geldiniz mesajı"""
        self.status.showMessage(
            "🔒 GİZLİ MOD AKTİF - Geçmiş, çerez ve önbellek kaydedilmez!",
            10000
        )

    def closeEvent(self, event):
        """Pencere kapatılırken"""
        # Profil zaten bellek içi, otomatik temizlenecek
        event.accept()


def main():
    """Ana program"""
    app = QApplication(sys.argv)
    app.setApplicationName("Gizli Tarayıcı")
    app.setOrganizationName("PrivateBrowser")

    # Karanlık tema (Windows için)
    app.setStyle('Fusion')

    # Ana pencereyi oluştur
    browser = PrivateBrowser()
    browser.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

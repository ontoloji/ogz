"""
Multi-AI Question Tool
Windows GUI uygulaması - Birden fazla yapay zekaya soru sor
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QTextEdit, QPushButton, QCheckBox,
    QMessageBox, QScrollArea, QFrame, QFileDialog, QLineEdit,
    QGridLayout, QTabWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from ai_providers import AIProviderManager


class QuestionWorker(QThread):
    """
    Arka planda AI'lara soru sormak için worker thread
    """
    finished = pyqtSignal(dict)  # Sonuçlar
    progress = pyqtSignal(str, str)  # Provider adı, mesaj
    error = pyqtSignal(str)  # Hata mesajı

    def __init__(self, provider_manager: AIProviderManager, question: str, selected_providers: list):
        super().__init__()
        self.provider_manager = provider_manager
        self.question = question
        self.selected_providers = selected_providers

    def run(self):
        """Thread'i çalıştır"""
        try:
            results = {}

            # Her provider için paralel olarak soru sor
            with ThreadPoolExecutor(max_workers=len(self.selected_providers)) as executor:
                futures = {}

                for provider_name in self.selected_providers:
                    if provider_name in self.provider_manager.providers:
                        provider = self.provider_manager.providers[provider_name]
                        if provider.is_available():
                            self.progress.emit(provider.get_provider_name(), "Soru soruluyor...")
                            future = executor.submit(provider.ask_question, self.question)
                            futures[future] = provider

                # Sonuçları topla
                for future in as_completed(futures):
                    provider = futures[future]
                    try:
                        answer = future.result()
                        results[provider.get_provider_name()] = answer
                        self.progress.emit(provider.get_provider_name(), "Cevap alındı ✓")
                    except Exception as e:
                        error_msg = f"❌ HATA: {str(e)}"
                        results[provider.get_provider_name()] = error_msg
                        self.progress.emit(provider.get_provider_name(), error_msg)

            self.finished.emit(results)

        except Exception as e:
            self.error.emit(f"İşlem hatası: {str(e)}")


class SettingsWindow(QWidget):
    """API Key ayarları penceresi"""

    def __init__(self, config_path: str):
        super().__init__()
        self.config_path = config_path
        self.config = self.load_config()

        self.init_ui()

    def load_config(self) -> dict:
        """Konfigürasyonu yükle"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config yükleme hatası: {e}")
            return self.get_default_config()

    def get_default_config(self) -> dict:
        """Varsayılan konfigürasyon"""
        return {
            "openai": {
                "enabled": False,
                "api_key": "",
                "model": "gpt-4"
            },
            "anthropic": {
                "enabled": False,
                "api_key": "",
                "model": "claude-3-5-sonnet-20241022"
            },
            "google": {
                "enabled": False,
                "api_key": "",
                "model": "gemini-pro"
            },
            "cohere": {
                "enabled": False,
                "api_key": "",
                "model": "command"
            }
        }

    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("API Key Ayarları")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        # OpenAI
        openai_group = QGroupBox("OpenAI")
        openai_layout = QGridLayout()

        self.openai_enabled = QCheckBox("Etkin")
        self.openai_enabled.setChecked(self.config.get('openai', {}).get('enabled', False))
        openai_layout.addWidget(self.openai_enabled, 0, 0)

        openai_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.openai_key = QLineEdit(self.config.get('openai', {}).get('api_key', ''))
        self.openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        openai_layout.addWidget(self.openai_key, 1, 1)

        openai_layout.addWidget(QLabel("Model:"), 2, 0)
        self.openai_model = QLineEdit(self.config.get('openai', {}).get('model', 'gpt-4'))
        openai_layout.addWidget(self.openai_model, 2, 1)

        openai_group.setLayout(openai_layout)
        layout.addWidget(openai_group)

        # Anthropic
        anthropic_group = QGroupBox("Anthropic Claude")
        anthropic_layout = QGridLayout()

        self.anthropic_enabled = QCheckBox("Etkin")
        self.anthropic_enabled.setChecked(self.config.get('anthropic', {}).get('enabled', False))
        anthropic_layout.addWidget(self.anthropic_enabled, 0, 0)

        anthropic_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.anthropic_key = QLineEdit(self.config.get('anthropic', {}).get('api_key', ''))
        self.anthropic_key.setEchoMode(QLineEdit.EchoMode.Password)
        anthropic_layout.addWidget(self.anthropic_key, 1, 1)

        anthropic_layout.addWidget(QLabel("Model:"), 2, 0)
        self.anthropic_model = QLineEdit(self.config.get('anthropic', {}).get('model', 'claude-3-5-sonnet-20241022'))
        anthropic_layout.addWidget(self.anthropic_model, 2, 1)

        anthropic_group.setLayout(anthropic_layout)
        layout.addWidget(anthropic_group)

        # Google Gemini
        google_group = QGroupBox("Google Gemini")
        google_layout = QGridLayout()

        self.google_enabled = QCheckBox("Etkin")
        self.google_enabled.setChecked(self.config.get('google', {}).get('enabled', False))
        google_layout.addWidget(self.google_enabled, 0, 0)

        google_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.google_key = QLineEdit(self.config.get('google', {}).get('api_key', ''))
        self.google_key.setEchoMode(QLineEdit.EchoMode.Password)
        google_layout.addWidget(self.google_key, 1, 1)

        google_layout.addWidget(QLabel("Model:"), 2, 0)
        self.google_model = QLineEdit(self.config.get('google', {}).get('model', 'gemini-pro'))
        google_layout.addWidget(self.google_model, 2, 1)

        google_group.setLayout(google_layout)
        layout.addWidget(google_group)

        # Cohere
        cohere_group = QGroupBox("Cohere (Opsiyonel)")
        cohere_layout = QGridLayout()

        self.cohere_enabled = QCheckBox("Etkin")
        self.cohere_enabled.setChecked(self.config.get('cohere', {}).get('enabled', False))
        cohere_layout.addWidget(self.cohere_enabled, 0, 0)

        cohere_layout.addWidget(QLabel("API Key:"), 1, 0)
        self.cohere_key = QLineEdit(self.config.get('cohere', {}).get('api_key', ''))
        self.cohere_key.setEchoMode(QLineEdit.EchoMode.Password)
        cohere_layout.addWidget(self.cohere_key, 1, 1)

        cohere_layout.addWidget(QLabel("Model:"), 2, 0)
        self.cohere_model = QLineEdit(self.config.get('cohere', {}).get('model', 'command'))
        cohere_layout.addWidget(self.cohere_model, 2, 1)

        cohere_group.setLayout(cohere_layout)
        layout.addWidget(cohere_group)

        # Butonlar
        btn_layout = QHBoxLayout()

        btn_save = QPushButton("Kaydet")
        btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(btn_save)

        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def save_settings(self):
        """Ayarları kaydet"""
        self.config = {
            "openai": {
                "enabled": self.openai_enabled.isChecked(),
                "api_key": self.openai_key.text(),
                "model": self.openai_model.text()
            },
            "anthropic": {
                "enabled": self.anthropic_enabled.isChecked(),
                "api_key": self.anthropic_key.text(),
                "model": self.anthropic_model.text()
            },
            "google": {
                "enabled": self.google_enabled.isChecked(),
                "api_key": self.google_key.text(),
                "model": self.google_model.text()
            },
            "cohere": {
                "enabled": self.cohere_enabled.isChecked(),
                "api_key": self.cohere_key.text(),
                "model": self.cohere_model.text()
            }
        }

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!\n\nUygulamayı yeniden başlatın.")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilemedi: {e}")


class MainWindow(QMainWindow):
    """Ana pencere"""

    def __init__(self):
        super().__init__()

        self.config_path = Path(__file__).parent / "config_ai.json"
        self.ensure_config_exists()

        self.provider_manager = None
        self.question_worker = None
        self.settings_window = None

        self.init_ui()
        self.load_providers()

        self.logger = logging.getLogger(__name__)

    def ensure_config_exists(self):
        """Config dosyasının var olduğundan emin ol"""
        if not self.config_path.exists():
            default_config = {
                "openai": {
                    "enabled": False,
                    "api_key": "",
                    "model": "gpt-4"
                },
                "anthropic": {
                    "enabled": False,
                    "api_key": "",
                    "model": "claude-3-5-sonnet-20241022"
                },
                "google": {
                    "enabled": False,
                    "api_key": "",
                    "model": "gemini-pro"
                },
                "cohere": {
                    "enabled": False,
                    "api_key": "",
                    "model": "command"
                }
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)

    def load_providers(self):
        """Provider'ları yükle"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.provider_manager = AIProviderManager(config)
            self.update_provider_checkboxes()

        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Provider yükleme hatası: {e}")

    def update_provider_checkboxes(self):
        """Provider checkbox'larını güncelle"""
        if not self.provider_manager:
            return

        # Tüm checkbox'ları temizle
        for cb in [self.cb_openai, self.cb_anthropic, self.cb_google, self.cb_cohere]:
            cb.setChecked(False)
            cb.setEnabled(False)

        # Kullanılabilir provider'ları etkinleştir
        available = self.provider_manager.get_available_providers()

        for provider_name, provider in available.items():
            if provider_name == 'openai':
                self.cb_openai.setEnabled(True)
                self.cb_openai.setChecked(True)
            elif provider_name == 'anthropic':
                self.cb_anthropic.setEnabled(True)
                self.cb_anthropic.setChecked(True)
            elif provider_name == 'google':
                self.cb_google.setEnabled(True)
                self.cb_google.setChecked(True)
            elif provider_name == 'cohere':
                self.cb_cohere.setEnabled(True)
                self.cb_cohere.setChecked(True)

    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("Multi-AI Question Tool")
        self.setGeometry(100, 100, 1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Başlık
        title = QLabel("🤖 Multi-AI Question Tool")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Soru paneli
        question_group = QGroupBox("Soru")
        question_layout = QVBoxLayout()

        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Sorunuzu buraya yazın...")
        self.question_input.setMaximumHeight(150)
        self.question_input.setFont(QFont("Segoe UI", 10))
        question_layout.addWidget(self.question_input)

        question_group.setLayout(question_layout)
        main_layout.addWidget(question_group)

        # AI seçimi paneli
        ai_selection_group = QGroupBox("AI Seçimi")
        ai_layout = QHBoxLayout()

        self.cb_openai = QCheckBox("OpenAI GPT")
        self.cb_anthropic = QCheckBox("Anthropic Claude")
        self.cb_google = QCheckBox("Google Gemini")
        self.cb_cohere = QCheckBox("Cohere")

        for cb in [self.cb_openai, self.cb_anthropic, self.cb_google, self.cb_cohere]:
            cb.setEnabled(False)
            ai_layout.addWidget(cb)

        ai_selection_group.setLayout(ai_layout)
        main_layout.addWidget(ai_selection_group)

        # Kontrol butonları
        btn_layout = QHBoxLayout()

        self.btn_ask = QPushButton("Soruyu Gönder")
        self.btn_ask.clicked.connect(self.ask_question)
        self.btn_ask.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        btn_layout.addWidget(self.btn_ask)

        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.clicked.connect(self.clear_results)
        btn_layout.addWidget(self.btn_clear)

        self.btn_save = QPushButton("Cevapları Kaydet")
        self.btn_save.clicked.connect(self.save_results)
        btn_layout.addWidget(self.btn_save)

        self.btn_settings = QPushButton("⚙️ API Key Ayarları")
        self.btn_settings.clicked.connect(self.open_settings)
        btn_layout.addWidget(self.btn_settings)

        main_layout.addLayout(btn_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # Cevaplar paneli
        results_group = QGroupBox("Cevaplar")
        results_layout = QVBoxLayout()

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        self.results_area.setFont(QFont("Segoe UI", 10))
        results_layout.addWidget(self.results_area)

        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Durum çubuğu
        self.statusBar().showMessage("Hazır")

    def open_settings(self):
        """Ayarlar penceresini aç"""
        self.settings_window = SettingsWindow(str(self.config_path))
        self.settings_window.show()

    def ask_question(self):
        """Soruyu tüm seçili AI'lara sor"""
        question = self.question_input.toPlainText().strip()

        if not question:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir soru yazın!")
            return

        # Seçili provider'ları bul
        selected_providers = []
        if self.cb_openai.isChecked():
            selected_providers.append('openai')
        if self.cb_anthropic.isChecked():
            selected_providers.append('anthropic')
        if self.cb_google.isChecked():
            selected_providers.append('google')
        if self.cb_cohere.isChecked():
            selected_providers.append('cohere')

        if not selected_providers:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir AI seçin!")
            return

        # UI'yi devre dışı bırak
        self.btn_ask.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.results_area.clear()
        self.statusBar().showMessage("Sorular gönderiliyor...")

        # Worker thread başlat
        self.question_worker = QuestionWorker(self.provider_manager, question, selected_providers)
        self.question_worker.finished.connect(self.on_question_finished)
        self.question_worker.progress.connect(self.on_question_progress)
        self.question_worker.error.connect(self.on_question_error)
        self.question_worker.start()

    def on_question_progress(self, provider_name: str, message: str):
        """Soru ilerlemesi"""
        self.statusBar().showMessage(f"{provider_name}: {message}")

    def on_question_finished(self, results: Dict[str, str]):
        """Sorular tamamlandı"""
        self.btn_ask.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Tamamlandı!")

        # Sonuçları göster
        self.display_results(results)

    def on_question_error(self, error_msg: str):
        """Hata oluştu"""
        self.btn_ask.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Hata!")

        QMessageBox.critical(self, "Hata", error_msg)

    def display_results(self, results: Dict[str, str]):
        """Sonuçları göster"""
        output = []
        output.append("=" * 80)
        output.append(f"SORU: {self.question_input.toPlainText().strip()}")
        output.append("=" * 80)
        output.append("")

        for provider_name, answer in results.items():
            output.append("─" * 80)
            output.append(f"🤖 {provider_name}")
            output.append("─" * 80)
            output.append(answer)
            output.append("")

        self.results_area.setPlainText("\n".join(output))

    def clear_results(self):
        """Sonuçları temizle"""
        self.question_input.clear()
        self.results_area.clear()
        self.statusBar().showMessage("Temizlendi")

    def save_results(self):
        """Sonuçları dosyaya kaydet"""
        if not self.results_area.toPlainText():
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek sonuç yok!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"multi_ai_results_{timestamp}.txt"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sonuçları Kaydet",
            default_filename,
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_area.toPlainText())

                QMessageBox.information(self, "Başarılı", f"Sonuçlar kaydedildi:\n{filename}")
                self.statusBar().showMessage(f"Kaydedildi: {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydetme hatası: {e}")


def setup_logging():
    """Logging yapılandırması"""
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"multi_ai_tool_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """Ana fonksiyon"""
    setup_logging()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

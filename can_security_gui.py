"""
CAN Bus Siber Güvenlik Test Arayüzü
Kvaser Memorator 2xHS - GUI

⚠️ UYARI: Bu yazılım SADECE yetkili güvenlik testleri, araştırma ve eğitim amaçlı kullanılmalıdır.
⚠️ WARNING: This software is ONLY for authorized security testing, research, and educational purposes.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QTextEdit, QGroupBox, QGridLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog, QLineEdit
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

from can_security_attacks import (
    CANSecurityTester, MockCANSecurityTester,
    AttackType, AttackConfig, CANLIB_AVAILABLE
)

try:
    from canlib import Frame
except ImportError:
    Frame = None


class SignalEmitter(QObject):
    """Thread-safe sinyal gönderimi için yardımcı sınıf"""
    status_update = pyqtSignal(str, dict)
    message_received = pyqtSignal(object)
    log_message = pyqtSignal(str, str)  # level, message


class CANSecurityGUI(QMainWindow):
    """CAN Bus Siber Güvenlik Test Ana Penceresi"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CAN Bus Siber Güvenlik Test Sistemi - Kvaser Memorator 2xHS")
        self.setGeometry(100, 100, 1400, 900)

        # CAN tester
        if CANLIB_AVAILABLE:
            self.tester = CANSecurityTester()
        else:
            self.tester = MockCANSecurityTester()
            self.statusBar().showMessage("⚠️ Mock mode - Kvaser CANlib bulunamadı", 5000)

        # Sinyal emitter (thread-safe GUI güncellemeleri için)
        self.signals = SignalEmitter()
        self.signals.status_update.connect(self._on_status_update)
        self.signals.message_received.connect(self._on_message_received)
        self.signals.log_message.connect(self._on_log_message)

        self.tester.set_status_callback(self._status_callback)
        self.tester.set_message_callback(self._message_callback)

        # Logging
        self._setup_logging()

        # CAN mesaj buffer
        self.message_buffer = []
        self.max_message_buffer = 1000

        # UI
        self._init_ui()

        # Timer (istatistik güncellemesi için)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_statistics)
        self.update_timer.start(500)  # 500ms

        self.logger.info("CAN Security GUI başlatıldı")

    def _setup_logging(self):
        """Logging konfigürasyonu"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"can_security_{timestamp}.log"

        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger(__name__)

    def _init_ui(self):
        """UI başlat"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Başlık
        title_label = QLabel("⚠️ CAN BUS SİBER GÜVENLİK TEST SİSTEMİ ⚠️")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: red; padding: 10px;")
        main_layout.addWidget(title_label)

        # Uyarı
        warning_label = QLabel(
            "Bu yazılım SADECE yetkili güvenlik testleri, araştırma ve eğitim amaçlı kullanılmalıdır.\n"
            "Yetkisiz kullanım yasalara aykırıdır ve ciddi sonuçlar doğurabilir."
        )
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("background-color: yellow; padding: 10px; color: black;")
        main_layout.addWidget(warning_label)

        # Üst panel (Bağlantı + İstatistik)
        top_panel = QHBoxLayout()
        main_layout.addLayout(top_panel)

        # Bağlantı grubu
        connection_group = self._create_connection_group()
        top_panel.addWidget(connection_group)

        # İstatistik grubu
        stats_group = self._create_statistics_group()
        top_panel.addWidget(stats_group)

        # Tab widget
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        # Saldırı kontrol tab
        attack_tab = self._create_attack_tab()
        tab_widget.addTab(attack_tab, "Saldırı Kontrolü")

        # Monitor tab
        monitor_tab = self._create_monitor_tab()
        tab_widget.addTab(monitor_tab, "CAN Bus Monitor")

        # Log tab
        log_tab = self._create_log_tab()
        tab_widget.addTab(log_tab, "Log")

        # Durum çubuğu
        self.statusBar().showMessage("Hazır")

    def _create_connection_group(self) -> QGroupBox:
        """Bağlantı kontrol grubu"""
        group = QGroupBox("CAN Bağlantısı")
        layout = QGridLayout()

        # Kanal
        layout.addWidget(QLabel("Kanal:"), 0, 0)
        self.channel_spin = QSpinBox()
        self.channel_spin.setRange(0, 7)
        self.channel_spin.setValue(0)
        layout.addWidget(self.channel_spin, 0, 1)

        # Baud rate
        layout.addWidget(QLabel("Baud Rate:"), 1, 0)
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems([
            "125000 (125 kbit/s)",
            "250000 (250 kbit/s)",
            "500000 (500 kbit/s)",
            "1000000 (1 Mbit/s)"
        ])
        self.baudrate_combo.setCurrentIndex(2)  # 500000
        layout.addWidget(self.baudrate_combo, 1, 1)

        # Bağlan butonu
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        self.connect_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(self.connect_btn, 2, 0, 1, 2)

        # Durum
        self.connection_status_label = QLabel("● Bağlantı Yok")
        self.connection_status_label.setStyleSheet("color: red;")
        layout.addWidget(self.connection_status_label, 3, 0, 1, 2)

        group.setLayout(layout)
        return group

    def _create_statistics_group(self) -> QGroupBox:
        """İstatistik grubu"""
        group = QGroupBox("İstatistikler")
        layout = QGridLayout()

        self.stat_labels = {}

        stats = [
            ("Gönderilen Paket:", "packets_sent"),
            ("Alınan Paket:", "packets_received"),
            ("Hata:", "errors"),
            ("Aktif Saldırı:", "attack_type")
        ]

        for i, (label_text, key) in enumerate(stats):
            layout.addWidget(QLabel(label_text), i, 0)
            label = QLabel("0")
            label.setStyleSheet("font-weight: bold;")
            self.stat_labels[key] = label
            layout.addWidget(label, i, 1)

        group.setLayout(layout)
        return group

    def _create_attack_tab(self) -> QWidget:
        """Saldırı kontrol tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Saldırı seçimi
        attack_group = QGroupBox("Saldırı Türü Seçimi")
        attack_layout = QGridLayout()

        attack_layout.addWidget(QLabel("Saldırı Türü:"), 0, 0)
        self.attack_type_combo = QComboBox()
        attack_types = [
            ("Fuzzing - Rastgele CAN Mesajları", AttackType.FUZZING),
            ("DoS - Bus Flooding", AttackType.DOS),
            ("Spoofing - Sahte Mesaj Gönderme", AttackType.SPOOFING),
            ("Replay - Mesaj Tekrarı", AttackType.REPLAY),
            ("Diagnostic - UDS Komutları", AttackType.DIAGNOSTIC),
            ("Error Frame - Hata Frame Enjeksiyonu", AttackType.ERROR_FRAME),
            ("Bus Off - Bus Off Durumu", AttackType.BUS_OFF),
            ("ID Scan - CAN ID Tarama", AttackType.ID_SCAN)
        ]

        for text, attack_type in attack_types:
            self.attack_type_combo.addItem(text, attack_type)

        self.attack_type_combo.currentIndexChanged.connect(self._on_attack_type_changed)
        attack_layout.addWidget(self.attack_type_combo, 0, 1)

        attack_group.setLayout(attack_layout)
        layout.addWidget(attack_group)

        # Saldırı parametreleri
        params_group = QGroupBox("Saldırı Parametreleri")
        params_layout = QGridLayout()

        # Hedef ID
        params_layout.addWidget(QLabel("Hedef ID (Hex):"), 0, 0)
        self.target_id_input = QLineEdit("0x000")
        params_layout.addWidget(self.target_id_input, 0, 1)

        # Paket hızı
        params_layout.addWidget(QLabel("Paket Hızı (pkt/s):"), 1, 0)
        self.packet_rate_spin = QDoubleSpinBox()
        self.packet_rate_spin.setRange(1, 10000)
        self.packet_rate_spin.setValue(100)
        self.packet_rate_spin.setDecimals(0)
        params_layout.addWidget(self.packet_rate_spin, 1, 1)

        # Süre
        params_layout.addWidget(QLabel("Süre (saniye):"), 2, 0)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(1, 3600)
        self.duration_spin.setValue(10)
        params_layout.addWidget(self.duration_spin, 2, 1)

        # ID aralığı başlangıç
        params_layout.addWidget(QLabel("ID Aralığı Başlangıç (Hex):"), 3, 0)
        self.id_start_input = QLineEdit("0x000")
        params_layout.addWidget(self.id_start_input, 3, 1)

        # ID aralığı bitiş
        params_layout.addWidget(QLabel("ID Aralığı Bitiş (Hex):"), 4, 0)
        self.id_end_input = QLineEdit("0x7FF")
        params_layout.addWidget(self.id_end_input, 4, 1)

        # Data uzunluğu
        params_layout.addWidget(QLabel("Data Uzunluğu (byte):"), 5, 0)
        self.data_len_spin = QSpinBox()
        self.data_len_spin.setRange(0, 8)
        self.data_len_spin.setValue(8)
        params_layout.addWidget(self.data_len_spin, 5, 1)

        params_group.setLayout(params_layout)
        layout.addWidget(params_group)

        # Replay kontrolleri
        replay_group = QGroupBox("Replay Attack Kontrolleri")
        replay_layout = QHBoxLayout()

        self.capture_btn = QPushButton("Mesaj Yakalamayı Başlat")
        self.capture_btn.clicked.connect(self._on_capture_clicked)
        replay_layout.addWidget(self.capture_btn)

        self.stop_capture_btn = QPushButton("Yakalamayı Durdur")
        self.stop_capture_btn.clicked.connect(self._on_stop_capture_clicked)
        self.stop_capture_btn.setEnabled(False)
        replay_layout.addWidget(self.stop_capture_btn)

        self.captured_label = QLabel("Yakalanan: 0 mesaj")
        replay_layout.addWidget(self.captured_label)

        replay_group.setLayout(replay_layout)
        layout.addWidget(replay_group)

        # Kontrol butonları
        control_layout = QHBoxLayout()

        self.start_attack_btn = QPushButton("🚀 SALDIRIYI BAŞLAT")
        self.start_attack_btn.clicked.connect(self._on_start_attack_clicked)
        self.start_attack_btn.setStyleSheet(
            "background-color: #f44336; color: white; padding: 15px; font-size: 14pt; font-weight: bold;"
        )
        self.start_attack_btn.setEnabled(False)
        control_layout.addWidget(self.start_attack_btn)

        self.stop_attack_btn = QPushButton("⛔ SALDIRIYI DURDUR")
        self.stop_attack_btn.clicked.connect(self._on_stop_attack_clicked)
        self.stop_attack_btn.setStyleSheet(
            "background-color: #FF9800; color: white; padding: 15px; font-size: 14pt; font-weight: bold;"
        )
        self.stop_attack_btn.setEnabled(False)
        control_layout.addWidget(self.stop_attack_btn)

        layout.addLayout(control_layout)

        # Saldırı açıklaması
        self.attack_desc_text = QTextEdit()
        self.attack_desc_text.setReadOnly(True)
        self.attack_desc_text.setMaximumHeight(100)
        self._update_attack_description()
        layout.addWidget(self.attack_desc_text)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _create_monitor_tab(self) -> QWidget:
        """CAN bus monitor tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Kontrol butonları
        control_layout = QHBoxLayout()

        clear_btn = QPushButton("Temizle")
        clear_btn.clicked.connect(self._on_clear_monitor_clicked)
        control_layout.addWidget(clear_btn)

        export_btn = QPushButton("CSV'ye Aktar")
        export_btn.clicked.connect(self._on_export_monitor_clicked)
        control_layout.addWidget(export_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Mesaj tablosu
        self.message_table = QTableWidget()
        self.message_table.setColumnCount(5)
        self.message_table.setHorizontalHeaderLabels([
            "Zaman", "ID (Hex)", "DLC", "Data (Hex)", "ASCII"
        ])
        self.message_table.setColumnWidth(0, 150)
        self.message_table.setColumnWidth(1, 100)
        self.message_table.setColumnWidth(2, 50)
        self.message_table.setColumnWidth(3, 300)
        self.message_table.setColumnWidth(4, 200)

        layout.addWidget(self.message_table)

        widget.setLayout(layout)
        return widget

    def _create_log_tab(self) -> QWidget:
        """Log tab"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Kontrol butonları
        control_layout = QHBoxLayout()

        clear_log_btn = QPushButton("Temizle")
        clear_log_btn.clicked.connect(self._on_clear_log_clicked)
        control_layout.addWidget(clear_log_btn)

        export_log_btn = QPushButton("Log'u Kaydet")
        export_log_btn.clicked.connect(self._on_export_log_clicked)
        control_layout.addWidget(export_log_btn)

        control_layout.addStretch()

        layout.addLayout(control_layout)

        # Log text
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.log_text)

        widget.setLayout(layout)
        return widget

    # ==================== Event Handlers ====================

    def _on_connect_clicked(self):
        """Bağlan/Bağlantıyı Kes butonuna tıklandı"""
        if self.tester.is_connected:
            # Bağlantıyı kes
            self.tester.disconnect()
            self.connect_btn.setText("Bağlan")
            self.connect_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
            self.connection_status_label.setText("● Bağlantı Yok")
            self.connection_status_label.setStyleSheet("color: red;")
            self.start_attack_btn.setEnabled(False)
            self.statusBar().showMessage("Bağlantı kesildi", 3000)
            self._log("INFO", "CAN bağlantısı kesildi")
        else:
            # Bağlan
            channel = self.channel_spin.value()
            bitrate = int(self.baudrate_combo.currentText().split()[0])

            self.tester.channel_num = channel
            self.tester.bitrate = bitrate

            if self.tester.connect():
                self.connect_btn.setText("Bağlantıyı Kes")
                self.connect_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
                self.connection_status_label.setText("● Bağlı")
                self.connection_status_label.setStyleSheet("color: green;")
                self.start_attack_btn.setEnabled(True)
                self.statusBar().showMessage(f"Bağlandı: Kanal {channel}, {bitrate} bit/s", 3000)
                self._log("INFO", f"CAN bağlantısı başarılı: Kanal {channel}, {bitrate} bit/s")
            else:
                QMessageBox.critical(
                    self,
                    "Bağlantı Hatası",
                    "CAN cihazına bağlanılamadı!\n\n"
                    "Kvaser Memorator bağlı mı?\n"
                    "Kanal numarası doğru mu?\n"
                    "CANlib SDK kurulu mu?"
                )
                self._log("ERROR", "CAN bağlantısı başarısız")

    def _on_attack_type_changed(self):
        """Saldırı türü değişti"""
        self._update_attack_description()

    def _on_capture_clicked(self):
        """Mesaj yakalamayı başlat"""
        if not self.tester.is_connected:
            QMessageBox.warning(self, "Uyarı", "Önce CAN bus'a bağlanın!")
            return

        self.tester.start_capture()
        self.capture_btn.setEnabled(False)
        self.stop_capture_btn.setEnabled(True)
        self.statusBar().showMessage("Mesaj yakalama başlatıldı", 3000)
        self._log("INFO", "Mesaj yakalama başlatıldı")

    def _on_stop_capture_clicked(self):
        """Mesaj yakalamayı durdur"""
        messages = self.tester.stop_capture()
        self.capture_btn.setEnabled(True)
        self.stop_capture_btn.setEnabled(False)
        self.captured_label.setText(f"Yakalanan: {len(messages)} mesaj")
        self.statusBar().showMessage(f"{len(messages)} mesaj yakalandı", 3000)
        self._log("INFO", f"{len(messages)} mesaj yakalandı")

    def _on_start_attack_clicked(self):
        """Saldırıyı başlat"""
        if not self.tester.is_connected:
            QMessageBox.warning(self, "Uyarı", "Önce CAN bus'a bağlanın!")
            return

        # Onay iste
        reply = QMessageBox.question(
            self,
            "⚠️ Saldırı Onayı",
            "CAN bus saldırısı başlatmak istediğinizden emin misiniz?\n\n"
            "Bu işlem yetkili güvenlik testi kapsamında yapılmalıdır.\n"
            "Yetkisiz kullanım yasalara aykırıdır!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Konfigürasyon oluştur
        try:
            attack_type = self.attack_type_combo.currentData()
            target_id = int(self.target_id_input.text(), 16)
            packet_rate = self.packet_rate_spin.value()
            duration = self.duration_spin.value()
            id_start = int(self.id_start_input.text(), 16)
            id_end = int(self.id_end_input.text(), 16)
            data_len = self.data_len_spin.value()

            config = AttackConfig(
                attack_type=attack_type,
                target_id=target_id,
                packet_rate=packet_rate,
                duration=duration,
                id_range_start=id_start,
                id_range_end=id_end,
                data_length=data_len,
                replay_messages=self.tester.captured_messages.copy() if attack_type == AttackType.REPLAY else None
            )

            if self.tester.start_attack(config):
                self.start_attack_btn.setEnabled(False)
                self.stop_attack_btn.setEnabled(True)
                self.statusBar().showMessage(f"Saldırı başlatıldı: {attack_type.value}", 3000)
                self._log("WARNING", f"Saldırı başlatıldı: {attack_type.value}")
            else:
                QMessageBox.critical(self, "Hata", "Saldırı başlatılamadı!")

        except ValueError as e:
            QMessageBox.critical(self, "Hata", f"Geçersiz parametre: {e}")

    def _on_stop_attack_clicked(self):
        """Saldırıyı durdur"""
        self.tester.stop_attack()
        self.start_attack_btn.setEnabled(True)
        self.stop_attack_btn.setEnabled(False)
        self.statusBar().showMessage("Saldırı durduruldu", 3000)
        self._log("INFO", "Saldırı durduruldu")

    def _on_clear_monitor_clicked(self):
        """Monitor'ü temizle"""
        self.message_table.setRowCount(0)
        self.message_buffer.clear()

    def _on_export_monitor_clicked(self):
        """Monitor verilerini CSV'ye aktar"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "CSV Kaydet",
            f"can_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write("Timestamp,ID,DLC,Data,ASCII\n")
                    for msg in self.message_buffer:
                        f.write(f"{msg['time']},{msg['id']},{msg['dlc']},{msg['data']},{msg['ascii']}\n")

                QMessageBox.information(self, "Başarılı", f"{len(self.message_buffer)} mesaj kaydedildi")
                self._log("INFO", f"Monitor verileri kaydedildi: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yazılamadı: {e}")

    def _on_clear_log_clicked(self):
        """Log'u temizle"""
        self.log_text.clear()

    def _on_export_log_clicked(self):
        """Log'u kaydet"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Log Kaydet",
            f"can_security_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt)"
        )

        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.log_text.toPlainText())

                QMessageBox.information(self, "Başarılı", "Log kaydedildi")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya yazılamadı: {e}")

    # ==================== Callbacks ====================

    def _status_callback(self, status: str, data: dict):
        """Saldırı durum güncellemesi (thread-safe)"""
        self.signals.status_update.emit(status, data)

    def _message_callback(self, frame):
        """CAN mesaj alındı (thread-safe)"""
        self.signals.message_received.emit(frame)

    def _on_status_update(self, status: str, data: dict):
        """Durum güncellemesi (ana thread)"""
        if status == "stopped":
            self.start_attack_btn.setEnabled(True)
            self.stop_attack_btn.setEnabled(False)

    def _on_message_received(self, frame):
        """CAN mesaj alındı (ana thread)"""
        if frame is None:
            return

        # Buffer'a ekle
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        can_id = f"0x{frame.id:03X}"
        dlc = frame.dlc
        data_hex = ' '.join(f'{b:02X}' for b in frame.data)
        data_ascii = ''.join(chr(b) if 32 <= b < 127 else '.' for b in frame.data)

        msg_data = {
            'time': timestamp,
            'id': can_id,
            'dlc': dlc,
            'data': data_hex,
            'ascii': data_ascii
        }

        self.message_buffer.append(msg_data)

        # Buffer limit
        if len(self.message_buffer) > self.max_message_buffer:
            self.message_buffer.pop(0)

        # Tabloya ekle
        row = self.message_table.rowCount()
        self.message_table.insertRow(row)

        self.message_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.message_table.setItem(row, 1, QTableWidgetItem(can_id))
        self.message_table.setItem(row, 2, QTableWidgetItem(str(dlc)))
        self.message_table.setItem(row, 3, QTableWidgetItem(data_hex))
        self.message_table.setItem(row, 4, QTableWidgetItem(data_ascii))

        # Auto-scroll
        self.message_table.scrollToBottom()

        # Table limit
        if self.message_table.rowCount() > self.max_message_buffer:
            self.message_table.removeRow(0)

    def _on_log_message(self, level: str, message: str):
        """Log mesajı (ana thread)"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"

        # Renk ekle
        if level == "ERROR":
            color = "red"
        elif level == "WARNING":
            color = "orange"
        elif level == "INFO":
            color = "blue"
        else:
            color = "black"

        self.log_text.append(f'<span style="color:{color}">{log_entry}</span>')

    # ==================== Helpers ====================

    def _log(self, level: str, message: str):
        """Log mesajı ekle"""
        self.signals.log_message.emit(level, message)

    def _update_statistics(self):
        """İstatistikleri güncelle"""
        stats = self.tester.get_statistics()

        self.stat_labels['packets_sent'].setText(str(stats['packets_sent']))
        self.stat_labels['packets_received'].setText(str(stats['packets_received']))
        self.stat_labels['errors'].setText(str(stats['errors']))
        self.stat_labels['attack_type'].setText(stats['attack_type'] or "Yok")

    def _update_attack_description(self):
        """Saldırı açıklamasını güncelle"""
        attack_type = self.attack_type_combo.currentData()

        descriptions = {
            AttackType.FUZZING: (
                "<b>Fuzzing Saldırısı</b><br>"
                "Rastgele CAN ID ve data ile mesajlar gönderir. ECU'ların beklenmedik girişlere "
                "karşı davranışını test eder. Buffer overflow, crash ve güvenlik açıkları tespit edilebilir."
            ),
            AttackType.DOS: (
                "<b>DoS (Denial of Service) Saldırısı</b><br>"
                "CAN bus'ı maksimum hızda mesajlarla doldurarak normal iletişimi engeller. "
                "Bus yükünü %100'e çıkarır ve diğer ECU'ların mesaj göndermesini önler."
            ),
            AttackType.SPOOFING: (
                "<b>Spoofing Saldırısı</b><br>"
                "Belirli bir CAN ID'sine sahte mesajlar gönderir. Örneğin hız, motor devri gibi "
                "kritik verileri manipüle ederek sistemin davranışını değiştirebilir."
            ),
            AttackType.REPLAY: (
                "<b>Replay Saldırısı</b><br>"
                "Yakalanan CAN mesajlarını tekrar gönderir. Örneğin kilit açma, motor çalıştırma "
                "gibi komutları tekrarlayarak yetkisiz işlemler gerçekleştirebilir."
            ),
            AttackType.DIAGNOSTIC: (
                "<b>Diagnostic Saldırısı</b><br>"
                "UDS (Unified Diagnostic Services) komutları gönderir. ECU reset, güvenlik erişimi, "
                "veri okuma/yazma gibi diagnostic servisleri test eder."
            ),
            AttackType.ERROR_FRAME: (
                "<b>Error Frame Injection Saldırısı</b><br>"
                "CAN bus'a hata frame'leri enjekte eder. Diğer ECU'ların error counter'larını "
                "artırarak bus-off durumuna geçmelerini sağlayabilir."
            ),
            AttackType.BUS_OFF: (
                "<b>Bus Off Saldırısı</b><br>"
                "ECU'ları bus-off durumuna getirmeye çalışır. Yüksek öncelikli ID'lerle "
                "flooding yaparak hedef ECU'nun error counter'ını artırır."
            ),
            AttackType.ID_SCAN: (
                "<b>ID Scan Saldırısı</b><br>"
                "Belirli bir ID aralığını tarayarak aktif CAN ID'lerini tespit eder. "
                "Bus'taki mevcut ECU'ları ve kullanılan ID'leri haritalandırır."
            )
        }

        desc = descriptions.get(attack_type, "Açıklama bulunamadı")
        self.attack_desc_text.setHtml(desc)

    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        if self.tester.is_connected:
            reply = QMessageBox.question(
                self,
                "Çıkış Onayı",
                "CAN bağlantısı aktif. Çıkmak istediğinizden emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.tester.disconnect()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Ana program"""
    app = QApplication(sys.argv)

    # Stil
    app.setStyle('Fusion')

    # Ana pencere
    window = CANSecurityGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

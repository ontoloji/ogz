"""
Kvaser Memorator 2xHS CAN Mesaj Logger
DBC dosyası veya manuel giriş ile CAN mesajlarını CSV'ye loglama
"""

import sys
import os
import csv
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, QSpinBox,
    QTableWidget, QTableWidgetItem, QGroupBox, QMessageBox, QComboBox,
    QHeaderView, QCheckBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont

# DBC ve CAN kütüphaneleri
try:
    import cantools
    CANTOOLS_AVAILABLE = True
except ImportError:
    CANTOOLS_AVAILABLE = False
    logging.warning("cantools kütüphanesi bulunamadı. DBC desteği sınırlı olacak.")

try:
    from canlib import canlib, Frame
    CANLIB_AVAILABLE = True
except ImportError:
    CANLIB_AVAILABLE = False
    logging.warning("Kvaser CANlib bulunamadı. CAN işlevselliği sınırlı olacak.")


class CANMessage:
    """CAN mesaj tanımı"""

    def __init__(self, msg_id: int, name: str = "", signals: List[Tuple[str, int, int]] = None):
        """
        Args:
            msg_id: CAN mesaj ID (hex veya decimal)
            name: Mesaj adı
            signals: Sinyal listesi [(isim, başlangıç_byte, uzunluk), ...]
        """
        self.id = msg_id
        self.name = name if name else f"MSG_0x{msg_id:X}"
        self.signals = signals if signals else []
        self.enabled = False
        self.last_data = None
        self.last_timestamp = None

    def __str__(self):
        return f"{self.name} (ID: 0x{self.id:X})"


class CANLogger(QObject):
    """CAN mesaj logger backend"""

    message_received = pyqtSignal(int, bytes, float)  # id, data, timestamp
    connection_status = pyqtSignal(bool, str)  # connected, message

    def __init__(self):
        super().__init__()
        self.channel = None
        self.is_connected = False
        self.is_logging = False

        # Loglama parametreleri
        self.messages: Dict[int, CANMessage] = {}  # ID -> CANMessage
        self.log_file = None
        self.csv_writer = None
        self.log_interval = 0.1  # saniye

        # Thread kontrol
        self.rx_thread = None
        self.log_thread = None
        self.running = False

        self.logger = logging.getLogger(__name__)

    def connect_can(self, channel_num: int = 0, bitrate: int = 500000) -> bool:
        """Kvaser CAN cihazına bağlan"""
        if not CANLIB_AVAILABLE:
            self.connection_status.emit(False, "Kvaser CANlib yüklü değil!")
            return False

        try:
            # Kanal aç
            self.channel = canlib.openChannel(channel_num, canlib.canOPEN_ACCEPT_VIRTUAL)

            # Bit rate ayarla
            self.channel.setBusParams(bitrate)

            # Bus'ı aç
            self.channel.busOn()

            self.is_connected = True
            self.connection_status.emit(True, f"Bağlantı başarılı: Kanal {channel_num}, {bitrate} bit/s")

            # RX thread başlat
            self._start_rx_thread()

            return True

        except Exception as e:
            self.connection_status.emit(False, f"Bağlantı hatası: {e}")
            return False

    def disconnect_can(self):
        """CAN bağlantısını kes"""
        self.stop_logging()
        self._stop_rx_thread()

        if self.channel:
            try:
                self.channel.busOff()
                self.channel.close()
                self.connection_status.emit(False, "Bağlantı kapatıldı")
            except Exception as e:
                self.logger.error(f"CAN kapatma hatası: {e}")

        self.is_connected = False
        self.channel = None

    def add_message(self, message: CANMessage):
        """Loglanacak mesaj ekle"""
        self.messages[message.id] = message

    def remove_message(self, msg_id: int):
        """Mesajı listeden çıkar"""
        if msg_id in self.messages:
            del self.messages[msg_id]

    def clear_messages(self):
        """Tüm mesajları temizle"""
        self.messages.clear()

    def set_message_enabled(self, msg_id: int, enabled: bool):
        """Mesaj loglama durumunu ayarla"""
        if msg_id in self.messages:
            self.messages[msg_id].enabled = enabled

    def start_logging(self, filename: str, log_interval: float = 0.1) -> bool:
        """CSV loglama başlat"""
        if self.is_logging:
            return False

        if not self.is_connected:
            self.logger.error("CAN bağlantısı yok!")
            return False

        try:
            # Tarih bilgisi ekle
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = filename.replace(".csv", "")
            full_filename = f"{base_name}_{timestamp}.csv"

            # CSV dosyası aç
            self.log_file = open(full_filename, 'w', newline='')
            self.csv_writer = csv.writer(self.log_file)

            # Başlık satırını yaz
            headers = ["Timestamp", "Time_ms", "Message_Name", "Message_ID"]

            # Tüm sinyalleri başlığa ekle
            for msg in self.messages.values():
                if msg.enabled:
                    if msg.signals:
                        for sig_name, _, _ in msg.signals:
                            headers.append(f"{msg.name}_{sig_name}")
                    else:
                        # Sinyal yoksa byte değerlerini yaz
                        for i in range(8):
                            headers.append(f"{msg.name}_Byte{i}")

            self.csv_writer.writerow(headers)
            self.log_file.flush()

            # Loglama parametreleri
            self.log_interval = log_interval
            self.is_logging = True

            # Log thread başlat
            self._start_log_thread()

            self.logger.info(f"Loglama başlatıldı: {full_filename}")
            return True

        except Exception as e:
            self.logger.error(f"Loglama başlatma hatası: {e}")
            return False

    def stop_logging(self):
        """Loglama durdur"""
        if not self.is_logging:
            return

        self.is_logging = False
        self._stop_log_thread()

        if self.log_file:
            try:
                self.log_file.close()
                self.logger.info("Loglama durduruldu")
            except Exception as e:
                self.logger.error(f"Log dosyası kapatma hatası: {e}")

        self.log_file = None
        self.csv_writer = None

    def _start_rx_thread(self):
        """CAN RX thread başlat"""
        self.running = True
        self.rx_thread = threading.Thread(target=self._rx_loop, daemon=True, name="CAN_RX")
        self.rx_thread.start()

    def _stop_rx_thread(self):
        """CAN RX thread durdur"""
        self.running = False
        if self.rx_thread:
            self.rx_thread.join(timeout=1.0)

    def _start_log_thread(self):
        """Log thread başlat"""
        self.log_thread = threading.Thread(target=self._log_loop, daemon=True, name="CAN_LOG")
        self.log_thread.start()

    def _stop_log_thread(self):
        """Log thread durdur"""
        if self.log_thread:
            self.log_thread.join(timeout=1.0)

    def _rx_loop(self):
        """CAN mesaj okuma döngüsü"""
        timeout = 100  # ms

        while self.running and self.is_connected:
            try:
                # Mesaj oku
                frame = self.channel.read(timeout=timeout)

                # İlgilendiğimiz mesaj mı?
                if frame.id in self.messages:
                    msg = self.messages[frame.id]
                    msg.last_data = bytes(frame.data)
                    msg.last_timestamp = time.time()

                    # Signal gönder
                    self.message_received.emit(frame.id, msg.last_data, msg.last_timestamp)

            except canlib.CanNoMsg:
                # Timeout - normal
                pass
            except Exception as e:
                self.logger.error(f"CAN RX hatası: {e}")
                time.sleep(0.1)

    def _log_loop(self):
        """Periyodik loglama döngüsü"""
        next_log_time = time.time()

        while self.is_logging:
            current_time = time.time()

            if current_time >= next_log_time:
                self._write_log_entry()
                next_log_time = current_time + self.log_interval

            time.sleep(0.001)  # CPU kullanımını azalt

    def _write_log_entry(self):
        """CSV'ye bir satır yaz"""
        if not self.csv_writer:
            return

        try:
            # Her aktif mesaj için bir satır yaz
            for msg in self.messages.values():
                if not msg.enabled or msg.last_data is None:
                    continue

                # Timestamp bilgisi
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                time_ms = int((msg.last_timestamp or 0) * 1000)

                row = [
                    timestamp_str,
                    time_ms,
                    msg.name,
                    f"0x{msg.id:X}"
                ]

                # Sinyal veya byte değerleri
                if msg.signals:
                    # Sinyal parsing
                    for sig_name, start_byte, length in msg.signals:
                        value = self._extract_signal(msg.last_data, start_byte, length)
                        row.append(value)
                else:
                    # Raw byte değerleri
                    for byte in msg.last_data[:8]:
                        row.append(f"0x{byte:02X}")

                self.csv_writer.writerow(row)

            self.log_file.flush()

        except Exception as e:
            self.logger.error(f"Log yazma hatası: {e}")

    def _extract_signal(self, data: bytes, start_byte: int, length: int) -> str:
        """CAN mesajından sinyal çıkar"""
        try:
            # Basit byte extraction (Little Endian)
            if start_byte + length > len(data):
                return "N/A"

            value = 0
            for i in range(length):
                value |= data[start_byte + i] << (8 * i)

            return str(value)
        except:
            return "ERR"


class KvaserMessageLoggerGUI(QMainWindow):
    """Ana GUI penceresi"""

    MAX_MANUAL_MESSAGES = 30

    def __init__(self):
        super().__init__()
        self.logger_backend = CANLogger()
        self.dbc_database = None

        # Sinyal bağlantıları
        self.logger_backend.connection_status.connect(self.on_connection_status)
        self.logger_backend.message_received.connect(self.on_message_received)

        self.init_ui()

        # Güncelleme timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)  # 500ms

    def init_ui(self):
        """GUI başlat"""
        self.setWindowTitle("Kvaser Memorator 2xHS - CAN Mesaj Logger")
        self.setGeometry(100, 100, 1200, 800)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Ana layout
        main_layout = QVBoxLayout(central_widget)

        # Üst panel - CAN bağlantı
        connection_group = self.create_connection_group()
        main_layout.addWidget(connection_group)

        # Orta panel - Mesaj yönetimi
        middle_layout = QHBoxLayout()

        # Sol: DBC ve Manuel giriş
        left_group = self.create_message_input_group()
        middle_layout.addWidget(left_group, 1)

        # Sağ: Mesaj listesi
        right_group = self.create_message_list_group()
        middle_layout.addWidget(right_group, 2)

        main_layout.addLayout(middle_layout)

        # Alt panel - Loglama kontrol
        logging_group = self.create_logging_group()
        main_layout.addWidget(logging_group)

        # Durum paneli
        status_group = self.create_status_group()
        main_layout.addWidget(status_group)

    def create_connection_group(self) -> QGroupBox:
        """CAN bağlantı grubu"""
        group = QGroupBox("CAN Bağlantı Ayarları")
        layout = QHBoxLayout()

        # Kanal seçimi
        layout.addWidget(QLabel("Kanal:"))
        self.channel_spin = QSpinBox()
        self.channel_spin.setRange(0, 7)
        self.channel_spin.setValue(0)
        layout.addWidget(self.channel_spin)

        # Bitrate seçimi
        layout.addWidget(QLabel("Bitrate:"))
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.addItems([
            "125000 (125 kbit/s)",
            "250000 (250 kbit/s)",
            "500000 (500 kbit/s)",
            "1000000 (1 Mbit/s)"
        ])
        self.bitrate_combo.setCurrentIndex(2)  # 500k default
        layout.addWidget(self.bitrate_combo)

        # Bağlan butonu
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_btn)

        # Durum etiketi
        self.connection_status_label = QLabel("Bağlı Değil")
        self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.connection_status_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_message_input_group(self) -> QGroupBox:
        """Mesaj girişi grubu"""
        group = QGroupBox("Mesaj Tanımlama")
        layout = QVBoxLayout()

        # DBC yükleme
        dbc_layout = QHBoxLayout()
        dbc_layout.addWidget(QLabel("DBC Dosyası:"))
        self.dbc_path_edit = QLineEdit()
        self.dbc_path_edit.setReadOnly(True)
        dbc_layout.addWidget(self.dbc_path_edit)

        self.dbc_browse_btn = QPushButton("Gözat...")
        self.dbc_browse_btn.clicked.connect(self.browse_dbc)
        dbc_layout.addWidget(self.dbc_browse_btn)

        self.dbc_load_btn = QPushButton("DBC Yükle")
        self.dbc_load_btn.clicked.connect(self.load_dbc)
        dbc_layout.addWidget(self.dbc_load_btn)

        layout.addLayout(dbc_layout)

        # DBC mesaj seçimi
        dbc_msg_layout = QHBoxLayout()
        dbc_msg_layout.addWidget(QLabel("DBC Mesajı:"))
        self.dbc_message_combo = QComboBox()
        self.dbc_message_combo.setEnabled(False)
        dbc_msg_layout.addWidget(self.dbc_message_combo)

        self.add_dbc_msg_btn = QPushButton("DBC Mesajı Ekle")
        self.add_dbc_msg_btn.clicked.connect(self.add_dbc_message)
        self.add_dbc_msg_btn.setEnabled(False)
        dbc_msg_layout.addWidget(self.add_dbc_msg_btn)

        layout.addLayout(dbc_msg_layout)

        # Ayırıcı
        layout.addWidget(QLabel("-" * 50))

        # Manuel mesaj girişi
        layout.addWidget(QLabel("Manuel Mesaj Tanımlama:"))

        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Mesaj ID (hex):"))
        self.manual_id_edit = QLineEdit()
        self.manual_id_edit.setPlaceholderText("örn: 0x123 veya 291")
        manual_layout.addWidget(self.manual_id_edit)

        manual_layout.addWidget(QLabel("İsim:"))
        self.manual_name_edit = QLineEdit()
        self.manual_name_edit.setPlaceholderText("Mesaj ismi")
        manual_layout.addWidget(self.manual_name_edit)

        layout.addLayout(manual_layout)

        # Manuel mesaj ekle butonu
        add_manual_layout = QHBoxLayout()
        self.add_manual_btn = QPushButton("Manuel Mesaj Ekle")
        self.add_manual_btn.clicked.connect(self.add_manual_message)
        add_manual_layout.addWidget(self.add_manual_btn)

        self.manual_count_label = QLabel(f"0/{self.MAX_MANUAL_MESSAGES}")
        add_manual_layout.addWidget(self.manual_count_label)
        add_manual_layout.addStretch()

        layout.addLayout(add_manual_layout)

        # Bilgi notu
        info_label = QLabel(
            "Not: Manuel mesajlar için byte değerleri otomatik olarak loglanır.\n"
            "DBC mesajları için sinyal değerleri loglanır."
        )
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info_label)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_message_list_group(self) -> QGroupBox:
        """Mesaj listesi grubu"""
        group = QGroupBox("Loglanacak Mesajlar")
        layout = QVBoxLayout()

        # Mesaj tablosu
        self.message_table = QTableWidget()
        self.message_table.setColumnCount(5)
        self.message_table.setHorizontalHeaderLabels([
            "Aktif", "ID", "Mesaj Adı", "Sinyal Sayısı", "Son Veri"
        ])

        header = self.message_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.message_table)

        # Kontrol butonları
        btn_layout = QHBoxLayout()

        self.remove_msg_btn = QPushButton("Seçili Mesajı Kaldır")
        self.remove_msg_btn.clicked.connect(self.remove_selected_message)
        btn_layout.addWidget(self.remove_msg_btn)

        self.clear_msg_btn = QPushButton("Tüm Mesajları Temizle")
        self.clear_msg_btn.clicked.connect(self.clear_all_messages)
        btn_layout.addWidget(self.clear_msg_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def create_logging_group(self) -> QGroupBox:
        """Loglama kontrol grubu"""
        group = QGroupBox("Loglama Kontrol")
        layout = QVBoxLayout()

        # Dosya ismi girişi
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Log Dosyası İsmi:"))
        self.log_filename_edit = QLineEdit()
        self.log_filename_edit.setText("can_log")
        self.log_filename_edit.setPlaceholderText("Dosya ismi (tarih otomatik eklenecek)")
        file_layout.addWidget(self.log_filename_edit)
        file_layout.addWidget(QLabel(".csv"))

        self.browse_log_btn = QPushButton("Klasör Seç...")
        self.browse_log_btn.clicked.connect(self.browse_log_folder)
        file_layout.addWidget(self.browse_log_btn)

        layout.addLayout(file_layout)

        # Loglama sıklığı
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Loglama Sıklığı:"))
        self.log_interval_spin = QDoubleSpinBox()
        self.log_interval_spin.setRange(0.001, 10.0)
        self.log_interval_spin.setSingleStep(0.01)
        self.log_interval_spin.setValue(0.1)
        self.log_interval_spin.setSuffix(" saniye")
        self.log_interval_spin.setDecimals(3)
        interval_layout.addWidget(self.log_interval_spin)

        interval_layout.addWidget(QLabel("(1000 ms = 1 Hz, 100 ms = 10 Hz, 10 ms = 100 Hz)"))
        interval_layout.addStretch()
        layout.addLayout(interval_layout)

        # Loglama butonları
        btn_layout = QHBoxLayout()

        self.start_log_btn = QPushButton("Loglamayı Başlat")
        self.start_log_btn.clicked.connect(self.start_logging)
        self.start_log_btn.setStyleSheet("background-color: green; color: white; font-weight: bold;")
        btn_layout.addWidget(self.start_log_btn)

        self.stop_log_btn = QPushButton("Loglamayı Durdur")
        self.stop_log_btn.clicked.connect(self.stop_logging)
        self.stop_log_btn.setEnabled(False)
        self.stop_log_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_layout.addWidget(self.stop_log_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        group.setLayout(layout)
        return group

    def create_status_group(self) -> QGroupBox:
        """Durum paneli"""
        group = QGroupBox("Durum")
        layout = QVBoxLayout()

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)

        font = QFont("Courier New", 9)
        self.status_text.setFont(font)

        layout.addWidget(self.status_text)
        group.setLayout(layout)
        return group

    def toggle_connection(self):
        """CAN bağlantısını aç/kapat"""
        if self.logger_backend.is_connected:
            self.logger_backend.disconnect_can()
        else:
            channel = self.channel_spin.value()
            bitrate_text = self.bitrate_combo.currentText()
            bitrate = int(bitrate_text.split()[0])

            self.logger_backend.connect_can(channel, bitrate)

    def on_connection_status(self, connected: bool, message: str):
        """Bağlantı durumu değişti"""
        if connected:
            self.connection_status_label.setText("Bağlı")
            self.connection_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.connect_btn.setText("Bağlantıyı Kes")
        else:
            self.connection_status_label.setText("Bağlı Değil")
            self.connection_status_label.setStyleSheet("color: red; font-weight: bold;")
            self.connect_btn.setText("Bağlan")

        self.log_status(message)

    def browse_dbc(self):
        """DBC dosyası seç"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "DBC Dosyası Seç",
            "",
            "DBC Files (*.dbc);;All Files (*)"
        )

        if filename:
            self.dbc_path_edit.setText(filename)

    def load_dbc(self):
        """DBC dosyasını yükle"""
        if not CANTOOLS_AVAILABLE:
            QMessageBox.warning(self, "Hata", "cantools kütüphanesi yüklü değil!")
            return

        dbc_path = self.dbc_path_edit.text()
        if not dbc_path or not os.path.exists(dbc_path):
            QMessageBox.warning(self, "Hata", "Geçerli bir DBC dosyası seçin!")
            return

        try:
            # DBC dosyasını yükle
            self.dbc_database = cantools.database.load_file(dbc_path)

            # Mesaj listesini güncelle
            self.dbc_message_combo.clear()
            for msg in self.dbc_database.messages:
                self.dbc_message_combo.addItem(f"{msg.name} (0x{msg.frame_id:X})", msg)

            self.dbc_message_combo.setEnabled(True)
            self.add_dbc_msg_btn.setEnabled(True)

            self.log_status(f"DBC dosyası yüklendi: {len(self.dbc_database.messages)} mesaj")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"DBC yükleme hatası: {e}")

    def add_dbc_message(self):
        """DBC'den mesaj ekle"""
        if not self.dbc_database:
            return

        dbc_msg = self.dbc_message_combo.currentData()
        if not dbc_msg:
            return

        # Sinyalleri çıkar
        signals = []
        for signal in dbc_msg.signals:
            # Basit sinyal bilgisi (start byte, length)
            start_byte = signal.start // 8
            length = (signal.length + 7) // 8
            signals.append((signal.name, start_byte, length))

        # Mesaj oluştur
        msg = CANMessage(dbc_msg.frame_id, dbc_msg.name, signals)
        msg.enabled = True

        # Backend'e ekle
        self.logger_backend.add_message(msg)

        # Tabloya ekle
        self.add_message_to_table(msg)

        self.log_status(f"DBC mesajı eklendi: {msg.name} (0x{msg.id:X})")

    def add_manual_message(self):
        """Manuel mesaj ekle"""
        # Mesaj sayısı kontrolü
        current_count = len(self.logger_backend.messages)
        if current_count >= self.MAX_MANUAL_MESSAGES:
            QMessageBox.warning(
                self,
                "Limit",
                f"Maksimum {self.MAX_MANUAL_MESSAGES} mesaj eklenebilir!"
            )
            return

        # ID'yi parse et
        id_text = self.manual_id_edit.text().strip()
        if not id_text:
            QMessageBox.warning(self, "Hata", "Mesaj ID giriniz!")
            return

        try:
            # Hex veya decimal
            if id_text.lower().startswith("0x"):
                msg_id = int(id_text, 16)
            else:
                msg_id = int(id_text)

            if msg_id < 0 or msg_id > 0x1FFFFFFF:
                raise ValueError("Geçersiz CAN ID")

        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçersiz mesaj ID formatı!")
            return

        # Mesaj ismini al
        msg_name = self.manual_name_edit.text().strip()
        if not msg_name:
            msg_name = f"MSG_0x{msg_id:X}"

        # Mesaj oluştur (sinyal yok, raw byte logging)
        msg = CANMessage(msg_id, msg_name, signals=[])
        msg.enabled = True

        # Backend'e ekle
        self.logger_backend.add_message(msg)

        # Tabloya ekle
        self.add_message_to_table(msg)

        # Girişleri temizle
        self.manual_id_edit.clear()
        self.manual_name_edit.clear()

        self.update_manual_count()
        self.log_status(f"Manuel mesaj eklendi: {msg.name} (0x{msg.id:X})")

    def add_message_to_table(self, msg: CANMessage):
        """Tabloya mesaj ekle"""
        row = self.message_table.rowCount()
        self.message_table.insertRow(row)

        # Checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(msg.enabled)
        checkbox.stateChanged.connect(
            lambda state, mid=msg.id: self.on_message_enabled_changed(mid, state)
        )
        checkbox_widget = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_widget)
        checkbox_layout.addWidget(checkbox)
        checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        checkbox_layout.setContentsMargins(0, 0, 0, 0)
        self.message_table.setCellWidget(row, 0, checkbox_widget)

        # ID
        self.message_table.setItem(row, 1, QTableWidgetItem(f"0x{msg.id:X}"))

        # İsim
        self.message_table.setItem(row, 2, QTableWidgetItem(msg.name))

        # Sinyal sayısı
        sig_count = len(msg.signals) if msg.signals else 8  # 8 byte
        self.message_table.setItem(row, 3, QTableWidgetItem(str(sig_count)))

        # Son veri
        self.message_table.setItem(row, 4, QTableWidgetItem("-"))

        # Mesaj ID'yi row'a kaydet
        self.message_table.item(row, 1).setData(Qt.ItemDataRole.UserRole, msg.id)

    def on_message_enabled_changed(self, msg_id: int, state: int):
        """Mesaj aktif/pasif durumu değişti"""
        enabled = (state == Qt.CheckState.Checked.value)
        self.logger_backend.set_message_enabled(msg_id, enabled)

    def remove_selected_message(self):
        """Seçili mesajı kaldır"""
        current_row = self.message_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir mesaj seçin!")
            return

        # Mesaj ID'yi al
        msg_id = self.message_table.item(current_row, 1).data(Qt.ItemDataRole.UserRole)

        # Backend'den kaldır
        self.logger_backend.remove_message(msg_id)

        # Tablodan kaldır
        self.message_table.removeRow(current_row)

        self.update_manual_count()
        self.log_status(f"Mesaj kaldırıldı: 0x{msg_id:X}")

    def clear_all_messages(self):
        """Tüm mesajları temizle"""
        reply = QMessageBox.question(
            self,
            "Onayla",
            "Tüm mesajlar silinecek. Emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logger_backend.clear_messages()
            self.message_table.setRowCount(0)
            self.update_manual_count()
            self.log_status("Tüm mesajlar temizlendi")

    def browse_log_folder(self):
        """Log klasörü seç"""
        folder = QFileDialog.getExistingDirectory(self, "Log Klasörü Seç")
        if folder:
            filename = self.log_filename_edit.text()
            full_path = os.path.join(folder, filename)
            self.log_filename_edit.setText(full_path)

    def start_logging(self):
        """Loglamayı başlat"""
        if not self.logger_backend.is_connected:
            QMessageBox.warning(self, "Hata", "Önce CAN cihazına bağlanın!")
            return

        # En az bir mesaj seçili mi?
        enabled_count = sum(1 for msg in self.logger_backend.messages.values() if msg.enabled)
        if enabled_count == 0:
            QMessageBox.warning(self, "Hata", "En az bir mesaj seçmelisiniz!")
            return

        filename = self.log_filename_edit.text().strip()
        if not filename:
            QMessageBox.warning(self, "Hata", "Log dosyası ismi giriniz!")
            return

        # .csv ekle
        if not filename.endswith(".csv"):
            filename += ".csv"

        interval = self.log_interval_spin.value()

        if self.logger_backend.start_logging(filename, interval):
            self.start_log_btn.setEnabled(False)
            self.stop_log_btn.setEnabled(True)
            self.log_status(f"Loglama başlatıldı: {enabled_count} mesaj, {interval*1000:.1f} ms aralık")
        else:
            QMessageBox.critical(self, "Hata", "Loglama başlatılamadı!")

    def stop_logging(self):
        """Loglamayı durdur"""
        self.logger_backend.stop_logging()
        self.start_log_btn.setEnabled(True)
        self.stop_log_btn.setEnabled(False)
        self.log_status("Loglama durduruldu")

    def on_message_received(self, msg_id: int, data: bytes, timestamp: float):
        """CAN mesajı alındı"""
        # Tabloda güncelle
        for row in range(self.message_table.rowCount()):
            item_id = self.message_table.item(row, 1).data(Qt.ItemDataRole.UserRole)
            if item_id == msg_id:
                # Son veriyi göster
                data_str = " ".join([f"{b:02X}" for b in data[:8]])
                self.message_table.item(row, 4).setText(data_str)
                break

    def update_manual_count(self):
        """Manuel mesaj sayacını güncelle"""
        count = len(self.logger_backend.messages)
        self.manual_count_label.setText(f"{count}/{self.MAX_MANUAL_MESSAGES}")

    def update_status(self):
        """Durum güncelle"""
        pass  # Timer callback

    def log_status(self, message: str):
        """Durum mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

    def closeEvent(self, event):
        """Pencere kapatılıyor"""
        # Loglamayı durdur
        if self.logger_backend.is_logging:
            self.logger_backend.stop_logging()

        # CAN bağlantısını kes
        if self.logger_backend.is_connected:
            self.logger_backend.disconnect_can()

        event.accept()


def main():
    """Ana program"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = QApplication(sys.argv)
    window = KvaserMessageLoggerGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

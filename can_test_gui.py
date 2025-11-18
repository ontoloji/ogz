"""
CAN Bus Test Arayüzü - Ana GUI
Modern PyQt6 tabanlı CAN test arayüzü
"""

import logging
import sys
import json
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog, QMessageBox,
    QSpinBox, QTabWidget, QStatusBar, QHeaderView, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QColor, QFont, QShortcut, QKeySequence

# CAN modülleri
from can_message_manager import CANMessage, CANMessageSender, CANMessageReceiver, ReceivedCANMessage
from dbc_manager import DBCManager
from can_logger import CANLogger

try:
    from canlib import canlib
    CANLIB_AVAILABLE = True
except ImportError:
    CANLIB_AVAILABLE = False


class CANTestGUI(QMainWindow):
    """CAN Bus Test Ana Arayüzü"""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # CAN bileşenleri
        self.can_channel = None
        self.message_sender: Optional[CANMessageSender] = None
        self.message_receiver: Optional[CANMessageReceiver] = None
        self.dbc_manager = DBCManager()
        self.can_logger = CANLogger()

        # Durum
        self.is_connected = False
        self.is_sending = False
        self.is_receiving = False

        # UI kurulum
        self.init_ui()
        self.setup_shortcuts()
        self.setup_timers()

        # Ayarları yükle
        self.load_settings()

        self.logger.info("CAN Test Arayüzü başlatıldı")

    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("CAN Bus Test Arayüzü - Kvaser Memorator 2xHS")
        self.setGeometry(100, 100, 1400, 900)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Üst panel: Bağlantı ayarları
        main_layout.addWidget(self.create_connection_panel())

        # Ana splitter (üst-alt bölme)
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Üst bölüm: Gönderme ve DBC
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.addWidget(self.create_send_panel())
        top_layout.addWidget(self.create_dbc_panel())
        main_splitter.addWidget(top_widget)

        # Alt bölüm: Alma ve decode
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.addWidget(self.create_filter_panel())

        # Tab widget (ham mesajlar vs decoded)
        self.message_tabs = QTabWidget()
        self.message_tabs.addTab(self.create_receive_panel(), "Ham Mesajlar")
        self.message_tabs.addTab(self.create_decode_panel(), "DBC Decode")
        bottom_layout.addWidget(self.message_tabs)

        main_splitter.addWidget(bottom_widget)
        main_layout.addWidget(main_splitter)

        # Durum çubuğu
        self.create_status_bar()

    def create_connection_panel(self) -> QGroupBox:
        """Bağlantı ayarları paneli"""
        group = QGroupBox("Bağlantı Ayarları")
        layout = QHBoxLayout()

        # CAN Kanal
        layout.addWidget(QLabel("CAN Kanal:"))
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["CH0 (Kanal 0)", "CH1 (Kanal 1)"])
        layout.addWidget(self.channel_combo)

        # Baud Rate
        layout.addWidget(QLabel("Baud Rate:"))
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems([
            "125 kbit/s",
            "250 kbit/s",
            "500 kbit/s",
            "1000 kbit/s"
        ])
        self.baudrate_combo.setCurrentIndex(2)  # 500 kbit/s varsayılan
        layout.addWidget(self.baudrate_combo)

        # Bağlan butonu
        self.connect_btn = QPushButton("Bağlan")
        self.connect_btn.clicked.connect(self.toggle_connection)
        self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        layout.addWidget(self.connect_btn)

        # Durum göstergesi
        layout.addWidget(QLabel("Durum:"))
        self.status_indicator = QLabel("● Bağlı Değil")
        self.status_indicator.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        layout.addWidget(self.status_indicator)

        layout.addStretch()
        group.setLayout(layout)
        return group

    def create_send_panel(self) -> QGroupBox:
        """Mesaj gönderme paneli"""
        group = QGroupBox("Mesaj Gönderme")
        layout = QVBoxLayout()

        # Üst: Mesaj oluşturma
        form_layout = QVBoxLayout()

        # CAN ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("CAN ID (Hex):"))
        self.can_id_input = QLineEdit("0x123")
        self.can_id_input.setMaximumWidth(150)
        id_layout.addWidget(self.can_id_input)
        id_layout.addStretch()
        form_layout.addLayout(id_layout)

        # DLC
        dlc_layout = QHBoxLayout()
        dlc_layout.addWidget(QLabel("DLC:"))
        self.dlc_spin = QSpinBox()
        self.dlc_spin.setRange(0, 8)
        self.dlc_spin.setValue(8)
        self.dlc_spin.setMaximumWidth(80)
        dlc_layout.addWidget(self.dlc_spin)
        dlc_layout.addStretch()
        form_layout.addLayout(dlc_layout)

        # Data
        data_layout = QHBoxLayout()
        data_layout.addWidget(QLabel("Data (Hex):"))
        self.data_inputs = []
        for i in range(8):
            byte_input = QLineEdit("00")
            byte_input.setMaximumWidth(40)
            byte_input.setMaxLength(2)
            self.data_inputs.append(byte_input)
            data_layout.addWidget(byte_input)
        form_layout.addLayout(data_layout)

        # Periyot
        period_layout = QHBoxLayout()
        period_layout.addWidget(QLabel("Gönderim Sıklığı (ms):"))
        self.period_spin = QSpinBox()
        self.period_spin.setRange(0, 10000)
        self.period_spin.setValue(100)
        self.period_spin.setMaximumWidth(100)
        self.period_spin.setSpecialValueText("Tek Seferlik")
        period_layout.addWidget(self.period_spin)
        period_layout.addStretch()
        form_layout.addLayout(period_layout)

        # Butonlar
        btn_layout = QHBoxLayout()
        self.add_msg_btn = QPushButton("Ekle")
        self.add_msg_btn.clicked.connect(self.add_message_to_list)
        btn_layout.addWidget(self.add_msg_btn)

        self.clear_msg_btn = QPushButton("Temizle")
        self.clear_msg_btn.clicked.connect(self.clear_message_form)
        btn_layout.addWidget(self.clear_msg_btn)
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)

        layout.addLayout(form_layout)

        # Gönderim listesi
        layout.addWidget(QLabel("Gönderim Listesi:"))
        self.send_table = QTableWidget()
        self.send_table.setColumnCount(5)
        self.send_table.setHorizontalHeaderLabels(["Aktif", "CAN ID", "Data", "Periyot (ms)", "Aksiyon"])
        self.send_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.send_table.setMaximumHeight(200)
        layout.addWidget(self.send_table)

        # Gönderim kontrol butonları
        control_layout = QHBoxLayout()
        self.start_send_btn = QPushButton("Gönderimi Başlat")
        self.start_send_btn.clicked.connect(self.toggle_sending)
        self.start_send_btn.setEnabled(False)
        control_layout.addWidget(self.start_send_btn)

        self.clear_list_btn = QPushButton("Listeyi Temizle")
        self.clear_list_btn.clicked.connect(self.clear_send_list)
        control_layout.addWidget(self.clear_list_btn)

        self.send_once_btn = QPushButton("Tek Seferlik Gönder")
        self.send_once_btn.clicked.connect(self.send_message_once)
        self.send_once_btn.setEnabled(False)
        control_layout.addWidget(self.send_once_btn)

        layout.addLayout(control_layout)

        group.setLayout(layout)
        return group

    def create_dbc_panel(self) -> QGroupBox:
        """DBC dosya yönetimi paneli"""
        group = QGroupBox("DBC Dosyası")
        layout = QVBoxLayout()

        # DBC yükleme
        load_layout = QHBoxLayout()
        self.load_dbc_btn = QPushButton("DBC Yükle...")
        self.load_dbc_btn.clicked.connect(self.load_dbc_file)
        load_layout.addWidget(self.load_dbc_btn)

        self.dbc_file_label = QLabel("Dosya yüklenmedi")
        self.dbc_file_label.setStyleSheet("QLabel { color: gray; font-style: italic; }")
        load_layout.addWidget(self.dbc_file_label)
        load_layout.addStretch()
        layout.addLayout(load_layout)

        # Mesaj listesi
        layout.addWidget(QLabel("Mesaj Listesi:"))
        self.dbc_message_list = QTableWidget()
        self.dbc_message_list.setColumnCount(3)
        self.dbc_message_list.setHorizontalHeaderLabels(["Mesaj Adı", "CAN ID", "Sinyaller"])
        self.dbc_message_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.dbc_message_list)

        # İzlemeye ekle butonu
        self.add_to_filter_btn = QPushButton("Seçili Mesajı İzlemeye Ekle")
        self.add_to_filter_btn.clicked.connect(self.add_dbc_message_to_filter)
        self.add_to_filter_btn.setEnabled(False)
        layout.addWidget(self.add_to_filter_btn)

        group.setLayout(layout)
        return group

    def create_filter_panel(self) -> QGroupBox:
        """Mesaj filtreleme paneli"""
        group = QGroupBox("Mesaj Filtreleme")
        layout = QHBoxLayout()

        # ID filtreleri
        layout.addWidget(QLabel("İzlenecek ID'ler (virgülle ayırın):"))
        self.filter_ids_input = QLineEdit("0x100, 0x200, 0x300")
        self.filter_ids_input.setPlaceholderText("Örn: 0x123, 0x456 (boş bırakın = tümü)")
        layout.addWidget(self.filter_ids_input)

        # Filtre uygula butonu
        self.apply_filter_btn = QPushButton("Filtre Uygula")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        self.apply_filter_btn.setEnabled(False)
        layout.addWidget(self.apply_filter_btn)

        group.setLayout(layout)
        return group

    def create_receive_panel(self) -> QWidget:
        """Alınan mesajlar paneli"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Mesaj tablosu
        self.receive_table = QTableWidget()
        self.receive_table.setColumnCount(5)
        self.receive_table.setHorizontalHeaderLabels(["Zaman", "CAN ID", "DLC", "Data", "Yön"])
        self.receive_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.receive_table.setMaximumHeight(300)
        layout.addWidget(self.receive_table)

        # Kontrol butonları
        btn_layout = QHBoxLayout()

        self.clear_rx_btn = QPushButton("Temizle")
        self.clear_rx_btn.clicked.connect(self.clear_receive_table)
        btn_layout.addWidget(self.clear_rx_btn)

        self.pause_rx_btn = QPushButton("Duraklat")
        self.pause_rx_btn.clicked.connect(self.toggle_pause_receive)
        self.pause_rx_btn.setCheckable(True)
        btn_layout.addWidget(self.pause_rx_btn)

        self.start_log_btn = QPushButton("Log Kaydet")
        self.start_log_btn.clicked.connect(self.toggle_logging)
        self.start_log_btn.setCheckable(True)
        btn_layout.addWidget(self.start_log_btn)

        self.export_log_btn = QPushButton("Export (CSV)")
        self.export_log_btn.clicked.connect(self.export_log)
        btn_layout.addWidget(self.export_log_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def create_decode_panel(self) -> QWidget:
        """DBC decode paneli"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Decode Edilmiş Mesajlar (DBC):"))

        self.decode_text = QTextEdit()
        self.decode_text.setReadOnly(True)
        self.decode_text.setFont(QFont("Courier New", 10))
        layout.addWidget(self.decode_text)

        # Temizle butonu
        clear_decode_btn = QPushButton("Temizle")
        clear_decode_btn.clicked.connect(lambda: self.decode_text.clear())
        layout.addWidget(clear_decode_btn)

        return widget

    def create_status_bar(self):
        """Durum çubuğu oluştur"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # İstatistik etiketleri
        self.tx_count_label = QLabel("TX: 0")
        self.rx_count_label = QLabel("RX: 0")
        self.bus_load_label = QLabel("Bus Load: 0%")

        self.status_bar.addPermanentWidget(self.tx_count_label)
        self.status_bar.addPermanentWidget(self.rx_count_label)
        self.status_bar.addPermanentWidget(self.bus_load_label)

        self.status_bar.showMessage("Hazır")

    def setup_shortcuts(self):
        """Kısayol tuşları"""
        # F5: Gönderimi başlat/durdur
        QShortcut(QKeySequence("F5"), self).activated.connect(self.toggle_sending)

        # F6: Loglama başlat/durdur
        QShortcut(QKeySequence("F6"), self).activated.connect(self.toggle_logging)

        # Ctrl+S: Log kaydet
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.export_log)

        # ESC: Acil durdur
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.emergency_stop)

    def setup_timers(self):
        """Zamanlayıcılar"""
        # UI güncelleme timer'ı
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start(100)  # 100ms

    # ===== Bağlantı Fonksiyonları =====

    def toggle_connection(self):
        """CAN bağlantısını aç/kapat"""
        if self.is_connected:
            self.disconnect_can()
        else:
            self.connect_can()

    def connect_can(self):
        """CAN'a bağlan"""
        if not CANLIB_AVAILABLE:
            QMessageBox.critical(self, "Hata", "Kvaser CANlib kütüphanesi bulunamadı!")
            return

        try:
            # Kanal numarası
            channel_idx = self.channel_combo.currentIndex()

            # Baud rate
            baudrate_map = {
                0: 125000,
                1: 250000,
                2: 500000,
                3: 1000000
            }
            bitrate = baudrate_map[self.baudrate_combo.currentIndex()]

            # Kanal aç
            self.can_channel = canlib.openChannel(channel_idx, canlib.canOPEN_ACCEPT_VIRTUAL)
            self.can_channel.setBusParams(bitrate)
            self.can_channel.busOn()

            # Sender ve Receiver oluştur
            self.message_sender = CANMessageSender(self.can_channel)
            self.message_receiver = CANMessageReceiver(self.can_channel)
            self.message_receiver.set_message_callback(self.on_message_received)

            # Alma işlemini başlat
            self.message_receiver.start_receiving()
            self.is_receiving = True

            self.is_connected = True
            self.status_indicator.setText("● Bağlı")
            self.status_indicator.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.connect_btn.setText("Bağlantıyı Kes")
            self.connect_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")

            # Butonları aktifleştir
            self.start_send_btn.setEnabled(True)
            self.send_once_btn.setEnabled(True)
            self.apply_filter_btn.setEnabled(True)

            self.status_bar.showMessage(f"CAN bağlantısı başarılı (Kanal {channel_idx}, {bitrate} bit/s)")
            self.logger.info(f"CAN bağlandı: Kanal {channel_idx}, {bitrate} bit/s")

        except Exception as e:
            QMessageBox.critical(self, "Bağlantı Hatası", f"CAN bağlantısı başarısız:\n{e}")
            self.logger.error(f"CAN bağlantı hatası: {e}")

    def disconnect_can(self):
        """CAN bağlantısını kes"""
        try:
            # Gönderimi durdur
            if self.is_sending and self.message_sender:
                self.message_sender.stop_sending()
                self.is_sending = False

            # Almayı durdur
            if self.is_receiving and self.message_receiver:
                self.message_receiver.stop_receiving()
                self.is_receiving = False

            # Kanal kapat
            if self.can_channel:
                self.can_channel.busOff()
                self.can_channel.close()

            self.is_connected = False
            self.status_indicator.setText("● Bağlı Değil")
            self.status_indicator.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            self.connect_btn.setText("Bağlan")
            self.connect_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")

            # Butonları devre dışı bırak
            self.start_send_btn.setEnabled(False)
            self.send_once_btn.setEnabled(False)
            self.apply_filter_btn.setEnabled(False)

            self.status_bar.showMessage("CAN bağlantısı kesildi")
            self.logger.info("CAN bağlantısı kesildi")

        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Bağlantı kesme hatası:\n{e}")
            self.logger.error(f"Bağlantı kesme hatası: {e}")

    # ===== Mesaj Gönderme Fonksiyonları =====

    def add_message_to_list(self):
        """Formdaki mesajı listeye ekle"""
        try:
            # CAN ID parse
            can_id_str = self.can_id_input.text().strip()
            if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
                can_id = int(can_id_str, 16)
            else:
                can_id = int(can_id_str)

            # Data parse
            data_bytes = []
            for i in range(self.dlc_spin.value()):
                byte_str = self.data_inputs[i].text().strip()
                if not byte_str:
                    byte_str = "00"
                data_bytes.append(int(byte_str, 16))

            data = bytes(data_bytes)
            dlc = self.dlc_spin.value()
            period = self.period_spin.value()

            # Mesaj oluştur
            message = CANMessage(
                can_id=can_id,
                data=data,
                dlc=dlc,
                period_ms=period,
                enabled=True,
                name=f"MSG_0x{can_id:X}"
            )

            # Tabloya ekle
            row = self.send_table.rowCount()
            self.send_table.insertRow(row)

            # Checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.send_table.setCellWidget(row, 0, checkbox)

            # CAN ID
            self.send_table.setItem(row, 1, QTableWidgetItem(f"0x{can_id:X}"))

            # Data
            data_str = ' '.join(f'{b:02X}' for b in data)
            self.send_table.setItem(row, 2, QTableWidgetItem(data_str))

            # Periyot
            period_str = f"{period}" if period > 0 else "Tek"
            self.send_table.setItem(row, 3, QTableWidgetItem(period_str))

            # Sil butonu
            delete_btn = QPushButton("Sil")
            delete_btn.clicked.connect(lambda: self.remove_message_from_list(row))
            self.send_table.setCellWidget(row, 4, delete_btn)

            # Sender'a ekle (bağlıysa)
            if self.is_connected and self.message_sender:
                self.message_sender.add_message(message)

            self.status_bar.showMessage(f"Mesaj eklendi: 0x{can_id:X}")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Mesaj eklenemedi:\n{e}")

    def remove_message_from_list(self, row: int):
        """Mesajı listeden çıkar"""
        if self.message_sender:
            self.message_sender.remove_message(row)
        self.send_table.removeRow(row)
        self.status_bar.showMessage(f"Mesaj silindi (satır {row})")

    def clear_send_list(self):
        """Gönderim listesini temizle"""
        self.send_table.setRowCount(0)
        if self.message_sender:
            self.message_sender.clear_messages()
        self.status_bar.showMessage("Gönderim listesi temizlendi")

    def clear_message_form(self):
        """Mesaj formunu temizle"""
        self.can_id_input.setText("0x123")
        self.dlc_spin.setValue(8)
        for input_field in self.data_inputs:
            input_field.setText("00")
        self.period_spin.setValue(100)

    def send_message_once(self):
        """Tek seferlik mesaj gönder"""
        if not self.is_connected or not self.message_sender:
            return

        try:
            # Formdaki mesajı al
            can_id_str = self.can_id_input.text().strip()
            if can_id_str.startswith('0x') or can_id_str.startswith('0X'):
                can_id = int(can_id_str, 16)
            else:
                can_id = int(can_id_str)

            data_bytes = []
            for i in range(self.dlc_spin.value()):
                byte_str = self.data_inputs[i].text().strip()
                if not byte_str:
                    byte_str = "00"
                data_bytes.append(int(byte_str, 16))

            message = CANMessage(
                can_id=can_id,
                data=bytes(data_bytes),
                dlc=self.dlc_spin.value(),
                period_ms=0
            )

            # Gönder
            if self.message_sender.send_once(message):
                self.status_bar.showMessage(f"Mesaj gönderildi: 0x{can_id:X}")
            else:
                self.status_bar.showMessage("Mesaj gönderilemedi!")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Mesaj gönderilemedi:\n{e}")

    def toggle_sending(self):
        """Periyodik gönderimi başlat/durdur"""
        if not self.is_connected or not self.message_sender:
            return

        if self.is_sending:
            # Durdur
            self.message_sender.stop_sending()
            self.is_sending = False
            self.start_send_btn.setText("Gönderimi Başlat")
            self.start_send_btn.setStyleSheet("")
            self.status_bar.showMessage("Gönderim durduruldu")
        else:
            # Başlat - mesajları sender'a ekle
            self.message_sender.clear_messages()
            for row in range(self.send_table.rowCount()):
                checkbox = self.send_table.cellWidget(row, 0)
                if not checkbox.isChecked():
                    continue

                can_id_str = self.send_table.item(row, 1).text()
                can_id = int(can_id_str, 16)

                data_str = self.send_table.item(row, 2).text()
                data = bytes.fromhex(data_str.replace(' ', ''))

                period_str = self.send_table.item(row, 3).text()
                period = 0 if period_str == "Tek" else int(period_str)

                message = CANMessage(
                    can_id=can_id,
                    data=data,
                    dlc=len(data),
                    period_ms=period,
                    enabled=True
                )
                self.message_sender.add_message(message)

            self.message_sender.start_sending()
            self.is_sending = True
            self.start_send_btn.setText("Gönderimi Durdur")
            self.start_send_btn.setStyleSheet("QPushButton { background-color: #ff9800; }")
            self.status_bar.showMessage("Gönderim başlatıldı")

    # ===== DBC Fonksiyonları =====

    def load_dbc_file(self):
        """DBC dosyası yükle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "DBC Dosyası Seç",
            "",
            "DBC Dosyaları (*.dbc);;Tüm Dosyalar (*)"
        )

        if not file_path:
            return

        if self.dbc_manager.load_dbc(file_path):
            self.dbc_file_label.setText(Path(file_path).name)
            self.dbc_file_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            self.add_to_filter_btn.setEnabled(True)

            # Mesaj listesini güncelle
            self.update_dbc_message_list()

            QMessageBox.information(self, "Başarılı", f"DBC dosyası yüklendi:\n{file_path}")
        else:
            QMessageBox.critical(self, "Hata", "DBC dosyası yüklenemedi!")

    def update_dbc_message_list(self):
        """DBC mesaj listesini güncelle"""
        self.dbc_message_list.setRowCount(0)

        for msg in self.dbc_manager.get_messages():
            row = self.dbc_message_list.rowCount()
            self.dbc_message_list.insertRow(row)

            self.dbc_message_list.setItem(row, 0, QTableWidgetItem(msg.name))
            self.dbc_message_list.setItem(row, 1, QTableWidgetItem(f"0x{msg.can_id:X}"))
            self.dbc_message_list.setItem(row, 2, QTableWidgetItem(str(len(msg.signals))))

    def add_dbc_message_to_filter(self):
        """Seçili DBC mesajını filtreye ekle"""
        current_row = self.dbc_message_list.currentRow()
        if current_row < 0:
            return

        can_id_str = self.dbc_message_list.item(current_row, 1).text()

        # Mevcut filtreye ekle
        current_filter = self.filter_ids_input.text().strip()
        if current_filter:
            new_filter = current_filter + ", " + can_id_str
        else:
            new_filter = can_id_str

        self.filter_ids_input.setText(new_filter)
        self.status_bar.showMessage(f"Filtre eklendi: {can_id_str}")

    # ===== Mesaj Alma Fonksiyonları =====

    def apply_filters(self):
        """Filtreleri uygula"""
        if not self.message_receiver:
            return

        # ID filtrelerini parse et
        filter_text = self.filter_ids_input.text().strip()
        if not filter_text:
            # Boş = tüm ID'ler
            self.message_receiver.set_id_filters([])
            self.status_bar.showMessage("Filtre kaldırıldı (tüm mesajlar izleniyor)")
            return

        id_list = []
        for id_str in filter_text.split(','):
            id_str = id_str.strip()
            if id_str:
                try:
                    if id_str.startswith('0x') or id_str.startswith('0X'):
                        can_id = int(id_str, 16)
                    else:
                        can_id = int(id_str)
                    id_list.append(can_id)
                except:
                    pass

        self.message_receiver.set_id_filters(id_list)
        self.status_bar.showMessage(f"Filtre uygulandı: {len(id_list)} ID izleniyor")

    def on_message_received(self, message: ReceivedCANMessage):
        """Mesaj alındığında callback"""
        # Duraklama kontrolü
        if self.pause_rx_btn.isChecked():
            return

        # Tabloya ekle (max 1000 satır)
        if self.receive_table.rowCount() >= 1000:
            self.receive_table.removeRow(0)

        row = self.receive_table.rowCount()
        self.receive_table.insertRow(row)

        # Zaman
        from datetime import datetime
        dt = datetime.fromtimestamp(message.timestamp)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]
        self.receive_table.setItem(row, 0, QTableWidgetItem(time_str))

        # CAN ID
        id_item = QTableWidgetItem(f"0x{message.can_id:X}")
        id_item.setBackground(QColor(200, 255, 200))  # Yeşil
        self.receive_table.setItem(row, 1, id_item)

        # DLC
        self.receive_table.setItem(row, 2, QTableWidgetItem(str(message.dlc)))

        # Data
        data_str = ' '.join(f'{b:02X}' for b in message.data[:message.dlc])
        self.receive_table.setItem(row, 3, QTableWidgetItem(data_str))

        # Yön
        dir_item = QTableWidgetItem(message.direction)
        dir_item.setForeground(QColor(0, 150, 0) if message.direction == "RX" else QColor(0, 0, 200))
        self.receive_table.setItem(row, 4, dir_item)

        # Scroll to bottom
        self.receive_table.scrollToBottom()

        # DBC decode (varsa)
        if self.dbc_manager.is_loaded():
            decoded = self.dbc_manager.decode_message(message.can_id, message.data)
            if decoded:
                self.append_decoded_message(message.can_id, decoded)

        # Log kaydet
        if self.can_logger.is_logging:
            self.can_logger.log_message(message)

    def append_decoded_message(self, can_id: int, decoded: dict):
        """Decode edilmiş mesajı göster"""
        dbc_msg = self.dbc_manager.get_message_by_id(can_id)
        if not dbc_msg:
            return

        text = f"\n[{dbc_msg.name} (0x{can_id:X})]:\n"
        for signal_name, value in decoded.items():
            # Birim bul
            signal = dbc_msg.get_signal(signal_name)
            unit = signal.unit if signal else ""
            text += f"  ├─ {signal_name}: {value} {unit}\n"

        self.decode_text.append(text)

        # Max uzunluk kontrolü (son 10000 karakter)
        if len(self.decode_text.toPlainText()) > 10000:
            cursor = self.decode_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.Start)
            cursor.movePosition(cursor.MoveOperation.NextCharacter, cursor.MoveMode.KeepAnchor, 1000)
            cursor.removeSelectedText()

    def clear_receive_table(self):
        """Alınan mesajlar tablosunu temizle"""
        self.receive_table.setRowCount(0)
        if self.message_receiver:
            self.message_receiver.clear_buffer()
        self.status_bar.showMessage("Alınan mesajlar temizlendi")

    def toggle_pause_receive(self):
        """Mesaj almayı duraklat/devam"""
        if self.pause_rx_btn.isChecked():
            self.pause_rx_btn.setText("Devam")
            self.status_bar.showMessage("Mesaj alma duraklatıldı")
        else:
            self.pause_rx_btn.setText("Duraklat")
            self.status_bar.showMessage("Mesaj alma devam ediyor")

    # ===== Loglama Fonksiyonları =====

    def toggle_logging(self):
        """Loglama başlat/durdur"""
        if self.can_logger.is_logging:
            # Durdur
            self.can_logger.stop_logging()
            self.start_log_btn.setText("Log Kaydet")
            self.start_log_btn.setChecked(False)
            self.status_bar.showMessage("Loglama durduruldu")
            QMessageBox.information(self, "Log Kaydedildi",
                                   f"Log dosyası kaydedildi:\n{self.can_logger.current_log_file}")
        else:
            # Başlat
            log_file = self.can_logger.start_logging()
            self.start_log_btn.setText("Loglamayı Durdur")
            self.start_log_btn.setChecked(True)
            self.status_bar.showMessage(f"Loglama başlatıldı: {log_file}")

    def export_log(self):
        """Logu export et"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Log Dosyasını Kaydet",
            f"CAN_LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Dosyaları (*.csv);;TXT Dosyaları (*.txt)"
        )

        if not file_path:
            return

        messages = self.message_receiver.get_messages() if self.message_receiver else []

        if file_path.endswith('.txt'):
            success = self.can_logger.export_to_txt(file_path, messages)
        else:
            success = self.can_logger.export_to_csv(file_path, messages)

        if success:
            QMessageBox.information(self, "Başarılı", f"Log export edildi:\n{file_path}")
        else:
            QMessageBox.warning(self, "Hata", "Log export edilemedi!")

    # ===== Yardımcı Fonksiyonlar =====

    def emergency_stop(self):
        """Acil durdurma"""
        if self.is_sending:
            self.toggle_sending()
        self.status_bar.showMessage("ACİL DURDURMA!")
        QMessageBox.warning(self, "Acil Durdurma", "Tüm gönderim işlemleri durduruldu!")

    def update_ui(self):
        """UI'yi güncelle (timer callback)"""
        if not self.is_connected:
            return

        # İstatistikleri güncelle
        if self.message_sender:
            stats = self.message_sender.get_statistics()
            self.tx_count_label.setText(f"TX: {stats['sent_count']}")

        if self.message_receiver:
            stats = self.message_receiver.get_statistics()
            self.rx_count_label.setText(f"RX: {stats['received_count']}")

    def load_settings(self):
        """Ayarları yükle"""
        settings_file = Path("can_test_settings.json")
        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Ayarları uygula
            if 'channel' in settings:
                self.channel_combo.setCurrentIndex(settings['channel'])
            if 'baudrate' in settings:
                self.baudrate_combo.setCurrentIndex(settings['baudrate'])
            if 'last_dbc' in settings and Path(settings['last_dbc']).exists():
                self.dbc_manager.load_dbc(settings['last_dbc'])
                self.dbc_file_label.setText(Path(settings['last_dbc']).name)
                self.update_dbc_message_list()

            self.logger.info("Ayarlar yüklendi")
        except Exception as e:
            self.logger.error(f"Ayar yükleme hatası: {e}")

    def save_settings(self):
        """Ayarları kaydet"""
        settings = {
            'channel': self.channel_combo.currentIndex(),
            'baudrate': self.baudrate_combo.currentIndex(),
            'last_dbc': self.dbc_manager.file_path if self.dbc_manager.is_loaded() else ""
        }

        try:
            with open("can_test_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            self.logger.info("Ayarlar kaydedildi")
        except Exception as e:
            self.logger.error(f"Ayar kaydetme hatası: {e}")

    def closeEvent(self, event):
        """Pencere kapatılırken"""
        # Bağlantıyı kes
        if self.is_connected:
            self.disconnect_can()

        # Ayarları kaydet
        self.save_settings()

        event.accept()


def main():
    """Ana program"""
    # Logging ayarla
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('can_test_gui.log'),
            logging.StreamHandler()
        ]
    )

    # PyQt uygulaması
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Ana pencere
    window = CANTestGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

"""
Ana GUI Penceresi
Windows CAN Bus Analiz Aracı
"""
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QTabWidget, QGroupBox, QLabel,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox,
    QSplitter, QCheckBox, QTextEdit, QHeaderView, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor
import logging

from ..core.can_handler import CANHandler
from ..core.dbc_parser import DBCParser
from ..core.log_reader import LogReader
from ..core.data_exporter import DataExporter
from ..utils.helpers import (
    format_can_id, format_data_hex,
    ensure_directory_exists, get_timestamp_string
)
from .plot_widget import PlotWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Ana uygulama penceresi.
    CAN Bus analiz ve görselleştirme özellikleri.
    """

    def __init__(self):
        """Ana pencereyi başlat."""
        super().__init__()

        # Core bileşenler
        self.can_handler = CANHandler()
        self.dbc_parser = DBCParser()
        self.log_reader = LogReader()
        self.data_exporter = DataExporter()

        # Veri saklama
        self.received_messages = []
        self.filtered_can_ids = set()
        self.max_table_rows = 1000

        # Timer'lar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_message_table)

        # UI oluştur
        self._setup_ui()
        self._setup_connections()

        # Durum
        self.setWindowTitle("CAN Bus Analyzer - Windows")
        self.resize(1400, 900)

        logger.info("Ana pencere oluşturuldu")

    def _setup_ui(self):
        """UI bileşenlerini oluştur."""
        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Üst bölüm: Bağlantı ve DBC
        main_layout.addWidget(self._create_connection_group())

        # Orta bölüm: Tab widget
        self.tab_widget = QTabWidget()

        # Tab 1: Real-time CAN Messages
        self.tab_widget.addTab(self._create_realtime_tab(), "Real-Time CAN")

        # Tab 2: Log File Analysis
        self.tab_widget.addTab(self._create_log_analysis_tab(), "Log Analizi")

        # Tab 3: Signal Plotting
        self.tab_widget.addTab(self._create_plotting_tab(), "Grafik")

        # Tab 4: Export
        self.tab_widget.addTab(self._create_export_tab(), "Export")

        main_layout.addWidget(self.tab_widget)

        # Alt bölüm: Durum çubuğu
        self.statusBar().showMessage("Hazır")

        # Menu bar
        self._create_menu_bar()

    def _create_connection_group(self) -> QGroupBox:
        """
        Bağlantı ayarları grubu.

        Returns:
            QGroupBox: Bağlantı grubu widget'ı
        """
        group = QGroupBox("CAN Bağlantısı ve DBC")
        layout = QHBoxLayout()

        # CAN Interface
        layout.addWidget(QLabel("Arayüz:"))
        self.combo_interface = QComboBox()
        self.combo_interface.addItems(["kvaser", "socketcan", "pcan", "vector"])
        self.combo_interface.setCurrentText("kvaser")
        layout.addWidget(self.combo_interface)

        # CAN Channel
        layout.addWidget(QLabel("Kanal:"))
        self.spin_channel = QSpinBox()
        self.spin_channel.setRange(0, 15)
        layout.addWidget(self.spin_channel)

        # Bitrate
        layout.addWidget(QLabel("Bitrate:"))
        self.combo_bitrate = QComboBox()
        self.combo_bitrate.addItems(["125000", "250000", "500000", "1000000"])
        self.combo_bitrate.setCurrentText("500000")
        layout.addWidget(self.combo_bitrate)

        # Connect button
        self.btn_connect = QPushButton("Bağlan")
        self.btn_connect.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_connect.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.btn_connect)

        layout.addWidget(QLabel("|"))

        # DBC File
        layout.addWidget(QLabel("DBC:"))
        self.line_dbc_path = QLineEdit()
        self.line_dbc_path.setPlaceholderText("DBC dosyası seçin...")
        self.line_dbc_path.setReadOnly(True)
        layout.addWidget(self.line_dbc_path)

        self.btn_load_dbc = QPushButton("DBC Yükle")
        self.btn_load_dbc.clicked.connect(self._on_load_dbc)
        layout.addWidget(self.btn_load_dbc)

        layout.addStretch()

        # Status indicator
        self.label_connection_status = QLabel("● Bağlı Değil")
        self.label_connection_status.setStyleSheet("color: red;")
        layout.addWidget(self.label_connection_status)

        group.setLayout(layout)
        return group

    def _create_realtime_tab(self) -> QWidget:
        """
        Real-time CAN mesaj tab'ı oluştur.

        Returns:
            QWidget: Tab widget'ı
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Kontrol paneli
        control_layout = QHBoxLayout()

        self.btn_start_receiving = QPushButton("Almaya Başla")
        self.btn_start_receiving.clicked.connect(self._on_start_receiving)
        self.btn_start_receiving.setEnabled(False)
        control_layout.addWidget(self.btn_start_receiving)

        self.btn_stop_receiving = QPushButton("Dur")
        self.btn_stop_receiving.clicked.connect(self._on_stop_receiving)
        self.btn_stop_receiving.setEnabled(False)
        control_layout.addWidget(self.btn_stop_receiving)

        self.btn_clear_table = QPushButton("Temizle")
        self.btn_clear_table.clicked.connect(self._on_clear_table)
        control_layout.addWidget(self.btn_clear_table)

        control_layout.addWidget(QLabel("ID Filtresi:"))
        self.line_id_filter = QLineEdit()
        self.line_id_filter.setPlaceholderText("0x123, 0x456 (virgülle ayırın)")
        control_layout.addWidget(self.line_id_filter)

        self.btn_apply_filter = QPushButton("Filtreyi Uygula")
        self.btn_apply_filter.clicked.connect(self._on_apply_filter)
        control_layout.addWidget(self.btn_apply_filter)

        control_layout.addStretch()

        self.label_message_count = QLabel("Mesaj Sayısı: 0")
        control_layout.addWidget(self.label_message_count)

        layout.addLayout(control_layout)

        # Mesaj tablosu
        self.table_messages = QTableWidget()
        self.table_messages.setColumnCount(7)
        self.table_messages.setHorizontalHeaderLabels([
            "Zaman", "CAN ID", "DLC", "Veri (Hex)", "Mesaj Adı", "Decode", "Kanal"
        ])
        self.table_messages.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_messages.setAlternatingRowColors(True)
        layout.addWidget(self.table_messages)

        return widget

    def _create_log_analysis_tab(self) -> QWidget:
        """
        Log dosya analiz tab'ı oluştur.

        Returns:
            QWidget: Tab widget'ı
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Dosya seçim
        file_layout = QHBoxLayout()

        file_layout.addWidget(QLabel("Log Dosyası:"))
        self.line_log_path = QLineEdit()
        self.line_log_path.setPlaceholderText("ASC veya BLF dosyası seçin...")
        self.line_log_path.setReadOnly(True)
        file_layout.addWidget(self.line_log_path)

        self.btn_load_log = QPushButton("Log Yükle")
        self.btn_load_log.clicked.connect(self._on_load_log)
        file_layout.addWidget(self.btn_load_log)

        layout.addLayout(file_layout)

        # Log bilgileri
        self.text_log_info = QTextEdit()
        self.text_log_info.setMaximumHeight(100)
        self.text_log_info.setReadOnly(True)
        layout.addWidget(self.text_log_info)

        # Progress bar
        self.progress_log = QProgressBar()
        self.progress_log.setVisible(False)
        layout.addWidget(self.progress_log)

        # Log mesaj tablosu
        self.table_log_messages = QTableWidget()
        self.table_log_messages.setColumnCount(6)
        self.table_log_messages.setHorizontalHeaderLabels([
            "Zaman", "CAN ID", "DLC", "Veri (Hex)", "Mesaj Adı", "Decode"
        ])
        self.table_log_messages.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self.table_log_messages)

        return widget

    def _create_plotting_tab(self) -> QWidget:
        """
        Grafik çizim tab'ı oluştur.

        Returns:
            QWidget: Tab widget'ı
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Sinyal seçim paneli
        signal_layout = QHBoxLayout()

        signal_layout.addWidget(QLabel("Sinyaller:"))
        self.combo_available_signals = QComboBox()
        self.combo_available_signals.setMinimumWidth(300)
        signal_layout.addWidget(self.combo_available_signals)

        self.btn_add_signal = QPushButton("Grafiğe Ekle")
        self.btn_add_signal.clicked.connect(self._on_add_signal_to_plot)
        signal_layout.addWidget(self.btn_add_signal)

        self.btn_remove_signal = QPushButton("Grafikten Çıkar")
        self.btn_remove_signal.clicked.connect(self._on_remove_signal_from_plot)
        signal_layout.addWidget(self.btn_remove_signal)

        signal_layout.addStretch()

        self.check_auto_update = QCheckBox("Otomatik Güncelle")
        self.check_auto_update.stateChanged.connect(self._on_auto_update_changed)
        signal_layout.addWidget(self.check_auto_update)

        layout.addLayout(signal_layout)

        # Plot widget
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)

        return widget

    def _create_export_tab(self) -> QWidget:
        """
        Export tab'ı oluştur.

        Returns:
            QWidget: Tab widget'ı
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Export seçenekleri
        options_group = QGroupBox("Export Seçenekleri")
        options_layout = QVBoxLayout()

        self.check_export_decoded = QCheckBox("Decode edilmiş sinyalleri dahil et")
        self.check_export_decoded.setChecked(True)
        options_layout.addWidget(self.check_export_decoded)

        self.check_export_stats = QCheckBox("İstatistikleri dahil et (sadece Excel)")
        self.check_export_stats.setChecked(True)
        options_layout.addWidget(self.check_export_stats)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Export butonları
        button_layout = QHBoxLayout()

        self.btn_export_csv = QPushButton("CSV'ye Export Et")
        self.btn_export_csv.clicked.connect(lambda: self._on_export_data('csv'))
        button_layout.addWidget(self.btn_export_csv)

        self.btn_export_excel = QPushButton("Excel'e Export Et")
        self.btn_export_excel.clicked.connect(lambda: self._on_export_data('excel'))
        button_layout.addWidget(self.btn_export_excel)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Export log alanı
        layout.addWidget(QLabel("Export Geçmişi:"))
        self.text_export_log = QTextEdit()
        self.text_export_log.setReadOnly(True)
        layout.addWidget(self.text_export_log)

        layout.addStretch()

        return widget

    def _create_menu_bar(self):
        """Menu bar oluştur."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("Dosya")

        action_exit = file_menu.addAction("Çıkış")
        action_exit.triggered.connect(self.close)

        # Help menu
        help_menu = menubar.addMenu("Yardım")

        action_about = help_menu.addAction("Hakkında")
        action_about.triggered.connect(self._show_about)

    def _setup_connections(self):
        """Signal-slot bağlantılarını kur."""
        pass

    # Event Handlers

    def _on_connect_clicked(self):
        """CAN bağlantısı butonuna tıklandığında."""
        if not self.can_handler.is_connected:
            # Bağlan
            try:
                interface = self.combo_interface.currentText()
                channel = self.spin_channel.value()
                bitrate = int(self.combo_bitrate.currentText())

                success = self.can_handler.connect(
                    channel=channel,
                    bitrate=bitrate,
                    interface=interface
                )

                if success:
                    self.btn_connect.setText("Bağlantıyı Kes")
                    self.btn_connect.setStyleSheet("background-color: #f44336; color: white;")
                    self.label_connection_status.setText("● Bağlı")
                    self.label_connection_status.setStyleSheet("color: green;")
                    self.btn_start_receiving.setEnabled(True)
                    self.statusBar().showMessage(f"CAN Bus'a bağlandı: {interface}, Kanal {channel}")

            except Exception as e:
                QMessageBox.critical(self, "Bağlantı Hatası", str(e))
                logger.error(f"Bağlantı hatası: {str(e)}")

        else:
            # Bağlantıyı kes
            self._on_stop_receiving()
            self.can_handler.disconnect()

            self.btn_connect.setText("Bağlan")
            self.btn_connect.setStyleSheet("background-color: #4CAF50; color: white;")
            self.label_connection_status.setText("● Bağlı Değil")
            self.label_connection_status.setStyleSheet("color: red;")
            self.btn_start_receiving.setEnabled(False)
            self.statusBar().showMessage("CAN bağlantısı kesildi")

    def _on_load_dbc(self):
        """DBC dosyası yükle."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "DBC Dosyası Seç",
            "",
            "DBC Dosyaları (*.dbc);;Tüm Dosyalar (*.*)"
        )

        if file_path:
            try:
                self.dbc_parser.load_dbc(file_path)
                self.line_dbc_path.setText(file_path)
                self.statusBar().showMessage(f"DBC yüklendi: {Path(file_path).name}")

                # Sinyal listesini güncelle
                self._update_signal_list()

                QMessageBox.information(
                    self,
                    "DBC Yüklendi",
                    f"DBC dosyası başarıyla yüklendi.\n\n"
                    f"Mesaj sayısı: {len(self.dbc_parser.get_all_messages())}\n"
                    f"Sinyal sayısı: {len(self.dbc_parser.get_all_signals())}"
                )

            except Exception as e:
                QMessageBox.critical(self, "DBC Yükleme Hatası", str(e))

    def _on_start_receiving(self):
        """CAN mesaj alımını başlat."""
        if not self.can_handler.is_connected:
            QMessageBox.warning(self, "Uyarı", "Önce CAN Bus'a bağlanın")
            return

        try:
            # Callback ekle
            self.can_handler.add_callback(self._on_can_message_received)

            # Almaya başla
            self.can_handler.start_receiving()

            # Timer başlat
            self.update_timer.start(100)  # 100ms

            # UI güncelle
            self.btn_start_receiving.setEnabled(False)
            self.btn_stop_receiving.setEnabled(True)
            self.statusBar().showMessage("CAN mesaj alımı başladı")

        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def _on_stop_receiving(self):
        """CAN mesaj alımını durdur."""
        if self.can_handler.is_receiving:
            self.can_handler.stop_receiving()

        self.update_timer.stop()

        self.btn_start_receiving.setEnabled(True)
        self.btn_stop_receiving.setEnabled(False)
        self.statusBar().showMessage("CAN mesaj alımı durduruldu")

    def _on_can_message_received(self, msg_dict: dict):
        """
        CAN mesajı alındığında callback.

        Args:
            msg_dict: Mesaj bilgileri
        """
        # Filtre kontrolü
        if self.filtered_can_ids:
            if msg_dict['arbitration_id'] not in self.filtered_can_ids:
                return

        # Mesajı kaydet
        self.received_messages.append(msg_dict)

        # Bellek yönetimi
        if len(self.received_messages) > self.max_table_rows:
            self.received_messages = self.received_messages[-self.max_table_rows:]

        # Decode et
        if self.dbc_parser.is_loaded:
            decoded = self.dbc_parser.decode_message(
                msg_dict['arbitration_id'],
                msg_dict['data']
            )

            if decoded and self.check_auto_update.isChecked():
                # Grafik güncelle
                for signal_name, value in decoded['signals'].items():
                    if signal_name in self.plot_widget.get_active_signals():
                        self.plot_widget.update_signal(
                            signal_name,
                            msg_dict['timestamp'],
                            value
                        )

    def _update_message_table(self):
        """Mesaj tablosunu güncelle."""
        # Son mesajları al
        recent_messages = self.received_messages[-100:]

        # Tablo boyutunu ayarla
        self.table_messages.setRowCount(len(recent_messages))

        for i, msg in enumerate(recent_messages):
            # Zaman
            time_item = QTableWidgetItem(f"{msg['timestamp']:.3f}")
            self.table_messages.setItem(i, 0, time_item)

            # CAN ID
            can_id_item = QTableWidgetItem(f"0x{msg['arbitration_id']:03X}")
            self.table_messages.setItem(i, 1, can_id_item)

            # DLC
            dlc_item = QTableWidgetItem(str(msg['dlc']))
            self.table_messages.setItem(i, 2, dlc_item)

            # Veri
            data_hex = ' '.join([f"{b:02X}" for b in msg['data']])
            data_item = QTableWidgetItem(data_hex)
            self.table_messages.setItem(i, 3, data_item)

            # Decode bilgileri
            if self.dbc_parser.is_loaded:
                decoded = self.dbc_parser.decode_message(msg['arbitration_id'], msg['data'])
                if decoded:
                    msg_name_item = QTableWidgetItem(decoded['message_name'])
                    self.table_messages.setItem(i, 4, msg_name_item)

                    signals_str = ', '.join([f"{k}={v}" for k, v in decoded['signals'].items()])
                    signals_item = QTableWidgetItem(signals_str)
                    self.table_messages.setItem(i, 5, signals_item)
                else:
                    self.table_messages.setItem(i, 4, QTableWidgetItem("Unknown"))
            else:
                self.table_messages.setItem(i, 4, QTableWidgetItem("-"))

            # Kanal
            channel_item = QTableWidgetItem(str(msg.get('channel', '-')))
            self.table_messages.setItem(i, 6, channel_item)

        # Scroll to bottom
        self.table_messages.scrollToBottom()

        # Mesaj sayısını güncelle
        self.label_message_count.setText(f"Mesaj Sayısı: {len(self.received_messages)}")

    def _on_clear_table(self):
        """Mesaj tablosunu temizle."""
        self.received_messages.clear()
        self.table_messages.setRowCount(0)
        self.label_message_count.setText("Mesaj Sayısı: 0")

    def _on_apply_filter(self):
        """ID filtresini uygula."""
        filter_text = self.line_id_filter.text().strip()

        if not filter_text:
            self.filtered_can_ids.clear()
            self.statusBar().showMessage("Filtre kaldırıldı")
            return

        try:
            # ID'leri parse et
            id_strings = filter_text.split(',')
            self.filtered_can_ids.clear()

            for id_str in id_strings:
                id_str = id_str.strip()
                if id_str.startswith('0x') or id_str.startswith('0X'):
                    can_id = int(id_str, 16)
                else:
                    can_id = int(id_str)

                self.filtered_can_ids.add(can_id)

            self.statusBar().showMessage(f"Filtre uygulandı: {len(self.filtered_can_ids)} ID")

        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz ID formatı")

    def _on_load_log(self):
        """Log dosyası yükle."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Log Dosyası Seç",
            "",
            "Log Dosyaları (*.asc *.blf *.log);;Tüm Dosyalar (*.*)"
        )

        if file_path:
            try:
                self.progress_log.setVisible(True)
                self.progress_log.setValue(0)

                # Log yükle
                self.log_reader.load_file(file_path)
                self.line_log_path.setText(file_path)

                # Bilgileri göster
                info = self.log_reader.get_file_info()
                info_text = (
                    f"Dosya: {info['file_name']}\n"
                    f"Format: {info['file_format']}\n"
                    f"Mesaj Sayısı: {info['message_count']}\n"
                    f"Unique ID'ler: {info['unique_ids']}\n"
                    f"Süre: {info['duration']:.2f} saniye"
                )
                self.text_log_info.setText(info_text)

                # Tabloyu doldur
                self._populate_log_table()

                self.progress_log.setValue(100)
                self.statusBar().showMessage(f"Log yüklendi: {info['file_name']}")

            except Exception as e:
                QMessageBox.critical(self, "Log Yükleme Hatası", str(e))
            finally:
                self.progress_log.setVisible(False)

    def _populate_log_table(self):
        """Log mesaj tablosunu doldur."""
        messages = self.log_reader.get_messages(count=1000)

        self.table_log_messages.setRowCount(len(messages))

        for i, msg in enumerate(messages):
            # Aynı format ile doldur
            time_item = QTableWidgetItem(f"{msg['timestamp']:.3f}")
            self.table_log_messages.setItem(i, 0, time_item)

            can_id_item = QTableWidgetItem(f"0x{msg['arbitration_id']:03X}")
            self.table_log_messages.setItem(i, 1, can_id_item)

            dlc_item = QTableWidgetItem(str(msg['dlc']))
            self.table_log_messages.setItem(i, 2, dlc_item)

            data_hex = ' '.join([f"{b:02X}" for b in msg['data']])
            data_item = QTableWidgetItem(data_hex)
            self.table_log_messages.setItem(i, 3, data_item)

            # Decode
            if self.dbc_parser.is_loaded:
                decoded = self.dbc_parser.decode_message(msg['arbitration_id'], msg['data'])
                if decoded:
                    self.table_log_messages.setItem(i, 4, QTableWidgetItem(decoded['message_name']))
                    signals_str = ', '.join([f"{k}={v}" for k, v in decoded['signals'].items()])
                    self.table_log_messages.setItem(i, 5, QTableWidgetItem(signals_str))

    def _update_signal_list(self):
        """Sinyal listesini güncelle."""
        if not self.dbc_parser.is_loaded:
            return

        signals = self.dbc_parser.get_all_signals()

        self.combo_available_signals.clear()
        for signal in signals:
            display_text = f"{signal['message_name']}.{signal['signal_name']}"
            self.combo_available_signals.addItem(display_text, signal)

    def _on_add_signal_to_plot(self):
        """Grafiğe sinyal ekle."""
        if self.combo_available_signals.currentIndex() < 0:
            return

        signal_data = self.combo_available_signals.currentData()
        signal_name = f"{signal_data['message_name']}.{signal_data['signal_name']}"

        self.plot_widget.add_signal(signal_name)
        self.statusBar().showMessage(f"Grafiğe eklendi: {signal_name}")

    def _on_remove_signal_from_plot(self):
        """Grafikten sinyal çıkar."""
        active_signals = self.plot_widget.get_active_signals()

        if not active_signals:
            return

        signal_name = active_signals[-1]  # Son eklenen sinyali çıkar
        self.plot_widget.remove_signal(signal_name)
        self.statusBar().showMessage(f"Grafikten çıkarıldı: {signal_name}")

    def _on_auto_update_changed(self, state):
        """Otomatik güncelleme değiştiğinde."""
        enabled = (state == Qt.Checked)
        self.plot_widget.set_auto_update(enabled, interval_ms=100)

    def _on_export_data(self, format_type: str):
        """
        Veri export et.

        Args:
            format_type: 'csv' veya 'excel'
        """
        if not self.received_messages and not self.log_reader.messages:
            QMessageBox.warning(self, "Uyarı", "Export edilecek veri yok")
            return

        # Hangi veriyi export edeceğiz
        messages = self.received_messages if self.received_messages else self.log_reader.messages

        # Dosya yolu al
        if format_type == 'csv':
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "CSV Olarak Kaydet",
                "",
                "CSV Dosyaları (*.csv)"
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Olarak Kaydet",
                "",
                "Excel Dosyaları (*.xlsx)"
            )

        if not file_path:
            return

        try:
            include_decoded = self.check_export_decoded.isChecked()
            dbc_parser = self.dbc_parser if include_decoded else None

            if format_type == 'csv':
                success = self.data_exporter.export_to_csv(
                    messages,
                    file_path,
                    include_decoded=include_decoded,
                    dbc_parser=dbc_parser
                )
            else:
                include_stats = self.check_export_stats.isChecked()
                success = self.data_exporter.export_to_excel(
                    messages,
                    file_path,
                    include_decoded=include_decoded,
                    dbc_parser=dbc_parser,
                    include_statistics=include_stats
                )

            if success:
                log_msg = f"Export başarılı: {file_path}\n"
                self.text_export_log.append(log_msg)
                QMessageBox.information(self, "Başarılı", f"Veri export edildi:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Export Hatası", str(e))

    def _show_about(self):
        """Hakkında dialogu göster."""
        QMessageBox.about(
            self,
            "Hakkında",
            "CAN Bus Analyzer v1.0\n\n"
            "Windows için Python tabanlı CAN Bus veri analiz aracı\n\n"
            "Özellikler:\n"
            "• Kvaser CAN cihazları desteği\n"
            "• DBC dosyası ile sinyal decode\n"
            "• Real-time veri görselleştirme\n"
            "• Log dosyası analizi (ASC, BLF)\n"
            "• CSV/Excel export\n\n"
            "Windows 10/11 uyumlu"
        )

    def closeEvent(self, event):
        """Pencere kapatılırken."""
        # CAN bağlantısını kapat
        if self.can_handler.is_connected:
            self.can_handler.disconnect()

        event.accept()

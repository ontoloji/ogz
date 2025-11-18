"""
SORT Test Otomasyon Sistemi - Ana GUI Modülü
PyQt6 tabanlı ana test arayüzü
"""

import sys
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
    QSpinBox, QDoubleSpinBox, QTextEdit, QMessageBox, QSplitter,
    QComboBox, QProgressBar, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPalette, QColor

import pyqtgraph as pg
import numpy as np

# Proje modülleri
from utils import (
    Config, setup_logging, TestStatus, SegmentType, VehicleType,
    format_speed, format_distance, format_energy, format_pedal, format_time,
    RingBuffer
)
from sort_profiles import SORTProfile
from can_interface import CANInterface, MockCANInterface
from arduino_interface import ArduinoInterface, MockArduinoInterface
from edaq_interface import eDAQInterface, MockeDAQInterface
from pid_controller import PIDController
from data_logger import DataLogger, TestMetadata


class TestController(QThread):
    """
    Test kontrolcü thread

    Test mantığını GUI thread'inden ayırır
    """

    # Signals
    status_update = pyqtSignal(dict)  # Durum güncellemesi
    test_completed = pyqtSignal()     # Test tamamlandı
    error_occurred = pyqtSignal(str)  # Hata oluştu

    def __init__(self, config: dict):
        super().__init__()

        self.config = config
        self.running = False
        self.emergency_stop = False

        # Test parametreleri
        self.vehicle_type = VehicleType.ELECTRIC
        self.test_profile = None
        self.accel_pedal = 50
        self.max_speed_limit = 80

        # Interface'ler
        self.can_interface: Optional[CANInterface] = None
        self.arduino_interface: Optional[ArduinoInterface] = None
        self.edaq_interface: Optional[eDAQInterface] = None
        self.pid_controller: Optional[PIDController] = None

        # Test durumu
        self.test_status = TestStatus.READY
        self.current_distance = 0.0
        self.current_speed = 0.0
        self.current_pedal = 0.0
        self.current_energy = 0.0
        self.current_segment = None
        self.current_segment_idx = 0

        # Bekleme modu
        self.wait_start_time = None
        self.wait_remaining = 0

        # Veri logger
        self.data_logger: Optional[DataLogger] = None

        # Zaman
        self.test_start_time = None
        self.last_update_time = time.time()

        self.logger = logging.getLogger(__name__)

    def setup_interfaces(self, mock_mode: bool = False):
        """Interface'leri kur"""
        try:
            # CAN interface
            if self.vehicle_type == VehicleType.ELECTRIC:
                if mock_mode:
                    self.can_interface = MockCANInterface()
                else:
                    self.can_interface = CANInterface(
                        channel=self.config.get('can', 'channel'),
                        bitrate=self.config.get('can', 'bitrate')
                    )
                self.can_interface.set_speed_callback(self._on_speed_update)

            # Arduino interface
            if self.vehicle_type in [VehicleType.DAF_MOTOR, VehicleType.IBK]:
                if mock_mode:
                    self.arduino_interface = MockArduinoInterface()
                else:
                    self.arduino_interface = ArduinoInterface(
                        port=self.config.get('arduino', 'port'),
                        baudrate=self.config.get('arduino', 'baudrate')
                    )

            # eDAQ interface
            if mock_mode:
                self.edaq_interface = MockeDAQInterface(
                    ip=self.config.get('edaq', 'ip'),
                    port=self.config.get('edaq', 'port'),
                    channel_name=self.config.get('edaq', 'channel_name'),
                    poll_interval=self.config.get('edaq', 'poll_interval')
                )
            else:
                self.edaq_interface = eDAQInterface(
                    ip=self.config.get('edaq', 'ip'),
                    port=self.config.get('edaq', 'port'),
                    channel_name=self.config.get('edaq', 'channel_name'),
                    poll_interval=self.config.get('edaq', 'poll_interval')
                )
            self.edaq_interface.set_energy_callback(self._on_energy_update)

            # PID controller
            self.pid_controller = PIDController(
                kp=self.config.get('pid', 'kp'),
                ki=self.config.get('pid', 'ki'),
                kd=self.config.get('pid', 'kd'),
                output_min=self.config.get('pid', 'output_min'),
                output_max=self.config.get('pid', 'output_max')
            )

            self.logger.info("Interface'ler kuruldu")

        except Exception as e:
            self.logger.error(f"Interface kurulum hatası: {e}")
            raise

    def connect_interfaces(self) -> bool:
        """Interface'lere bağlan"""
        try:
            # CAN bağlan
            if self.can_interface:
                if not self.can_interface.connect():
                    raise Exception("CAN bağlantısı başarısız")

            # Arduino bağlan
            if self.arduino_interface:
                if not self.arduino_interface.connect():
                    raise Exception("Arduino bağlantısı başarısız")

            # eDAQ bağlan
            if self.edaq_interface:
                if not self.edaq_interface.connect():
                    raise Exception("eDAQ bağlantısı başarısız")

            self.logger.info("Tüm interface'lere bağlanıldı")
            return True

        except Exception as e:
            self.logger.error(f"Bağlantı hatası: {e}")
            self.disconnect_interfaces()
            return False

    def disconnect_interfaces(self):
        """Interface bağlantılarını kes"""
        if self.can_interface:
            self.can_interface.disconnect()

        if self.arduino_interface:
            self.arduino_interface.disconnect()

        if self.edaq_interface:
            self.edaq_interface.disconnect()

        self.logger.info("Tüm interface'lerden ayrıldı")

    def start_test(self, test_type: int, filename: str, metadata: dict):
        """Testi başlat"""
        try:
            # Test profili oluştur
            self.test_profile = SORTProfile(test_type)

            # Durumu sıfırla
            self.test_status = TestStatus.RUNNING
            self.current_distance = 0.0
            self.current_speed = 0.0
            self.current_pedal = 0.0
            self.current_energy = 0.0
            self.emergency_stop = False
            self.test_start_time = time.time()

            # PID sıfırla
            if self.pid_controller:
                self.pid_controller.reset()

            # Data logger başlat
            self.data_logger = DataLogger(filename=filename)
            self.data_logger.open()

            # Metadata kaydet
            test_meta = TestMetadata(str(self.data_logger.filepath))
            for key, value in metadata.items():
                test_meta.set(key, value)
            test_meta.save()

            # Thread başlat
            self.running = True
            self.start()

            self.logger.info(f"Test başlatıldı: {self.test_profile.get_profile_name()}")

        except Exception as e:
            self.logger.error(f"Test başlatma hatası: {e}")
            self.error_occurred.emit(str(e))

    def stop_test(self):
        """Testi durdur"""
        self.running = False
        self.emergency_stop = True
        self.test_status = TestStatus.STOPPED
        self._set_pedal(0.0)
        self.logger.info("Test durduruldu")

    def run(self):
        """Test ana loop (QThread)"""
        update_interval = 0.1  # 100ms

        while self.running and not self.emergency_stop:
            try:
                current_time = time.time()
                dt = current_time - self.last_update_time
                self.last_update_time = current_time

                # Mesafeyi güncelle (hıza göre)
                if self.current_speed > 0:
                    distance_delta = (self.current_speed / 3.6) * dt  # km/h -> m/s
                    self.current_distance += distance_delta

                # Aktif segmenti bul
                segment, seg_idx = self.test_profile.get_current_segment(self.current_distance)
                self.current_segment = segment
                self.current_segment_idx = seg_idx

                # Segment tipine göre kontrol
                if segment:
                    self._handle_segment(segment, dt)

                # Veri kaydet
                self._log_data()

                # Durum güncelle
                self._emit_status()

                # Test tamamlandı mı?
                if self.test_profile.is_test_completed(self.current_distance):
                    self.logger.info("Test tamamlandı!")
                    self.test_status = TestStatus.COMPLETED
                    self._set_pedal(0.0)
                    self.running = False
                    self.test_completed.emit()

                # Hız limiti kontrolü
                if self.current_speed > self.max_speed_limit + 2:
                    self.logger.error("HIZ LİMİTİ AŞILDI!")
                    self.error_occurred.emit("HIZ LİMİTİ AŞILDI!")
                    self.stop_test()

                # CAN timeout kontrolü
                if self.can_interface and self.can_interface.check_timeout():
                    self.logger.error("CAN BAĞLANTISI KESİLDİ!")
                    self.error_occurred.emit("CAN BAĞLANTISI KESİLDİ!")
                    self.stop_test()

                # Sleep
                time.sleep(update_interval)

            except Exception as e:
                self.logger.error(f"Test loop hatası: {e}")
                self.error_occurred.emit(str(e))
                break

        # Cleanup
        self._set_pedal(0.0)
        if self.data_logger:
            self.data_logger.close()

        self.logger.info("Test loop sonlandı")

    def _handle_segment(self, segment, dt):
        """Segment kontrolü"""
        if segment.segment_type == SegmentType.ACCEL:
            # Hızlanma: Sabit pedal
            self._set_pedal(self.accel_pedal)

        elif segment.segment_type == SegmentType.CONSTANT:
            # Sabit hız: PID kontrolü
            if self.pid_controller:
                self.pid_controller.set_setpoint(segment.target_speed)
                pedal = self.pid_controller.update(self.current_speed, dt)
                self._set_pedal(pedal)

        elif segment.segment_type == SegmentType.BRAKE:
            # Frenleme: Sürücü kontrolü - pedal 0
            self._set_pedal(0.0)

            # Frenleme toleransı kontrolü
            if self.current_speed < 1.0:  # Durdu
                actual_stop = self.current_distance
                target_stop = segment.end_distance
                tolerance = segment.brake_tolerance

                if abs(actual_stop - target_stop) > tolerance:
                    warning = f"DURMA MESAFESI TOLERANSI AŞILDI: {actual_stop - target_stop:.1f}m"
                    self.logger.warning(warning)

        elif segment.segment_type == SegmentType.WAIT:
            # Bekleme
            self._set_pedal(0.0)
            self.test_status = TestStatus.WAITING

            if self.wait_start_time is None:
                self.wait_start_time = time.time()

            elapsed = time.time() - self.wait_start_time
            self.wait_remaining = max(0, segment.wait_time - elapsed)

            # Bekleme tamamlandı mı?
            if self.wait_remaining <= 0:
                self.wait_start_time = None
                self.test_status = TestStatus.RUNNING

    def _set_pedal(self, pedal_percent: float):
        """Gaz pedalını ayarla"""
        self.current_pedal = pedal_percent

        if self.vehicle_type == VehicleType.ELECTRIC and self.can_interface:
            self.can_interface.set_pedal(pedal_percent)

        elif self.vehicle_type == VehicleType.DAF_MOTOR and self.arduino_interface:
            self.arduino_interface.set_daf_pedal(pedal_percent)

        elif self.vehicle_type == VehicleType.IBK and self.arduino_interface:
            self.arduino_interface.set_ibk_pedal(pedal_percent)

    def _on_speed_update(self, speed: float):
        """CAN hız güncellemesi callback"""
        self.current_speed = speed

    def _on_energy_update(self, energy: float):
        """eDAQ enerji güncellemesi callback"""
        self.current_energy = energy

    def _log_data(self):
        """Veri kaydet"""
        if self.data_logger and self.data_logger.is_open:
            data = {
                'distance_m': self.current_distance,
                'speed_kmh': self.current_speed,
                'pedal_pct': self.current_pedal,
                'energy_kwh': self.current_energy,
                'segment': self.current_segment.description if self.current_segment else 'IDLE',
                'test_status': self.test_status
            }
            self.data_logger.write(data)

    def _emit_status(self):
        """Durum sinyali gönder"""
        status = {
            'test_status': self.test_status,
            'distance': self.current_distance,
            'speed': self.current_speed,
            'pedal': self.current_pedal,
            'energy': self.current_energy,
            'segment': self.current_segment.description if self.current_segment else 'Hazır',
            'segment_idx': self.current_segment_idx,
            'wait_remaining': self.wait_remaining,
            'elapsed_time': time.time() - self.test_start_time if self.test_start_time else 0
        }
        self.status_update.emit(status)


class MainWindow(QMainWindow):
    """Ana pencere"""

    def __init__(self):
        super().__init__()

        self.config = Config()
        self.test_controller: Optional[TestController] = None

        # Grafik bufferleri
        self.time_data = RingBuffer(1000)
        self.speed_data = RingBuffer(1000)
        self.distance_data = RingBuffer(1000)
        self.energy_data = RingBuffer(1000)

        self.init_ui()
        self.setup_timers()

        # Test controller oluştur
        self.create_test_controller()

        self.logger = logging.getLogger(__name__)

    def init_ui(self):
        """UI bileşenlerini oluştur"""
        self.setWindowTitle("SORT Test Otomasyon Sistemi")
        self.setGeometry(100, 100, 1400, 900)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Üst panel (Konfigürasyon)
        main_layout.addWidget(self.create_config_panel())

        # Durum paneli
        main_layout.addWidget(self.create_status_panel())

        # Grafik paneli
        main_layout.addWidget(self.create_graph_panel())

        # Alt panel
        main_layout.addWidget(self.create_bottom_panel())

    def create_config_panel(self) -> QGroupBox:
        """Konfigürasyon paneli"""
        group = QGroupBox("Test Konfigürasyonu")
        layout = QGridLayout()

        row = 0

        # Araç tipi
        layout.addWidget(QLabel("Araç Tipi:"), row, 0)
        self.vehicle_type_group = QButtonGroup()
        self.rb_electric = QRadioButton("Elektrikli Araç (CAN)")
        self.rb_daf = QRadioButton("DAF Motor (Arduino)")
        self.rb_ibk = QRadioButton("IBK (Arduino)")
        self.rb_electric.setChecked(True)
        self.vehicle_type_group.addButton(self.rb_electric, 0)
        self.vehicle_type_group.addButton(self.rb_daf, 1)
        self.vehicle_type_group.addButton(self.rb_ibk, 2)

        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(self.rb_electric)
        vehicle_layout.addWidget(self.rb_daf)
        vehicle_layout.addWidget(self.rb_ibk)
        layout.addLayout(vehicle_layout, row, 1, 1, 3)
        row += 1

        # Test tipi
        layout.addWidget(QLabel("Test Tipi:"), row, 0)
        self.test_type_group = QButtonGroup()
        self.rb_sort1 = QRadioButton("SORT 1")
        self.rb_sort2 = QRadioButton("SORT 2")
        self.rb_sort3 = QRadioButton("SORT 3")
        self.rb_sort1.setChecked(True)
        self.test_type_group.addButton(self.rb_sort1, 1)
        self.test_type_group.addButton(self.rb_sort2, 2)
        self.test_type_group.addButton(self.rb_sort3, 3)

        test_layout = QHBoxLayout()
        test_layout.addWidget(self.rb_sort1)
        test_layout.addWidget(self.rb_sort2)
        test_layout.addWidget(self.rb_sort3)
        layout.addLayout(test_layout, row, 1, 1, 3)
        row += 1

        # Hızlanma pedalı
        layout.addWidget(QLabel("Hızlanma Gaz Pedalı (%):"), row, 0)
        self.spin_accel_pedal = QSpinBox()
        self.spin_accel_pedal.setRange(0, 100)
        self.spin_accel_pedal.setValue(self.config.get('test', 'accel_pedal_default'))
        layout.addWidget(self.spin_accel_pedal, row, 1)

        # Maksimum hız limiti
        layout.addWidget(QLabel("Maksimum Hız Limiti (km/h):"), row, 2)
        self.spin_max_speed = QSpinBox()
        self.spin_max_speed.setRange(20, 100)
        self.spin_max_speed.setValue(self.config.get('test', 'max_speed_limit'))
        layout.addWidget(self.spin_max_speed, row, 3)
        row += 1

        # PID parametreleri
        layout.addWidget(QLabel("PID - Kp:"), row, 0)
        self.spin_kp = QDoubleSpinBox()
        self.spin_kp.setRange(0.0, 10.0)
        self.spin_kp.setSingleStep(0.1)
        self.spin_kp.setValue(self.config.get('pid', 'kp'))
        layout.addWidget(self.spin_kp, row, 1)

        layout.addWidget(QLabel("Ki:"), row, 2)
        self.spin_ki = QDoubleSpinBox()
        self.spin_ki.setRange(0.0, 5.0)
        self.spin_ki.setSingleStep(0.1)
        self.spin_ki.setValue(self.config.get('pid', 'ki'))
        layout.addWidget(self.spin_ki, row, 3)

        layout.addWidget(QLabel("Kd:"), row, 4)
        self.spin_kd = QDoubleSpinBox()
        self.spin_kd.setRange(0.0, 2.0)
        self.spin_kd.setSingleStep(0.01)
        self.spin_kd.setValue(self.config.get('pid', 'kd'))
        layout.addWidget(self.spin_kd, row, 5)
        row += 1

        # Butonlar
        self.btn_connect = QPushButton("CAN/Arduino Bağlan")
        self.btn_connect.clicked.connect(self.on_connect_clicked)
        layout.addWidget(self.btn_connect, row, 0, 1, 2)

        self.btn_start = QPushButton("TEST BAŞLAT")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_start.setStyleSheet("QPushButton { background-color: green; color: white; font-weight: bold; }")
        layout.addWidget(self.btn_start, row, 2, 1, 2)

        self.btn_emergency = QPushButton("ACİL DURDUR")
        self.btn_emergency.clicked.connect(self.on_emergency_stop)
        self.btn_emergency.setStyleSheet("QPushButton { background-color: red; color: white; font-weight: bold; }")
        layout.addWidget(self.btn_emergency, row, 4, 1, 2)

        group.setLayout(layout)
        return group

    def create_status_panel(self) -> QGroupBox:
        """Durum paneli"""
        group = QGroupBox("Test Durumu")
        layout = QHBoxLayout()

        # Anlık değerler
        self.lbl_speed = QLabel("Hız: 0.0 km/h")
        self.lbl_distance = QLabel("Mesafe: 0.0 m")
        self.lbl_pedal = QLabel("Pedal: 0%")
        self.lbl_energy = QLabel("Enerji: 0.00 kWh")

        for lbl in [self.lbl_speed, self.lbl_distance, self.lbl_pedal, self.lbl_energy]:
            lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            layout.addWidget(lbl)

        # Test durumu
        self.lbl_status = QLabel("Durum: Hazır")
        self.lbl_status.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(self.lbl_status)

        # Segment
        self.lbl_segment = QLabel("Segment: -")
        self.lbl_segment.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.lbl_segment)

        # Geri sayım
        self.lbl_countdown = QLabel("")
        self.lbl_countdown.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_countdown.setStyleSheet("QLabel { color: orange; }")
        layout.addWidget(self.lbl_countdown)

        group.setLayout(layout)
        return group

    def create_graph_panel(self) -> QWidget:
        """Grafik paneli"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Hız-Zaman grafiği
        self.plot_speed_time = pg.PlotWidget(title="Hız-Zaman")
        self.plot_speed_time.setLabel('left', 'Hız', units='km/h')
        self.plot_speed_time.setLabel('bottom', 'Zaman', units='s')
        self.plot_speed_time.showGrid(x=True, y=True)
        self.curve_speed_time = self.plot_speed_time.plot(pen='g', width=2)
        layout.addWidget(self.plot_speed_time)

        # Hız-Mesafe grafiği
        self.plot_speed_dist = pg.PlotWidget(title="Hız-Mesafe")
        self.plot_speed_dist.setLabel('left', 'Hız', units='km/h')
        self.plot_speed_dist.setLabel('bottom', 'Mesafe', units='m')
        self.plot_speed_dist.showGrid(x=True, y=True)
        self.curve_speed_dist = self.plot_speed_dist.plot(pen='b', width=2)
        layout.addWidget(self.plot_speed_dist)

        # Enerji-Zaman grafiği
        self.plot_energy = pg.PlotWidget(title="Enerji Tüketimi-Zaman")
        self.plot_energy.setLabel('left', 'Enerji', units='kWh')
        self.plot_energy.setLabel('bottom', 'Zaman', units='s')
        self.plot_energy.showGrid(x=True, y=True)
        self.curve_energy = self.plot_energy.plot(pen='r', width=2)
        layout.addWidget(self.plot_energy)

        return widget

    def create_bottom_panel(self) -> QGroupBox:
        """Alt panel"""
        group = QGroupBox("Test Bilgileri")
        layout = QGridLayout()

        row = 0

        # Test adı
        layout.addWidget(QLabel("Test Kayıt Adı:"), row, 0)
        self.edit_test_name = QLineEdit()
        layout.addWidget(self.edit_test_name, row, 1, 1, 3)
        row += 1

        # Araç bilgileri
        layout.addWidget(QLabel("Araç:"), row, 0)
        self.edit_vehicle = QLineEdit("EV001")
        layout.addWidget(self.edit_vehicle, row, 1)

        layout.addWidget(QLabel("Sürücü:"), row, 2)
        self.edit_driver = QLineEdit("Test")
        layout.addWidget(self.edit_driver, row, 3)

        layout.addWidget(QLabel("Dış Sıcaklık (°C):"), row, 4)
        self.edit_temperature = QLineEdit("25")
        layout.addWidget(self.edit_temperature, row, 5)
        row += 1

        # Notlar
        layout.addWidget(QLabel("Notlar:"), row, 0)
        self.edit_notes = QLineEdit()
        layout.addWidget(self.edit_notes, row, 1, 1, 5)
        row += 1

        # Yön
        layout.addWidget(QLabel("Yön:"), row, 0)
        self.direction_group = QButtonGroup()
        self.rb_gidis = QRadioButton("Gidiş")
        self.rb_donus = QRadioButton("Dönüş")
        self.rb_gidis.setChecked(True)
        self.direction_group.addButton(self.rb_gidis, 0)
        self.direction_group.addButton(self.rb_donus, 1)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.rb_gidis)
        dir_layout.addWidget(self.rb_donus)
        layout.addLayout(dir_layout, row, 1)

        # Butonlar
        self.btn_report = QPushButton("Raporlama Ekranı")
        self.btn_report.clicked.connect(self.on_report_clicked)
        layout.addWidget(self.btn_report, row, 4, 1, 2)

        group.setLayout(layout)
        return group

    def setup_timers(self):
        """Zamanlayıcıları kur"""
        # GUI güncelleme timer (50ms)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_graphs)
        self.update_timer.start(50)

    def create_test_controller(self):
        """Test controller oluştur"""
        self.test_controller = TestController(self.config.config)
        self.test_controller.status_update.connect(self.on_status_update)
        self.test_controller.test_completed.connect(self.on_test_completed)
        self.test_controller.error_occurred.connect(self.on_error_occurred)

    def on_connect_clicked(self):
        """Bağlan butonu"""
        try:
            # Mock mode - gerçek donanım için False yapın
            mock_mode = True

            # Interface'leri kur
            vehicle_id = self.vehicle_type_group.checkedId()
            if vehicle_id == 0:
                self.test_controller.vehicle_type = VehicleType.ELECTRIC
            elif vehicle_id == 1:
                self.test_controller.vehicle_type = VehicleType.DAF_MOTOR
            else:
                self.test_controller.vehicle_type = VehicleType.IBK

            self.test_controller.setup_interfaces(mock_mode=mock_mode)

            # Bağlan
            if self.test_controller.connect_interfaces():
                self.btn_start.setEnabled(True)
                self.btn_connect.setEnabled(False)
                QMessageBox.information(self, "Başarılı", "Bağlantı başarılı!")
            else:
                QMessageBox.critical(self, "Hata", "Bağlantı başarısız!")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bağlantı hatası: {e}")

    def on_start_clicked(self):
        """Test başlat butonu"""
        try:
            # Test parametrelerini ayarla
            test_type = self.test_type_group.checkedId()
            self.test_controller.accel_pedal = self.spin_accel_pedal.value()
            self.test_controller.max_speed_limit = self.spin_max_speed.value()

            # PID parametrelerini güncelle
            if self.test_controller.pid_controller:
                self.test_controller.pid_controller.set_gains(
                    kp=self.spin_kp.value(),
                    ki=self.spin_ki.value(),
                    kd=self.spin_kd.value()
                )

            # Dosya adı oluştur
            direction = "GIDIS" if self.rb_gidis.isChecked() else "DONUS"
            vehicle = self.edit_vehicle.text() or "VEHICLE"
            driver = self.edit_driver.text() or "DRIVER"

            from utils import generate_test_filename
            filename = generate_test_filename(str(test_type), direction, vehicle, driver)

            # Metadata
            metadata = {
                'test_type': f'SORT{test_type}',
                'direction': direction,
                'vehicle': vehicle,
                'driver': driver,
                'temperature': self.edit_temperature.text(),
                'notes': self.edit_notes.text(),
                'accel_pedal': self.test_controller.accel_pedal,
                'max_speed_limit': self.test_controller.max_speed_limit,
                'pid_kp': self.spin_kp.value(),
                'pid_ki': self.spin_ki.value(),
                'pid_kd': self.spin_kd.value()
            }

            # Grafik bufferlarını temizle
            self.time_data.clear()
            self.speed_data.clear()
            self.distance_data.clear()
            self.energy_data.clear()

            # Testi başlat
            self.test_controller.start_test(test_type, filename, metadata)

            # UI güncelle
            self.btn_start.setEnabled(False)
            self.btn_connect.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Test başlatma hatası: {e}")

    def on_emergency_stop(self):
        """Acil durdur"""
        if self.test_controller:
            self.test_controller.stop_test()
        self.btn_start.setEnabled(False)
        self.btn_connect.setEnabled(True)

    def on_status_update(self, status: dict):
        """Test durumu güncellendi"""
        # Durum etiketlerini güncelle
        self.lbl_speed.setText(f"Hız: {format_speed(status['speed'])}")
        self.lbl_distance.setText(f"Mesafe: {format_distance(status['distance'])}")
        self.lbl_pedal.setText(f"Pedal: {format_pedal(status['pedal'])}")
        self.lbl_energy.setText(f"Enerji: {format_energy(status['energy'])}")

        self.lbl_status.setText(f"Durum: {status['test_status']}")
        self.lbl_segment.setText(f"Segment: {status['segment']}")

        # Geri sayım
        if status['wait_remaining'] > 0:
            self.lbl_countdown.setText(f"Bekleme: {int(status['wait_remaining'])}s")
        else:
            self.lbl_countdown.setText("")

        # Grafik verisi ekle
        elapsed = status['elapsed_time']
        self.time_data.append(elapsed)
        self.speed_data.append(status['speed'])
        self.distance_data.append(status['distance'])
        self.energy_data.append(status['energy'])

    def update_graphs(self):
        """Grafikleri güncelle"""
        if len(self.time_data) > 0:
            times = np.array(self.time_data.get_all())
            speeds = np.array(self.speed_data.get_all())
            distances = np.array(self.distance_data.get_all())
            energies = np.array(self.energy_data.get_all())

            # Hız-Zaman
            self.curve_speed_time.setData(times, speeds)

            # Hız-Mesafe
            self.curve_speed_dist.setData(distances, speeds)

            # Enerji-Zaman
            self.curve_energy.setData(times, energies)

    def on_test_completed(self):
        """Test tamamlandı"""
        QMessageBox.information(self, "Test Tamamlandı", "Test başarıyla tamamlandı!")
        self.btn_start.setEnabled(False)
        self.btn_connect.setEnabled(True)

    def on_error_occurred(self, error_msg: str):
        """Hata oluştu"""
        QMessageBox.critical(self, "Hata", error_msg)

    def on_report_clicked(self):
        """Raporlama ekranı aç"""
        # TODO: Raporlama penceresi
        QMessageBox.information(self, "Bilgi", "Raporlama ekranı yakında eklenecek")

    def closeEvent(self, event):
        """Pencere kapanıyor"""
        if self.test_controller:
            self.test_controller.stop_test()
            self.test_controller.disconnect_interfaces()
        event.accept()


def main():
    """Ana fonksiyon"""
    # Logging kur
    setup_logging()

    # Qt uygulaması
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Ana pencere
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

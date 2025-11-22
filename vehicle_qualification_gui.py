"""
Araç Kalifikasyon Takip Sistemi - Ana GUI
Windows platformu için PyQt6 tabanlı kullanıcı arayüzü
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QGridLayout, QTabWidget, QDateEdit,
    QDoubleSpinBox, QSpinBox, QDialog, QDialogButtonBox, QGroupBox,
    QSplitter
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QPixmap, QIcon, QFont

from vehicle_database import VehicleDatabase


class VehicleCardWidget(QFrame):
    """Araç kartı widget'ı - Dashboard için"""

    def __init__(self, vehicle: Dict, db: VehicleDatabase, parent=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.db = db
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        """Arayüzü oluştur"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self.setMaximumWidth(400)

        layout = QVBoxLayout()

        # Araç resmi
        image_label = QLabel()
        if self.vehicle['image_path'] and os.path.exists(self.vehicle['image_path']):
            pixmap = QPixmap(self.vehicle['image_path'])
            scaled_pixmap = pixmap.scaled(350, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("Resim Yok")
            image_label.setStyleSheet("background-color: #cccccc; min-height: 200px;")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(image_label)

        # Araç adı
        name_label = QLabel(f"<h3>{self.vehicle['name']}</h3>")
        layout.addWidget(name_label)

        # Model bilgisi
        if self.vehicle['model']:
            model_label = QLabel(f"Model: {self.vehicle['model']}")
            layout.addWidget(model_label)

        # Üretici
        if self.vehicle['manufacturer']:
            manufacturer_label = QLabel(f"Üretici: {self.vehicle['manufacturer']}")
            layout.addWidget(manufacturer_label)

        # Son günlük girdiler
        entries_label = QLabel("<b>Son Günlük Girdiler:</b>")
        layout.addWidget(entries_label)

        # Son 5 girdiyi göster
        entries = self.db.get_vehicle_entries(self.vehicle['id'], limit=5)
        if entries:
            for entry in entries:
                entry_text = f"📅 {entry['entry_date']}"
                if entry['test_type']:
                    entry_text += f" - {entry['test_type']}"
                if entry['test_result']:
                    entry_text += f" - {entry['test_result']}"

                entry_label = QLabel(entry_text)
                entry_label.setStyleSheet("padding: 2px; font-size: 10pt;")
                layout.addWidget(entry_label)
        else:
            no_entry_label = QLabel("Henüz günlük girdi yok")
            no_entry_label.setStyleSheet("color: gray; font-style: italic;")
            layout.addWidget(no_entry_label)

        # Butonlar
        btn_layout = QHBoxLayout()

        add_entry_btn = QPushButton("Günlük Girdi Ekle")
        add_entry_btn.clicked.connect(self.add_daily_entry)
        btn_layout.addWidget(add_entry_btn)

        details_btn = QPushButton("Detaylar")
        details_btn.clicked.connect(self.show_details)
        btn_layout.addWidget(details_btn)

        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def add_daily_entry(self):
        """Günlük girdi ekleme dialogunu aç"""
        if self.parent_window:
            dialog = DailyEntryDialog(self.vehicle['id'], self.db, self.parent_window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Kartı yenile
                self.parent_window.refresh_dashboard()

    def show_details(self):
        """Araç detaylarını göster"""
        if self.parent_window:
            self.parent_window.show_vehicle_details(self.vehicle['id'])


class VehicleDialog(QDialog):
    """Araç ekleme/düzenleme dialogu"""

    def __init__(self, db: VehicleDatabase, vehicle_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.db = db
        self.vehicle_id = vehicle_id
        self.vehicle = None
        self.image_path = None

        if vehicle_id:
            self.vehicle = db.get_vehicle(vehicle_id)
            self.setWindowTitle("Araç Düzenle")
        else:
            self.setWindowTitle("Yeni Araç Ekle")

        self.init_ui()

    def init_ui(self):
        """Arayüzü oluştur"""
        self.resize(600, 700)

        layout = QVBoxLayout()

        # Araç bilgileri
        info_group = QGroupBox("Araç Bilgileri")
        info_layout = QGridLayout()

        # Araç adı
        info_layout.addWidget(QLabel("Araç Adı *:"), 0, 0)
        self.name_input = QLineEdit()
        if self.vehicle:
            self.name_input.setText(self.vehicle['name'])
        info_layout.addWidget(self.name_input, 0, 1)

        # Model
        info_layout.addWidget(QLabel("Model:"), 1, 0)
        self.model_input = QLineEdit()
        if self.vehicle and self.vehicle['model']:
            self.model_input.setText(self.vehicle['model'])
        info_layout.addWidget(self.model_input, 1, 1)

        # Üretici
        info_layout.addWidget(QLabel("Üretici:"), 2, 0)
        self.manufacturer_input = QLineEdit()
        if self.vehicle and self.vehicle['manufacturer']:
            self.manufacturer_input.setText(self.vehicle['manufacturer'])
        info_layout.addWidget(self.manufacturer_input, 2, 1)

        # Yıl
        info_layout.addWidget(QLabel("Yıl:"), 3, 0)
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(datetime.now().year)
        if self.vehicle and self.vehicle['year']:
            self.year_input.setValue(self.vehicle['year'])
        info_layout.addWidget(self.year_input, 3, 1)

        # Araç tipi
        info_layout.addWidget(QLabel("Araç Tipi:"), 4, 0)
        self.type_combo = QComboBox()
        self.type_combo.addItems(['Elektrikli', 'Dizel', 'Benzinli', 'Hibrit', 'Doğalgaz', 'Diğer'])
        if self.vehicle and self.vehicle['vehicle_type']:
            index = self.type_combo.findText(self.vehicle['vehicle_type'])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        info_layout.addWidget(self.type_combo, 4, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Resim
        image_group = QGroupBox("Araç Resmi")
        image_layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0; min-height: 200px;")

        if self.vehicle and self.vehicle['image_path'] and os.path.exists(self.vehicle['image_path']):
            self.image_path = self.vehicle['image_path']
            pixmap = QPixmap(self.image_path)
            scaled_pixmap = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Resim Seçilmedi")

        image_layout.addWidget(self.image_label)

        select_image_btn = QPushButton("Resim Seç")
        select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(select_image_btn)

        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

        # Teknik özellikler
        specs_group = QGroupBox("Teknik Özellikler (JSON)")
        specs_layout = QVBoxLayout()

        self.specs_input = QTextEdit()
        self.specs_input.setPlaceholderText('{"motor_gucu": "150 kW", "batarya": "75 kWh"}')
        if self.vehicle and self.vehicle['specifications']:
            import json
            self.specs_input.setPlainText(json.dumps(self.vehicle['specifications'], ensure_ascii=False, indent=2))

        specs_layout.addWidget(self.specs_input)
        specs_group.setLayout(specs_layout)
        layout.addWidget(specs_group)

        # Notlar
        notes_group = QGroupBox("Notlar")
        notes_layout = QVBoxLayout()

        self.notes_input = QTextEdit()
        if self.vehicle and self.vehicle['notes']:
            self.notes_input.setPlainText(self.vehicle['notes'])

        notes_layout.addWidget(self.notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_vehicle)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def select_image(self):
        """Resim seç"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Araç Resmi Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self.image_path = file_path
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(400, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

    def save_vehicle(self):
        """Aracı kaydet"""
        name = self.name_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Uyarı", "Araç adı boş olamaz!")
            return

        # Teknik özellikleri parse et
        specs = None
        specs_text = self.specs_input.toPlainText().strip()
        if specs_text:
            try:
                import json
                specs = json.loads(specs_text)
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Uyarı", "Teknik özellikler geçerli JSON formatında değil!")
                return

        try:
            if self.vehicle_id:
                # Güncelle
                self.db.update_vehicle(
                    self.vehicle_id,
                    name=name,
                    model=self.model_input.text().strip() or None,
                    manufacturer=self.manufacturer_input.text().strip() or None,
                    year=self.year_input.value(),
                    vehicle_type=self.type_combo.currentText(),
                    image_path=self.image_path,
                    specifications=specs,
                    notes=self.notes_input.toPlainText().strip() or None
                )
            else:
                # Yeni ekle
                self.db.add_vehicle(
                    name=name,
                    model=self.model_input.text().strip() or None,
                    manufacturer=self.manufacturer_input.text().strip() or None,
                    year=self.year_input.value(),
                    vehicle_type=self.type_combo.currentText(),
                    image_path=self.image_path,
                    specifications=specs,
                    notes=self.notes_input.toPlainText().strip() or None
                )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Araç kaydedilemedi: {str(e)}")


class DailyEntryDialog(QDialog):
    """Günlük girdi ekleme/düzenleme dialogu"""

    def __init__(self, vehicle_id: int, db: VehicleDatabase,
                 parent=None, entry_id: Optional[int] = None):
        super().__init__(parent)
        self.vehicle_id = vehicle_id
        self.db = db
        self.entry_id = entry_id
        self.entry = None

        vehicle = db.get_vehicle(vehicle_id)
        self.setWindowTitle(f"Günlük Girdi - {vehicle['name']}")

        if entry_id:
            # Entry'i bul
            entries = db.get_vehicle_entries(vehicle_id)
            for e in entries:
                if e['id'] == entry_id:
                    self.entry = e
                    break

        self.init_ui()

    def init_ui(self):
        """Arayüzü oluştur"""
        self.resize(500, 600)

        layout = QVBoxLayout()

        # Tarih
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Tarih:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        if self.entry and self.entry['entry_date']:
            date_parts = self.entry['entry_date'].split('-')
            self.date_input.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Test tipi
        test_layout = QHBoxLayout()
        test_layout.addWidget(QLabel("Test Tipi:"))
        self.test_type_combo = QComboBox()
        self.test_type_combo.setEditable(True)
        self.test_type_combo.addItems(['SORT 1', 'SORT 2', 'SORT 3', 'Performans', 'Dayanıklılık', 'Diğer'])
        if self.entry and self.entry['test_type']:
            self.test_type_combo.setCurrentText(self.entry['test_type'])
        test_layout.addWidget(self.test_type_combo)
        layout.addLayout(test_layout)

        # Test sonucu
        result_layout = QHBoxLayout()
        result_layout.addWidget(QLabel("Test Sonucu:"))
        self.test_result_combo = QComboBox()
        self.test_result_combo.setEditable(True)
        self.test_result_combo.addItems(['Başarılı', 'Başarısız', 'Kısmen Başarılı', 'İptal'])
        if self.entry and self.entry['test_result']:
            self.test_result_combo.setCurrentText(self.entry['test_result'])
        result_layout.addWidget(self.test_result_combo)
        layout.addLayout(result_layout)

        # Mesafe
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(QLabel("Mesafe (km):"))
        self.distance_input = QDoubleSpinBox()
        self.distance_input.setRange(0, 10000)
        self.distance_input.setDecimals(2)
        if self.entry and self.entry['distance_km']:
            self.distance_input.setValue(self.entry['distance_km'])
        distance_layout.addWidget(self.distance_input)
        layout.addLayout(distance_layout)

        # Süre
        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Süre (saat):"))
        self.duration_input = QDoubleSpinBox()
        self.duration_input.setRange(0, 100)
        self.duration_input.setDecimals(2)
        if self.entry and self.entry['duration_hours']:
            self.duration_input.setValue(self.entry['duration_hours'])
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)

        # Yakıt tüketimi
        fuel_layout = QHBoxLayout()
        fuel_layout.addWidget(QLabel("Yakıt Tüketimi (L):"))
        self.fuel_input = QDoubleSpinBox()
        self.fuel_input.setRange(0, 1000)
        self.fuel_input.setDecimals(2)
        if self.entry and self.entry['fuel_consumption']:
            self.fuel_input.setValue(self.entry['fuel_consumption'])
        fuel_layout.addWidget(self.fuel_input)
        layout.addLayout(fuel_layout)

        # Enerji tüketimi
        energy_layout = QHBoxLayout()
        energy_layout.addWidget(QLabel("Enerji Tüketimi (kWh):"))
        self.energy_input = QDoubleSpinBox()
        self.energy_input.setRange(0, 1000)
        self.energy_input.setDecimals(2)
        if self.entry and self.entry['energy_consumption']:
            self.energy_input.setValue(self.entry['energy_consumption'])
        energy_layout.addWidget(self.energy_input)
        layout.addLayout(energy_layout)

        # Durum
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Durum:"))
        self.status_combo = QComboBox()
        self.status_combo.setEditable(True)
        self.status_combo.addItems(['Tamamlandı', 'Devam Ediyor', 'Beklemede', 'İptal'])
        if self.entry and self.entry['status']:
            self.status_combo.setCurrentText(self.entry['status'])
        status_layout.addWidget(self.status_combo)
        layout.addLayout(status_layout)

        # Operatör
        operator_layout = QHBoxLayout()
        operator_layout.addWidget(QLabel("Operatör:"))
        self.operator_input = QLineEdit()
        if self.entry and self.entry['operator']:
            self.operator_input.setText(self.entry['operator'])
        operator_layout.addWidget(self.operator_input)
        layout.addLayout(operator_layout)

        # Sıcaklık
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Sıcaklık (°C):"))
        self.temp_input = QDoubleSpinBox()
        self.temp_input.setRange(-50, 100)
        self.temp_input.setDecimals(1)
        if self.entry and self.entry['temperature']:
            self.temp_input.setValue(self.entry['temperature'])
        temp_layout.addWidget(self.temp_input)
        layout.addLayout(temp_layout)

        # Hava durumu
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel("Hava Durumu:"))
        self.weather_combo = QComboBox()
        self.weather_combo.setEditable(True)
        self.weather_combo.addItems(['Güneşli', 'Bulutlu', 'Yağmurlu', 'Karlı', 'Sisli'])
        if self.entry and self.entry['weather']:
            self.weather_combo.setCurrentText(self.entry['weather'])
        weather_layout.addWidget(self.weather_combo)
        layout.addLayout(weather_layout)

        # Sorunlar
        issues_group = QGroupBox("Sorunlar")
        issues_layout = QVBoxLayout()
        self.issues_input = QTextEdit()
        if self.entry and self.entry['issues']:
            self.issues_input.setPlainText(self.entry['issues'])
        issues_layout.addWidget(self.issues_input)
        issues_group.setLayout(issues_layout)
        layout.addWidget(issues_group)

        # Notlar
        notes_group = QGroupBox("Notlar")
        notes_layout = QVBoxLayout()
        self.notes_input = QTextEdit()
        if self.entry and self.entry['notes']:
            self.notes_input.setPlainText(self.entry['notes'])
        notes_layout.addWidget(self.notes_input)
        notes_group.setLayout(notes_layout)
        layout.addWidget(notes_group)

        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_entry)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def save_entry(self):
        """Girdiyi kaydet"""
        try:
            date_str = self.date_input.date().toString("yyyy-MM-dd")

            if self.entry_id:
                # Güncelle
                self.db.update_daily_entry(
                    self.entry_id,
                    entry_date=date_str,
                    test_type=self.test_type_combo.currentText() or None,
                    test_result=self.test_result_combo.currentText() or None,
                    distance_km=self.distance_input.value() if self.distance_input.value() > 0 else None,
                    duration_hours=self.duration_input.value() if self.duration_input.value() > 0 else None,
                    fuel_consumption=self.fuel_input.value() if self.fuel_input.value() > 0 else None,
                    energy_consumption=self.energy_input.value() if self.energy_input.value() > 0 else None,
                    status=self.status_combo.currentText() or None,
                    operator=self.operator_input.text().strip() or None,
                    temperature=self.temp_input.value() if self.temp_input.value() != 0 else None,
                    weather=self.weather_combo.currentText() or None,
                    issues=self.issues_input.toPlainText().strip() or None,
                    notes=self.notes_input.toPlainText().strip() or None
                )
            else:
                # Yeni ekle
                self.db.add_daily_entry(
                    vehicle_id=self.vehicle_id,
                    entry_date=date_str,
                    test_type=self.test_type_combo.currentText() or None,
                    test_result=self.test_result_combo.currentText() or None,
                    distance_km=self.distance_input.value() if self.distance_input.value() > 0 else None,
                    duration_hours=self.duration_input.value() if self.duration_input.value() > 0 else None,
                    fuel_consumption=self.fuel_input.value() if self.fuel_input.value() > 0 else None,
                    energy_consumption=self.energy_input.value() if self.energy_input.value() > 0 else None,
                    status=self.status_combo.currentText() or None,
                    operator=self.operator_input.text().strip() or None,
                    temperature=self.temp_input.value() if self.temp_input.value() != 0 else None,
                    weather=self.weather_combo.currentText() or None,
                    issues=self.issues_input.toPlainText().strip() or None,
                    notes=self.notes_input.toPlainText().strip() or None
                )

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Girdi kaydedilemedi: {str(e)}")


class VehicleQualificationApp(QMainWindow):
    """Ana uygulama penceresi"""

    def __init__(self):
        super().__init__()
        self.db = VehicleDatabase()
        self.setWindowTitle("Araç Kalifikasyon Takip Sistemi")
        self.setGeometry(100, 100, 1400, 900)

        self.init_ui()
        self.refresh_dashboard()

    def init_ui(self):
        """Arayüzü oluştur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # Başlık
        title = QLabel("<h1>Araç Kalifikasyon Takip Sistemi</h1>")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()

        # Dashboard tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "Ana Sayfa")

        # Araç listesi tab
        self.list_tab = self.create_list_tab()
        self.tabs.addTab(self.list_tab, "Araç Listesi")

        # Raporlar tab
        self.reports_tab = self.create_reports_tab()
        self.tabs.addTab(self.reports_tab, "Raporlar")

        main_layout.addWidget(self.tabs)

        # Alt butonlar
        bottom_layout = QHBoxLayout()

        add_vehicle_btn = QPushButton("Yeni Araç Ekle")
        add_vehicle_btn.clicked.connect(self.add_vehicle)
        bottom_layout.addWidget(add_vehicle_btn)

        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh_all)
        bottom_layout.addWidget(refresh_btn)

        bottom_layout.addStretch()

        main_layout.addLayout(bottom_layout)

        central_widget.setLayout(main_layout)

    def create_dashboard_tab(self) -> QWidget:
        """Dashboard tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Arama çubuğu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ara:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Araç adı, model veya üretici...")
        self.search_input.textChanged.connect(self.filter_dashboard)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Araç kartları container
        self.cards_widget = QWidget()
        self.cards_layout = QGridLayout()
        self.cards_widget.setLayout(self.cards_layout)

        scroll.setWidget(self.cards_widget)
        layout.addWidget(scroll)

        tab.setLayout(layout)
        return tab

    def create_list_tab(self) -> QWidget:
        """Araç listesi tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Tablo
        self.vehicle_table = QTableWidget()
        self.vehicle_table.setColumnCount(7)
        self.vehicle_table.setHorizontalHeaderLabels([
            'ID', 'Araç Adı', 'Model', 'Üretici', 'Yıl', 'Tip', 'Durum'
        ])
        self.vehicle_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vehicle_table.doubleClicked.connect(self.on_vehicle_double_click)

        layout.addWidget(self.vehicle_table)

        # Butonlar
        btn_layout = QHBoxLayout()

        view_btn = QPushButton("Detayları Gör")
        view_btn.clicked.connect(self.view_selected_vehicle)
        btn_layout.addWidget(view_btn)

        edit_btn = QPushButton("Düzenle")
        edit_btn.clicked.connect(self.edit_selected_vehicle)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(self.delete_selected_vehicle)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        tab.setLayout(layout)
        return tab

    def create_reports_tab(self) -> QWidget:
        """Raporlar tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Rapor ayarları
        settings_group = QGroupBox("Rapor Ayarları")
        settings_layout = QVBoxLayout()

        # Araç seçimi
        vehicle_layout = QHBoxLayout()
        vehicle_layout.addWidget(QLabel("Araç:"))
        self.report_vehicle_combo = QComboBox()
        self.report_vehicle_combo.addItem("Tüm Araçlar", None)
        vehicle_layout.addWidget(self.report_vehicle_combo)
        settings_layout.addLayout(vehicle_layout)

        # Hafta seçimi
        week_layout = QHBoxLayout()
        week_layout.addWidget(QLabel("Hafta:"))
        self.week_combo = QComboBox()
        self.week_combo.addItem("Bu Hafta", 0)
        self.week_combo.addItem("Geçen Hafta", -1)
        self.week_combo.addItem("2 Hafta Önce", -2)
        self.week_combo.addItem("3 Hafta Önce", -3)
        self.week_combo.addItem("4 Hafta Önce", -4)
        week_layout.addWidget(self.week_combo)
        settings_layout.addLayout(week_layout)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # Rapor oluştur butonu
        generate_btn = QPushButton("Haftalık Rapor Oluştur")
        generate_btn.clicked.connect(self.generate_weekly_report)
        layout.addWidget(generate_btn)

        # Rapor önizleme
        self.report_preview = QTextEdit()
        self.report_preview.setReadOnly(True)
        layout.addWidget(self.report_preview)

        # Excel'e aktar
        export_btn = QPushButton("Excel'e Aktar")
        export_btn.clicked.connect(self.export_to_excel)
        layout.addWidget(export_btn)

        tab.setLayout(layout)
        return tab

    def refresh_dashboard(self):
        """Dashboard'u yenile"""
        # Eski kartları temizle
        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        # Araçları getir
        vehicles = self.db.get_all_vehicles()

        # Kartları oluştur
        row = 0
        col = 0
        max_cols = 3

        for vehicle in vehicles:
            card = VehicleCardWidget(vehicle, self.db, self)
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Boş mesaj
        if not vehicles:
            empty_label = QLabel("Henüz araç eklenmemiş. 'Yeni Araç Ekle' butonunu kullanarak başlayın.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: gray; font-size: 14pt; padding: 50px;")
            self.cards_layout.addWidget(empty_label, 0, 0, 1, max_cols)

    def filter_dashboard(self):
        """Dashboard filtreleme"""
        search_term = self.search_input.text().strip()

        if search_term:
            vehicles = self.db.search_vehicles(search_term)
        else:
            vehicles = self.db.get_all_vehicles()

        # Kartları güncelle
        for i in reversed(range(self.cards_layout.count())):
            self.cards_layout.itemAt(i).widget().setParent(None)

        row = 0
        col = 0
        max_cols = 3

        for vehicle in vehicles:
            card = VehicleCardWidget(vehicle, self.db, self)
            self.cards_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        if not vehicles:
            empty_label = QLabel("Araç bulunamadı.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: gray; font-size: 14pt; padding: 50px;")
            self.cards_layout.addWidget(empty_label, 0, 0, 1, max_cols)

    def refresh_vehicle_list(self):
        """Araç listesini yenile"""
        vehicles = self.db.get_all_vehicles('all')

        self.vehicle_table.setRowCount(len(vehicles))

        for row, vehicle in enumerate(vehicles):
            self.vehicle_table.setItem(row, 0, QTableWidgetItem(str(vehicle['id'])))
            self.vehicle_table.setItem(row, 1, QTableWidgetItem(vehicle['name']))
            self.vehicle_table.setItem(row, 2, QTableWidgetItem(vehicle['model'] or '-'))
            self.vehicle_table.setItem(row, 3, QTableWidgetItem(vehicle['manufacturer'] or '-'))
            self.vehicle_table.setItem(row, 4, QTableWidgetItem(str(vehicle['year']) if vehicle['year'] else '-'))
            self.vehicle_table.setItem(row, 5, QTableWidgetItem(vehicle['vehicle_type'] or '-'))
            self.vehicle_table.setItem(row, 6, QTableWidgetItem(vehicle['status']))

        self.vehicle_table.resizeColumnsToContents()

    def refresh_report_vehicles(self):
        """Rapor araç listesini yenile"""
        self.report_vehicle_combo.clear()
        self.report_vehicle_combo.addItem("Tüm Araçlar", None)

        vehicles = self.db.get_all_vehicles()
        for vehicle in vehicles:
            self.report_vehicle_combo.addItem(vehicle['name'], vehicle['id'])

    def refresh_all(self):
        """Tüm tab'ları yenile"""
        self.refresh_dashboard()
        self.refresh_vehicle_list()
        self.refresh_report_vehicles()

    def add_vehicle(self):
        """Yeni araç ekle"""
        dialog = VehicleDialog(self.db, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_all()
            QMessageBox.information(self, "Başarılı", "Araç başarıyla eklendi!")

    def edit_selected_vehicle(self):
        """Seçili aracı düzenle"""
        current_row = self.vehicle_table.currentRow()
        if current_row >= 0:
            vehicle_id = int(self.vehicle_table.item(current_row, 0).text())
            dialog = VehicleDialog(self.db, vehicle_id, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh_all()
                QMessageBox.information(self, "Başarılı", "Araç başarıyla güncellendi!")

    def delete_selected_vehicle(self):
        """Seçili aracı sil"""
        current_row = self.vehicle_table.currentRow()
        if current_row >= 0:
            vehicle_id = int(self.vehicle_table.item(current_row, 0).text())
            vehicle_name = self.vehicle_table.item(current_row, 1).text()

            reply = QMessageBox.question(
                self,
                "Onay",
                f"'{vehicle_name}' aracını silmek istediğinizden emin misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_vehicle(vehicle_id)
                self.refresh_all()
                QMessageBox.information(self, "Başarılı", "Araç başarıyla silindi!")

    def view_selected_vehicle(self):
        """Seçili araç detaylarını göster"""
        current_row = self.vehicle_table.currentRow()
        if current_row >= 0:
            vehicle_id = int(self.vehicle_table.item(current_row, 0).text())
            self.show_vehicle_details(vehicle_id)

    def on_vehicle_double_click(self):
        """Araç çift tıklama"""
        self.view_selected_vehicle()

    def show_vehicle_details(self, vehicle_id: int):
        """Araç detaylarını göster"""
        vehicle = self.db.get_vehicle(vehicle_id)
        if not vehicle:
            return

        # Detay dialogu (basit versiyon)
        msg = f"""
        <h2>{vehicle['name']}</h2>
        <p><b>Model:</b> {vehicle['model'] or '-'}</p>
        <p><b>Üretici:</b> {vehicle['manufacturer'] or '-'}</p>
        <p><b>Yıl:</b> {vehicle['year'] or '-'}</p>
        <p><b>Tip:</b> {vehicle['vehicle_type'] or '-'}</p>
        """

        if vehicle['specifications']:
            msg += "<p><b>Teknik Özellikler:</b></p><ul>"
            for key, value in vehicle['specifications'].items():
                msg += f"<li>{key}: {value}</li>"
            msg += "</ul>"

        if vehicle['notes']:
            msg += f"<p><b>Notlar:</b> {vehicle['notes']}</p>"

        # İstatistikler
        stats = self.db.get_vehicle_statistics(vehicle_id)
        msg += f"""
        <h3>İstatistikler</h3>
        <p><b>Toplam Girdi:</b> {stats.get('total_entries', 0)}</p>
        <p><b>Toplam Mesafe:</b> {stats.get('total_distance', 0):.2f} km</p>
        <p><b>Ortalama Mesafe:</b> {stats.get('avg_distance', 0) or 0:.2f} km</p>
        """

        QMessageBox.information(self, "Araç Detayları", msg)

    def generate_weekly_report(self):
        """Haftalık rapor oluştur"""
        vehicle_id = self.report_vehicle_combo.currentData()
        week_offset = self.week_combo.currentData()

        summary = self.db.get_weekly_summary(vehicle_id, week_offset)

        # Hafta tarihlerini hesapla
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
        week_end = week_start + timedelta(days=6)

        report_text = f"""
        <h2>Haftalık Rapor</h2>
        <p><b>Tarih Aralığı:</b> {week_start.strftime('%d.%m.%Y')} - {week_end.strftime('%d.%m.%Y')}</p>
        <p><b>Araç:</b> {self.report_vehicle_combo.currentText()}</p>
        <hr>
        <h3>Özet</h3>
        <p><b>Toplam Girdi:</b> {summary['total_entries']}</p>
        <p><b>Toplam Mesafe:</b> {summary['total_distance']:.2f} km</p>
        <p><b>Toplam Süre:</b> {summary['total_duration']:.2f} saat</p>
        <p><b>Toplam Yakıt:</b> {summary['total_fuel']:.2f} L</p>
        <p><b>Toplam Enerji:</b> {summary['total_energy']:.2f} kWh</p>
        <hr>
        <h3>Detaylar</h3>
        """

        if summary['entries']:
            report_text += "<table border='1' cellpadding='5' cellspacing='0' width='100%'>"
            report_text += "<tr><th>Tarih</th><th>Test</th><th>Sonuç</th><th>Mesafe</th><th>Durum</th></tr>"

            for entry in summary['entries']:
                report_text += f"""
                <tr>
                    <td>{entry['entry_date']}</td>
                    <td>{entry['test_type'] or '-'}</td>
                    <td>{entry['test_result'] or '-'}</td>
                    <td>{entry['distance_km'] or 0:.2f} km</td>
                    <td>{entry['status'] or '-'}</td>
                </tr>
                """

            report_text += "</table>"
        else:
            report_text += "<p><i>Bu hafta için kayıt bulunamadı.</i></p>"

        self.report_preview.setHtml(report_text)

    def export_to_excel(self):
        """Raporu Excel'e aktar"""
        try:
            import pandas as pd
            from openpyxl import Workbook
            from openpyxl.utils.dataframe import dataframe_to_rows

            vehicle_id = self.report_vehicle_combo.currentData()
            week_offset = self.week_combo.currentData()

            summary = self.db.get_weekly_summary(vehicle_id, week_offset)

            if not summary['entries']:
                QMessageBox.warning(self, "Uyarı", "Rapor için veri bulunamadı!")
                return

            # Dosya adı seç
            today = datetime.now()
            week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
            default_name = f"Haftalik_Rapor_{week_start.strftime('%Y%m%d')}.xlsx"

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Excel Dosyası Kaydet",
                default_name,
                "Excel Dosyaları (*.xlsx)"
            )

            if not file_path:
                return

            # DataFrame oluştur
            df = pd.DataFrame(summary['entries'])

            # Excel'e yaz
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Günlük Girdiler', index=False)

                # Özet sayfa
                summary_data = {
                    'Metrik': ['Toplam Girdi', 'Toplam Mesafe (km)', 'Toplam Süre (saat)',
                              'Toplam Yakıt (L)', 'Toplam Enerji (kWh)'],
                    'Değer': [
                        summary['total_entries'],
                        summary['total_distance'],
                        summary['total_duration'],
                        summary['total_fuel'],
                        summary['total_energy']
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Özet', index=False)

            QMessageBox.information(self, "Başarılı", f"Rapor başarıyla kaydedildi:\n{file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel oluşturulamadı: {str(e)}")

    def closeEvent(self, event):
        """Pencere kapatma"""
        self.db.close()
        event.accept()


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)

    # Stil ayarla
    app.setStyle('Fusion')

    window = VehicleQualificationApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

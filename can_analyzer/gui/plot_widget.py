"""
Real-time Grafik Görselleştirme Widget
PyQtGraph kullanarak yüksek performanslı çizim
"""
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal
from collections import deque
import logging

logger = logging.getLogger(__name__)


class PlotWidget(QWidget):
    """
    Real-time CAN sinyal grafiği widget'ı.
    Yüksek performanslı veri görselleştirme.
    """

    # Signal'lar
    signal_added = pyqtSignal(str)
    signal_removed = pyqtSignal(str)

    def __init__(self, parent=None):
        """
        Plot Widget'ı başlat.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # Veri saklama
        self.signal_data = {}  # {signal_name: {'time': deque, 'values': deque}}
        self.plot_items = {}   # {signal_name: PlotDataItem}
        self.colors = [
            (255, 0, 0),      # Kırmızı
            (0, 255, 0),      # Yeşil
            (0, 0, 255),      # Mavi
            (255, 255, 0),    # Sarı
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
            (255, 128, 0),    # Turuncu
            (128, 0, 255),    # Mor
        ]
        self.color_index = 0
        self.max_points = 1000  # Maksimum gösterilen nokta sayısı

        # Timer (otomatik yenileme için)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_plots)
        self.auto_update_enabled = False

        # UI oluştur
        self._setup_ui()

        logger.debug("PlotWidget oluşturuldu")

    def _setup_ui(self):
        """UI bileşenlerini oluştur."""
        layout = QVBoxLayout(self)

        # Kontrol paneli
        control_layout = QHBoxLayout()

        self.btn_clear = QPushButton("Temizle")
        self.btn_clear.clicked.connect(self.clear_all)

        self.btn_auto_scale = QPushButton("Auto Scale")
        self.btn_auto_scale.clicked.connect(self._auto_scale)

        self.btn_pause = QPushButton("Durdur")
        self.btn_pause.setCheckable(True)
        self.btn_pause.clicked.connect(self._toggle_pause)

        self.label_signal_count = QLabel("Sinyaller: 0")

        control_layout.addWidget(self.btn_clear)
        control_layout.addWidget(self.btn_auto_scale)
        control_layout.addWidget(self.btn_pause)
        control_layout.addStretch()
        control_layout.addWidget(self.label_signal_count)

        layout.addLayout(control_layout)

        # Grafik widget'ı
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')  # Beyaz arka plan
        self.plot_widget.setLabel('left', 'Değer')
        self.plot_widget.setLabel('bottom', 'Zaman (s)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.addLegend()

        layout.addWidget(self.plot_widget)

    def add_signal(self, signal_name: str, initial_time: float = 0,
                   initial_value: float = 0):
        """
        Grafiğe yeni sinyal ekle.

        Args:
            signal_name: Sinyal ismi
            initial_time: İlk zaman değeri
            initial_value: İlk sinyal değeri
        """
        if signal_name in self.signal_data:
            logger.warning(f"Sinyal zaten mevcut: {signal_name}")
            return

        # Veri deque'leri oluştur
        self.signal_data[signal_name] = {
            'time': deque(maxlen=self.max_points),
            'values': deque(maxlen=self.max_points)
        }

        # İlk değeri ekle
        self.signal_data[signal_name]['time'].append(initial_time)
        self.signal_data[signal_name]['values'].append(initial_value)

        # Grafik çizgisi oluştur
        color = self.colors[self.color_index % len(self.colors)]
        self.color_index += 1

        pen = pg.mkPen(color=color, width=2)
        plot_item = self.plot_widget.plot(
            [],
            [],
            pen=pen,
            name=signal_name
        )

        self.plot_items[signal_name] = plot_item

        self._update_signal_count()
        self.signal_added.emit(signal_name)

        logger.info(f"Sinyal grafiğe eklendi: {signal_name}")

    def remove_signal(self, signal_name: str):
        """
        Grafikten sinyal kaldır.

        Args:
            signal_name: Sinyal ismi
        """
        if signal_name not in self.signal_data:
            logger.warning(f"Sinyal bulunamadı: {signal_name}")
            return

        # Veriyi sil
        del self.signal_data[signal_name]

        # Grafik çizgisini sil
        if signal_name in self.plot_items:
            self.plot_widget.removeItem(self.plot_items[signal_name])
            del self.plot_items[signal_name]

        self._update_signal_count()
        self.signal_removed.emit(signal_name)

        logger.info(f"Sinyal grafikten kaldırıldı: {signal_name}")

    def update_signal(self, signal_name: str, time: float, value: float):
        """
        Sinyal değerini güncelle.

        Args:
            signal_name: Sinyal ismi
            time: Zaman değeri
            value: Sinyal değeri
        """
        if signal_name not in self.signal_data:
            # Sinyal yoksa ekle
            self.add_signal(signal_name, time, value)
            return

        # Veriyi ekle
        self.signal_data[signal_name]['time'].append(time)
        self.signal_data[signal_name]['values'].append(value)

        # Auto update kapalıysa manuel güncelleme
        if not self.auto_update_enabled and not self.btn_pause.isChecked():
            self._update_single_plot(signal_name)

    def update_multiple_signals(self, signal_updates: dict):
        """
        Birden fazla sinyali aynı anda güncelle.

        Args:
            signal_updates: {signal_name: (time, value), ...}
        """
        for signal_name, (time, value) in signal_updates.items():
            if signal_name not in self.signal_data:
                self.add_signal(signal_name, time, value)
            else:
                self.signal_data[signal_name]['time'].append(time)
                self.signal_data[signal_name]['values'].append(value)

        # Auto update kapalıysa manuel güncelleme
        if not self.auto_update_enabled and not self.btn_pause.isChecked():
            self._update_plots()

    def _update_single_plot(self, signal_name: str):
        """
        Tek bir sinyal grafiğini güncelle.

        Args:
            signal_name: Sinyal ismi
        """
        if signal_name not in self.plot_items:
            return

        data = self.signal_data[signal_name]
        if len(data['time']) > 0:
            self.plot_items[signal_name].setData(
                list(data['time']),
                list(data['values'])
            )

    def _update_plots(self):
        """Tüm grafikleri güncelle."""
        if self.btn_pause.isChecked():
            return

        for signal_name in self.plot_items:
            self._update_single_plot(signal_name)

    def set_auto_update(self, enabled: bool, interval_ms: int = 100):
        """
        Otomatik güncellemeyi ayarla.

        Args:
            enabled: Otomatik güncelleme aktif mi
            interval_ms: Güncelleme aralığı (milisaniye)
        """
        self.auto_update_enabled = enabled

        if enabled:
            self.update_timer.start(interval_ms)
            logger.debug(f"Otomatik güncelleme aktif: {interval_ms}ms")
        else:
            self.update_timer.stop()
            logger.debug("Otomatik güncelleme pasif")

    def clear_signal(self, signal_name: str):
        """
        Belirli bir sinyalin verisini temizle.

        Args:
            signal_name: Sinyal ismi
        """
        if signal_name in self.signal_data:
            self.signal_data[signal_name]['time'].clear()
            self.signal_data[signal_name]['values'].clear()
            self._update_single_plot(signal_name)

            logger.debug(f"Sinyal verisi temizlendi: {signal_name}")

    def clear_all(self):
        """Tüm sinyalleri ve verilerini temizle."""
        for signal_name in list(self.signal_data.keys()):
            self.remove_signal(signal_name)

        logger.info("Tüm grafikler temizlendi")

    def _auto_scale(self):
        """Grafik eksenlerini otomatik ölçekle."""
        self.plot_widget.enableAutoRange()
        logger.debug("Auto scale uygulandı")

    def _toggle_pause(self, checked: bool):
        """
        Grafiği duraklat/devam ettir.

        Args:
            checked: Duraklat durumu
        """
        if checked:
            self.btn_pause.setText("Devam Et")
            logger.debug("Grafik güncelleme duraklatıldı")
        else:
            self.btn_pause.setText("Durdur")
            logger.debug("Grafik güncelleme devam ediyor")

    def _update_signal_count(self):
        """Sinyal sayısı etiketini güncelle."""
        count = len(self.signal_data)
        self.label_signal_count.setText(f"Sinyaller: {count}")

    def get_active_signals(self) -> list:
        """
        Aktif sinyal isimlerini getir.

        Returns:
            list: Sinyal isimleri
        """
        return list(self.signal_data.keys())

    def set_max_points(self, max_points: int):
        """
        Maksimum gösterilen nokta sayısını ayarla.

        Args:
            max_points: Maksimum nokta sayısı
        """
        self.max_points = max_points

        # Mevcut deque'leri güncelle
        for signal_name in self.signal_data:
            old_time = list(self.signal_data[signal_name]['time'])
            old_values = list(self.signal_data[signal_name]['values'])

            self.signal_data[signal_name]['time'] = deque(old_time, maxlen=max_points)
            self.signal_data[signal_name]['values'] = deque(old_values, maxlen=max_points)

        logger.debug(f"Maksimum nokta sayısı ayarlandı: {max_points}")

    def export_plot_image(self, file_path: str):
        """
        Grafiği resim olarak kaydet.

        Args:
            file_path: Kayıt yolu (PNG, JPG)
        """
        try:
            exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(file_path)
            logger.info(f"Grafik resim olarak kaydedildi: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Grafik export hatası: {str(e)}")
            return False

    def get_signal_statistics(self, signal_name: str) -> dict:
        """
        Sinyal için istatistik bilgileri getir.

        Args:
            signal_name: Sinyal ismi

        Returns:
            dict: İstatistik bilgileri
        """
        if signal_name not in self.signal_data:
            return {}

        values = list(self.signal_data[signal_name]['values'])

        if not values:
            return {}

        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'current': values[-1] if values else None
        }

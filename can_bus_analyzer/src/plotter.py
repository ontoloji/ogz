"""
Veri Görselleştirme Modülü
CAN sinyallerini real-time ve static olarak grafikleştirir.
"""

import matplotlib
matplotlib.use('TkAgg')  # Windows için backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
from typing import Dict, List, Optional, Any
import threading
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalPlotter:
    """
    CAN sinyallerini grafikleştirme sınıfı.
    Real-time ve static plotting desteği.
    """

    def __init__(self, max_points: int = 1000):
        """
        Signal plotter başlatıcı.

        Args:
            max_points: Grafikte gösterilecek maksimum nokta sayısı
        """
        self.max_points = max_points
        self.signals: Dict[str, deque] = {}
        self.timestamps: deque = deque(maxlen=max_points)

        # Matplotlib figure ve axes
        self.fig: Optional[Figure] = None
        self.axes: Dict[str, Any] = {}
        self.lines: Dict[str, Any] = {}

        # Real-time animation
        self.animation: Optional[animation.FuncAnimation] = None
        self.is_running = False

        # Thread safety
        self.lock = threading.Lock()

    def add_signal(self, signal_name: str):
        """
        İzlenecek sinyal ekle.

        Args:
            signal_name: Sinyal ismi
        """
        with self.lock:
            if signal_name not in self.signals:
                self.signals[signal_name] = deque(maxlen=self.max_points)
                logger.info(f"Sinyal eklendi: {signal_name}")

    def remove_signal(self, signal_name: str):
        """
        Sinyali kaldır.

        Args:
            signal_name: Sinyal ismi
        """
        with self.lock:
            if signal_name in self.signals:
                del self.signals[signal_name]
                if signal_name in self.axes:
                    del self.axes[signal_name]
                if signal_name in self.lines:
                    del self.lines[signal_name]
                logger.info(f"Sinyal kaldırıldı: {signal_name}")

    def update_data(self, timestamp: float, signal_values: Dict[str, float]):
        """
        Yeni veri noktası ekle.

        Args:
            timestamp: Zaman damgası
            signal_values: Sinyal ismi -> değer mapping
        """
        with self.lock:
            self.timestamps.append(timestamp)

            for signal_name, value in signal_values.items():
                if signal_name in self.signals:
                    self.signals[signal_name].append(value)
                else:
                    # Otomatik olarak yeni sinyal ekle
                    self.add_signal(signal_name)
                    self.signals[signal_name].append(value)

    def create_static_plot(self, signals_to_plot: Optional[List[str]] = None,
                          title: str = "CAN Signals", save_file: Optional[str] = None) -> Figure:
        """
        Static grafik oluştur.

        Args:
            signals_to_plot: Çizilecek sinyaller (None ise tümü)
            title: Grafik başlığı
            save_file: Kaydedilecek dosya yolu (opsiyonel)

        Returns:
            Figure: Matplotlib figure objesi
        """
        with self.lock:
            if signals_to_plot is None:
                signals_to_plot = list(self.signals.keys())

            if not signals_to_plot:
                logger.warning("Çizilecek sinyal yok")
                return None

            # Figure oluştur
            num_signals = len(signals_to_plot)
            fig, axes = plt.subplots(num_signals, 1, figsize=(12, 3 * num_signals))

            if num_signals == 1:
                axes = [axes]

            fig.suptitle(title, fontsize=14, fontweight='bold')

            timestamps = list(self.timestamps)

            # Her sinyal için subplot
            for idx, signal_name in enumerate(signals_to_plot):
                if signal_name in self.signals:
                    values = list(self.signals[signal_name])

                    # Veri uzunluklarını eşitle
                    min_len = min(len(timestamps), len(values))
                    x_data = timestamps[:min_len]
                    y_data = values[:min_len]

                    axes[idx].plot(x_data, y_data, label=signal_name, linewidth=1.5)
                    axes[idx].set_ylabel(signal_name, fontsize=10)
                    axes[idx].grid(True, alpha=0.3)
                    axes[idx].legend(loc='upper right')

            axes[-1].set_xlabel('Timestamp (s)', fontsize=10)

            plt.tight_layout()

            # Dosyaya kaydet
            if save_file:
                try:
                    fig.savefig(save_file, dpi=150, bbox_inches='tight')
                    logger.info(f"Grafik kaydedildi: {save_file}")
                except Exception as e:
                    logger.error(f"Grafik kaydetme hatası: {e}")

            return fig

    def create_embedded_plot(self, parent_widget, signals_to_plot: Optional[List[str]] = None):
        """
        Tkinter widget'ına gömülü grafik oluştur.

        Args:
            parent_widget: Tkinter parent widget
            signals_to_plot: Çizilecek sinyaller (None ise tümü)

        Returns:
            FigureCanvasTkAgg: Canvas objesi
        """
        if signals_to_plot is None:
            signals_to_plot = list(self.signals.keys())

        if not signals_to_plot:
            logger.warning("Çizilecek sinyal yok")
            return None

        # Figure oluştur
        num_signals = len(signals_to_plot)
        self.fig = Figure(figsize=(10, 3 * num_signals))

        # Subplotlar oluştur
        for idx, signal_name in enumerate(signals_to_plot):
            ax = self.fig.add_subplot(num_signals, 1, idx + 1)
            self.axes[signal_name] = ax
            line, = ax.plot([], [], label=signal_name, linewidth=1.5)
            self.lines[signal_name] = line

            ax.set_ylabel(signal_name, fontsize=9)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper right', fontsize=8)

        if signals_to_plot:
            self.axes[signals_to_plot[-1]].set_xlabel('Timestamp (s)', fontsize=9)

        self.fig.tight_layout()

        # Canvas oluştur
        canvas = FigureCanvasTkAgg(self.fig, parent_widget)
        canvas.draw()

        return canvas

    def update_embedded_plot(self):
        """Gömülü grafiği güncelle."""
        if not self.fig or not self.axes:
            return

        with self.lock:
            timestamps = list(self.timestamps)

            for signal_name, line in self.lines.items():
                if signal_name in self.signals:
                    values = list(self.signals[signal_name])

                    # Veri uzunluklarını eşitle
                    min_len = min(len(timestamps), len(values))
                    x_data = timestamps[:min_len]
                    y_data = values[:min_len]

                    # Line güncelle
                    line.set_data(x_data, y_data)

                    # Axes limitleri güncelle
                    ax = self.axes[signal_name]
                    if x_data:
                        ax.set_xlim(min(x_data), max(x_data))
                    if y_data:
                        y_min, y_max = min(y_data), max(y_data)
                        margin = (y_max - y_min) * 0.1 if y_max != y_min else 1
                        ax.set_ylim(y_min - margin, y_max + margin)

            try:
                self.fig.canvas.draw_idle()
            except:
                pass

    def clear_data(self):
        """Tüm veriyi temizle."""
        with self.lock:
            self.timestamps.clear()
            for signal in self.signals.values():
                signal.clear()
            logger.info("Grafik verileri temizlendi")

    def get_signal_statistics(self, signal_name: str) -> Optional[Dict]:
        """
        Sinyal istatistiklerini al.

        Args:
            signal_name: Sinyal ismi

        Returns:
            Dict: İstatistikler (min, max, avg, etc.)
        """
        with self.lock:
            if signal_name not in self.signals or not self.signals[signal_name]:
                return None

            values = list(self.signals[signal_name])

            return {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'count': len(values),
                'current': values[-1] if values else None
            }


class MultiSignalPlotter:
    """
    Birden fazla sinyali aynı grafikte gösterme sınıfı.
    """

    def __init__(self):
        """Multi signal plotter başlatıcı."""
        self.plotters: Dict[str, SignalPlotter] = {}

    def add_plotter(self, plotter_name: str, max_points: int = 1000):
        """
        Yeni plotter ekle.

        Args:
            plotter_name: Plotter ismi
            max_points: Maksimum nokta sayısı
        """
        if plotter_name not in self.plotters:
            self.plotters[plotter_name] = SignalPlotter(max_points)
            logger.info(f"Plotter eklendi: {plotter_name}")

    def get_plotter(self, plotter_name: str) -> Optional[SignalPlotter]:
        """
        Plotter'ı al.

        Args:
            plotter_name: Plotter ismi

        Returns:
            SignalPlotter: Plotter objesi veya None
        """
        return self.plotters.get(plotter_name)

    def create_combined_plot(self, save_file: Optional[str] = None) -> Figure:
        """
        Tüm plotter'ları tek figure'da birleştir.

        Args:
            save_file: Kaydedilecek dosya yolu

        Returns:
            Figure: Matplotlib figure
        """
        if not self.plotters:
            logger.warning("Hiç plotter yok")
            return None

        total_signals = sum(len(p.signals) for p in self.plotters.values())

        if total_signals == 0:
            logger.warning("Hiç sinyal yok")
            return None

        fig, axes = plt.subplots(total_signals, 1, figsize=(12, 2.5 * total_signals))

        if total_signals == 1:
            axes = [axes]

        fig.suptitle('CAN Bus Signal Analysis', fontsize=14, fontweight='bold')

        idx = 0
        for plotter_name, plotter in self.plotters.items():
            with plotter.lock:
                timestamps = list(plotter.timestamps)

                for signal_name, signal_data in plotter.signals.items():
                    values = list(signal_data)

                    min_len = min(len(timestamps), len(values))
                    x_data = timestamps[:min_len]
                    y_data = values[:min_len]

                    axes[idx].plot(x_data, y_data, label=f"{plotter_name}: {signal_name}",
                                  linewidth=1.5)
                    axes[idx].set_ylabel(signal_name, fontsize=9)
                    axes[idx].grid(True, alpha=0.3)
                    axes[idx].legend(loc='upper right', fontsize=8)

                    idx += 1

        axes[-1].set_xlabel('Timestamp (s)', fontsize=10)
        plt.tight_layout()

        if save_file:
            try:
                fig.savefig(save_file, dpi=150, bbox_inches='tight')
                logger.info(f"Birleşik grafik kaydedildi: {save_file}")
            except Exception as e:
                logger.error(f"Grafik kaydetme hatası: {e}")

        return fig


if __name__ == "__main__":
    # Test kodu
    print("Signal Plotter Modülü Test Ediliyor...")

    import numpy as np

    plotter = SignalPlotter(max_points=100)

    # Test sinyalleri ekle
    plotter.add_signal("Speed")
    plotter.add_signal("RPM")

    # Örnek veri üret
    for i in range(100):
        timestamp = i * 0.1
        signal_values = {
            'Speed': 50 + 20 * np.sin(i * 0.1),
            'RPM': 2000 + 500 * np.cos(i * 0.1)
        }
        plotter.update_data(timestamp, signal_values)

    # Statik grafik oluştur
    # fig = plotter.create_static_plot(title="Test Signals", save_file="test_plot.png")
    # plt.show()

    print("Test tamamlandı")

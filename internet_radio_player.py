#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internet Radyo Çalar
Windows tabanlı, VLC destekli internet radyo çalar uygulaması
Equalizer özelliği ile
"""

import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLineEdit, QLabel,
                             QSlider, QListWidget, QGroupBox, QMessageBox,
                             QListWidgetItem, QInputDialog, QSplitter, QDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import vlc


class MiniPlayer(QDialog):
    """Mini player penceresi - küçük, her zaman üstte"""

    # Sinyaller
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    volume_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mini Player")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setFixedSize(300, 120)

        # Başlangıç pozisyonu (sağ üst köşe)
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width() - 320, 20)

        self.init_ui()

    def init_ui(self):
        """Mini player arayüzü"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Başlık ve kapat butonu
        header_layout = QHBoxLayout()
        title_label = QLabel("🎵 Radyo Çalar")
        title_label.setFont(QFont("Arial", 10, QFont.Bold))

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.hide)
        close_btn.setStyleSheet("background-color: #f44336; color: white; border: none; border-radius: 10px;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # Durum etiketi
        self.status_label = QLabel("Hazır")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #2196F3; font-weight: bold;")
        layout.addWidget(self.status_label)

        # Kontrol butonları
        controls_layout = QHBoxLayout()

        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(40, 40)
        self.play_btn.clicked.connect(self.play_clicked.emit)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(40, 40)
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 18px;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.stop_btn)
        layout.addLayout(controls_layout)

        # Ses kontrolü
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊")
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)

        self.volume_value_label = QLabel("70%")
        self.volume_value_label.setFixedWidth(35)

        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_value_label)
        layout.addLayout(volume_layout)

        self.setLayout(layout)

    def update_status(self, status, color="#2196F3"):
        """Durum metnini güncelle"""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_volume_label(self, value):
        """Ses seviyesi etiketini güncelle"""
        self.volume_value_label.setText(f"{value}%")

    def set_playing_state(self, playing):
        """Çalma durumuna göre butonları güncelle"""
        self.play_btn.setEnabled(not playing)
        self.stop_btn.setEnabled(playing)

class InternetRadioPlayer(QMainWindow):
    """Ana radyo çalar sınıfı"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Internet Radyo Çalar")
        self.setGeometry(100, 100, 900, 700)

        # VLC player instance
        self.vlc_instance = vlc.Instance('--no-xlib')
        self.player = self.vlc_instance.media_player_new()

        # Equalizer
        self.equalizer = None
        self.eq_preamp = 0.0
        self.eq_values = [0.0] * 10  # 10 bant değerlerini sakla

        # Durum değişkenleri
        self.is_playing = False
        self.current_url = ""
        self.favorites = []
        self.favorites_file = "radio_favorites.json"

        # Equalizer frekans bantları (Hz)
        self.eq_bands = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]
        self.eq_sliders = []

        # Mini player
        self.mini_player = None

        # Arayüzü oluştur
        self.init_ui()

        # Mini player'ı oluştur
        self.create_mini_player()

        # Favorileri yükle
        self.load_favorites()

        # Timer for updating current track info
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)

    def init_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Başlık
        title = QLabel("🎵 Internet Radyo Çalar")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Splitter ile sol ve sağ paneli ayır
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Sol panel - Kontroller ve URL
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # URL giriş grubu
        url_group = QGroupBox("Radyo İstasyonu URL")
        url_layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("http://... veya https://... radyo akış adresi girin")
        self.url_input.setFont(QFont("Arial", 10))
        url_layout.addWidget(self.url_input)

        # URL butonları
        url_buttons = QHBoxLayout()
        self.play_btn = QPushButton("▶ Çal")
        self.play_btn.clicked.connect(self.play_radio)
        self.play_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;")

        self.stop_btn = QPushButton("⏹ Durdur")
        self.stop_btn.clicked.connect(self.stop_radio)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 10px;")
        self.stop_btn.setEnabled(False)

        url_buttons.addWidget(self.play_btn)
        url_buttons.addWidget(self.stop_btn)
        url_layout.addLayout(url_buttons)

        url_group.setLayout(url_layout)
        left_layout.addWidget(url_group)

        # Ses kontrolü
        volume_group = QGroupBox("Ses Seviyesi")
        volume_layout = QVBoxLayout()

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)

        self.volume_label = QLabel("70%")
        self.volume_label.setAlignment(Qt.AlignCenter)

        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        volume_group.setLayout(volume_layout)
        left_layout.addWidget(volume_group)

        # Durum bilgisi
        status_group = QGroupBox("Durum")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Hazır")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11))
        self.status_label.setStyleSheet("color: #2196F3; padding: 10px;")

        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)

        # Mini Player butonu
        mini_player_btn = QPushButton("📱 Mini Player Aç")
        mini_player_btn.clicked.connect(self.toggle_mini_player)
        mini_player_btn.setStyleSheet("background-color: #9C27B0; color: white; font-size: 12px; padding: 8px;")
        left_layout.addWidget(mini_player_btn)

        # Equalizer
        eq_group = QGroupBox("Equalizer (dB)")
        eq_layout = QVBoxLayout()

        # Equalizer reset butonu
        eq_buttons = QHBoxLayout()
        reset_eq_btn = QPushButton("Sıfırla")
        reset_eq_btn.clicked.connect(self.reset_equalizer)
        eq_buttons.addWidget(reset_eq_btn)
        eq_layout.addLayout(eq_buttons)

        # Equalizer sliders
        sliders_layout = QHBoxLayout()
        for i, freq in enumerate(self.eq_bands):
            band_layout = QVBoxLayout()

            # Slider
            slider = QSlider(Qt.Vertical)
            slider.setMinimum(-20)
            slider.setMaximum(20)
            slider.setValue(0)
            slider.setTickPosition(QSlider.TicksBothSides)
            slider.setTickInterval(5)
            slider.valueChanged.connect(lambda value, band=i: self.change_eq_band(band, value))

            # Frekans etiketi
            if freq >= 1000:
                freq_label = QLabel(f"{freq//1000}K")
            else:
                freq_label = QLabel(f"{freq}")
            freq_label.setAlignment(Qt.AlignCenter)
            freq_label.setFont(QFont("Arial", 8))

            # Değer etiketi
            value_label = QLabel("0")
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setFont(QFont("Arial", 8))

            slider.value_label = value_label  # Store reference

            band_layout.addWidget(value_label)
            band_layout.addWidget(slider)
            band_layout.addWidget(freq_label)

            sliders_layout.addLayout(band_layout)
            self.eq_sliders.append(slider)

        eq_layout.addLayout(sliders_layout)
        eq_group.setLayout(eq_layout)
        left_layout.addWidget(eq_group)

        splitter.addWidget(left_panel)

        # Sağ panel - Favoriler
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        favorites_group = QGroupBox("Favoriler")
        favorites_layout = QVBoxLayout()

        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.play_favorite)
        favorites_layout.addWidget(self.favorites_list)

        # Favori butonları
        fav_buttons = QHBoxLayout()

        add_fav_btn = QPushButton("➕ Ekle")
        add_fav_btn.clicked.connect(self.add_favorite)

        remove_fav_btn = QPushButton("🗑 Sil")
        remove_fav_btn.clicked.connect(self.remove_favorite)

        fav_buttons.addWidget(add_fav_btn)
        fav_buttons.addWidget(remove_fav_btn)
        favorites_layout.addLayout(fav_buttons)

        favorites_group.setLayout(favorites_layout)
        right_layout.addWidget(favorites_group)

        splitter.addWidget(right_panel)

        # Splitter oranları
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        # Durum çubuğu
        self.statusBar().showMessage("Hazır")

    def play_radio(self):
        """Radyo çalmayı başlat"""
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir radyo URL'si girin!")
            return

        if not (url.startswith('http://') or url.startswith('https://')):
            QMessageBox.warning(self, "Uyarı", "URL http:// veya https:// ile başlamalıdır!")
            return

        try:
            # Stop current stream if playing
            if self.is_playing:
                self.player.stop()

            # Create new media
            media = self.vlc_instance.media_new(url)
            self.player.set_media(media)

            # Play
            self.player.play()

            # Equalizer'ı yeniden ayarla (her yeni media için gerekli)
            self.apply_equalizer()

            self.current_url = url
            self.is_playing = True

            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

            self.status_label.setText(f"Çalıyor: {url}")
            self.status_label.setStyleSheet("color: #4CAF50; padding: 10px; font-weight: bold;")
            self.statusBar().showMessage(f"Çalıyor: {url}")

            # Mini player'ı güncelle
            if self.mini_player:
                self.mini_player.set_playing_state(True)
                self.mini_player.update_status("▶ Çalıyor", "#4CAF50")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Radyo çalınamadı:\n{str(e)}")
            self.status_label.setText("Hata!")
            self.status_label.setStyleSheet("color: #f44336; padding: 10px;")

            # Mini player'ı güncelle
            if self.mini_player:
                self.mini_player.set_playing_state(False)
                self.mini_player.update_status("Hata!", "#f44336")

    def stop_radio(self):
        """Radyoyu durdur"""
        if self.is_playing:
            self.player.stop()
            self.is_playing = False

            self.play_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

            self.status_label.setText("Durduruldu")
            self.status_label.setStyleSheet("color: #FF9800; padding: 10px;")
            self.statusBar().showMessage("Radyo durduruldu")

            # Mini player'ı güncelle
            if self.mini_player:
                self.mini_player.set_playing_state(False)
                self.mini_player.update_status("Durduruldu", "#FF9800")

    def change_volume(self, value):
        """Ses seviyesini değiştir"""
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"{value}%")

    def change_eq_band(self, band, value):
        """Equalizer bandını değiştir"""
        # Değeri sakla
        self.eq_values[band] = float(value)

        # Update value label
        if self.eq_sliders[band].value_label:
            self.eq_sliders[band].value_label.setText(f"{value}")

        # Equalizer'ı güncelle
        self.apply_equalizer()

    def reset_equalizer(self):
        """Equalizeri sıfırla"""
        # Değerleri sıfırla
        self.eq_values = [0.0] * 10

        # Slider'ları sıfırla
        for i, slider in enumerate(self.eq_sliders):
            slider.setValue(0)
            if hasattr(slider, 'value_label'):
                slider.value_label.setText("0")

        # Equalizer'ı güncelle
        self.apply_equalizer()

    def apply_equalizer(self):
        """Equalizer ayarlarını player'a uygula"""
        try:
            # Yeni equalizer oluştur
            self.equalizer = vlc.AudioEqualizer()

            # Tüm bant değerlerini ayarla
            for i, value in enumerate(self.eq_values):
                self.equalizer.set_amp_at_index(value, i)

            # Player'a bağla
            self.player.set_equalizer(self.equalizer)

        except Exception as e:
            print(f"Equalizer hatası: {e}")

    def add_favorite(self):
        """Favori ekle"""
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir URL girin!")
            return

        # İsim iste
        name, ok = QInputDialog.getText(self, "Favori Ekle", "İstasyon adı:")

        if ok and name:
            favorite = {"name": name, "url": url}
            self.favorites.append(favorite)
            self.save_favorites()
            self.update_favorites_list()

            QMessageBox.information(self, "Başarılı", f"'{name}' favorilere eklendi!")

    def remove_favorite(self):
        """Favori sil"""
        current_item = self.favorites_list.currentItem()

        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz favoriyi seçin!")
            return

        index = self.favorites_list.currentRow()
        favorite = self.favorites[index]

        reply = QMessageBox.question(self, "Favori Sil",
                                    f"'{favorite['name']}' favorilerden silinsin mi?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            del self.favorites[index]
            self.save_favorites()
            self.update_favorites_list()

    def play_favorite(self, item):
        """Favori istasyonu çal"""
        index = self.favorites_list.row(item)
        favorite = self.favorites[index]

        self.url_input.setText(favorite['url'])
        self.play_radio()

    def load_favorites(self):
        """Favorileri dosyadan yükle"""
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    self.favorites = json.load(f)
                self.update_favorites_list()
            except Exception as e:
                print(f"Favoriler yüklenemedi: {e}")

    def save_favorites(self):
        """Favorileri dosyaya kaydet"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Favoriler kaydedilemedi: {e}")

    def update_favorites_list(self):
        """Favori listesini güncelle"""
        self.favorites_list.clear()
        for favorite in self.favorites:
            self.favorites_list.addItem(f"📻 {favorite['name']}")

    def update_status(self):
        """Durum bilgisini güncelle"""
        if self.is_playing:
            state = self.player.get_state()
            if state == vlc.State.Playing:
                self.status_label.setText(f"▶ Çalıyor")
            elif state == vlc.State.Buffering:
                self.status_label.setText("⏳ Yükleniyor...")
            elif state == vlc.State.Error:
                self.status_label.setText("❌ Hata!")
                self.status_label.setStyleSheet("color: #f44336; padding: 10px;")
                self.is_playing = False
                self.play_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)

    def create_mini_player(self):
        """Mini player'ı oluştur ve bağlantıları kur"""
        self.mini_player = MiniPlayer(self)

        # Mini player sinyallerini ana player'a bağla
        self.mini_player.play_clicked.connect(self.play_radio)
        self.mini_player.stop_clicked.connect(self.stop_radio)
        self.mini_player.volume_changed.connect(self.sync_volume_from_mini)

    def toggle_mini_player(self):
        """Mini player'ı aç/kapat"""
        if self.mini_player.isVisible():
            self.mini_player.hide()
        else:
            self.mini_player.show()
            # Mevcut durumu senkronize et
            self.sync_mini_player_state()

    def sync_mini_player_state(self):
        """Ana player durumunu mini player'a senkronize et"""
        if self.mini_player:
            # Ses seviyesi
            volume = self.volume_slider.value()
            self.mini_player.volume_slider.setValue(volume)
            self.mini_player.update_volume_label(volume)

            # Çalma durumu
            self.mini_player.set_playing_state(self.is_playing)

            # Durum metni
            if self.is_playing:
                self.mini_player.update_status("▶ Çalıyor", "#4CAF50")
            else:
                self.mini_player.update_status("Hazır", "#2196F3")

    def sync_volume_from_mini(self, value):
        """Mini player'dan gelen ses değişikliğini ana player'a uygula"""
        self.volume_slider.setValue(value)
        self.change_volume(value)
        self.mini_player.update_volume_label(value)

    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap"""
        if self.is_playing:
            self.player.stop()

        # Mini player'ı kapat
        if self.mini_player:
            self.mini_player.close()

        event.accept()


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    player = InternetRadioPlayer()
    player.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

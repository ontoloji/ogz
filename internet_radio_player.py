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
                             QListWidgetItem, QInputDialog, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon
import vlc

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
        self.equalizer = vlc.AudioEqualizer()
        self.player.set_equalizer(self.equalizer)

        # Durum değişkenleri
        self.is_playing = False
        self.current_url = ""
        self.favorites = []
        self.favorites_file = "radio_favorites.json"

        # Equalizer frekans bantları (Hz)
        self.eq_bands = [60, 170, 310, 600, 1000, 3000, 6000, 12000, 14000, 16000]
        self.eq_sliders = []

        # Arayüzü oluştur
        self.init_ui()

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

            self.current_url = url
            self.is_playing = True

            self.play_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

            self.status_label.setText(f"Çalıyor: {url}")
            self.status_label.setStyleSheet("color: #4CAF50; padding: 10px; font-weight: bold;")
            self.statusBar().showMessage(f"Çalıyor: {url}")

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Radyo çalınamadı:\n{str(e)}")
            self.status_label.setText("Hata!")
            self.status_label.setStyleSheet("color: #f44336; padding: 10px;")

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

    def change_volume(self, value):
        """Ses seviyesini değiştir"""
        self.player.audio_set_volume(value)
        self.volume_label.setText(f"{value}%")

    def change_eq_band(self, band, value):
        """Equalizer bandını değiştir"""
        # VLC equalizer değeri -20 ile +20 arasında (dB cinsinden)
        self.equalizer.set_amp_at_index(float(value), band)

        # Update value label
        if self.eq_sliders[band].value_label:
            self.eq_sliders[band].value_label.setText(f"{value}")

    def reset_equalizer(self):
        """Equalizeri sıfırla"""
        for i, slider in enumerate(self.eq_sliders):
            slider.setValue(0)
            if hasattr(slider, 'value_label'):
                slider.value_label.setText("0")
            self.equalizer.set_amp_at_index(0.0, i)

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

    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap"""
        if self.is_playing:
            self.player.stop()
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

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
                             QListWidgetItem, QInputDialog, QSplitter, QDialog,
                             QScrollArea, QGridLayout, QTabWidget)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QPen
import vlc
import urllib.request
import urllib.parse
from ambient_sounds import AMBIENT_SOUNDS, SOUNDS_DIR


def create_app_icon():
    """Kırmızı daire içinde beyaz RPo ikonu oluştur"""
    icon = QIcon()

    for size in [256, 128, 64, 48, 32, 16]:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Kırmızı daire
        painter.setPen(QPen(QColor("#C62828"), max(2, size // 32)))
        painter.setBrush(QColor("#E53935"))
        margin = 2
        painter.drawEllipse(margin, margin, size - margin*2, size - margin*2)

        # Beyaz "RPo" yazısı
        painter.setPen(QColor("white"))
        font = QFont("Arial", int(size * 0.3), QFont.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "RPo")

        painter.end()
        icon.addPixmap(pixmap)

    return icon


def parse_playlist_url(url):
    """
    PLS, M3U, ASX gibi playlist dosyalarını parse et ve gerçek stream URL'ini döndür
    """
    try:
        # URL'nin uzantısını kontrol et
        url_lower = url.lower()

        # Direkt stream URL'si ise olduğu gibi döndür
        if not any(ext in url_lower for ext in ['.pls', '.m3u', '.m3u8', '.asx', '.xspf']):
            return url

        # Playlist dosyasını indir
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8', errors='ignore')

        # PLS formatı
        if '.pls' in url_lower or '[playlist]' in content.lower():
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('File') and '=' in line:
                    stream_url = line.split('=', 1)[1].strip()
                    if stream_url.startswith('http'):
                        return stream_url

        # M3U/M3U8 formatı
        elif '.m3u' in url_lower or '#EXTM3U' in content:
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and line.startswith('http'):
                    return line

        # ASX formatı (XML-based)
        elif '.asx' in url_lower or '<asx' in content.lower():
            import re
            # <ref href="stream_url" /> formatını ara
            match = re.search(r'href=["\'](http[^"\']+)["\']', content, re.IGNORECASE)
            if match:
                return match.group(1)

        # XSPF formatı (XML-based)
        elif '.xspf' in url_lower or '<playlist' in content.lower():
            import re
            # <location>stream_url</location> formatını ara
            match = re.search(r'<location>(http[^<]+)</location>', content, re.IGNORECASE)
            if match:
                return match.group(1)

        # Parse edemediyse orijinal URL'i döndür
        return url

    except Exception as e:
        print(f"Playlist parse hatası: {e}")
        # Hata durumunda orijinal URL'i döndür
        return url


class NoisePlayer:
    """Multi-channel ambient noise player - 30 sese kadar aynı anda çalabilir"""

    def __init__(self):
        """Her ses için ayrı VLC instance oluştur"""
        self.players = {}  # {sound_id: {'player': vlc_player, 'instance': vlc_instance, 'active': bool}}
        self.vlc_base_instance = vlc.Instance('--no-xlib')

    def toggle_sound(self, sound_id):
        """Sesi aç/kapat (toggle)"""
        if sound_id not in AMBIENT_SOUNDS:
            print(f"Bilinmeyen ses: {sound_id}")
            return False

        sound_info = AMBIENT_SOUNDS[sound_id]
        sound_file = os.path.join(SOUNDS_DIR, sound_info['file'])

        # Ses dosyası var mı kontrol et
        if not os.path.exists(sound_file):
            return False  # Dosya yok

        # Eğer çalıyorsa durdur
        if sound_id in self.players and self.players[sound_id]['active']:
            self.stop_sound(sound_id)
            return False

        # Değilse çal
        return self.play_sound(sound_id, sound_file)

    def play_sound(self, sound_id, sound_file):
        """Sesi çal (loop modunda)"""
        try:
            # Yeni player oluştur veya mevcut olanı kullan
            if sound_id not in self.players:
                instance = vlc.Instance('--no-xlib')
                player = instance.media_player_new()
                self.players[sound_id] = {
                    'instance': instance,
                    'player': player,
                    'active': False,
                    'volume': 100
                }

            player = self.players[sound_id]['player']
            instance = self.players[sound_id]['instance']

            # Media oluştur
            media = instance.media_new(sound_file)
            player.set_media(media)

            # Loop için event manager kullan
            event_manager = player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,
                                     lambda event: self._loop_sound(sound_id))

            # Ses seviyesini ayarla
            volume = self.players[sound_id].get('volume', 100)
            player.audio_set_volume(volume)

            # Çal
            player.play()
            self.players[sound_id]['active'] = True

            return True

        except Exception as e:
            print(f"Ses çalma hatası ({sound_id}): {e}")
            return False

    def _loop_sound(self, sound_id):
        """Ses bitince tekrar başlat (seamless loop)"""
        if sound_id in self.players and self.players[sound_id]['active']:
            player = self.players[sound_id]['player']
            player.stop()
            player.play()

    def stop_sound(self, sound_id):
        """Sesi durdur"""
        if sound_id in self.players:
            try:
                self.players[sound_id]['player'].stop()
                self.players[sound_id]['active'] = False
            except Exception as e:
                print(f"Ses durdurma hatası ({sound_id}): {e}")

    def stop_all(self):
        """Tüm sesleri durdur"""
        for sound_id in list(self.players.keys()):
            self.stop_sound(sound_id)

    def is_playing(self, sound_id):
        """Ses çalıyor mu kontrol et"""
        return sound_id in self.players and self.players[sound_id]['active']

    def set_volume(self, sound_id, volume):
        """Belirli bir ses için volume ayarla (0-100)"""
        if sound_id in self.players:
            self.players[sound_id]['volume'] = volume
            if self.players[sound_id]['active']:
                self.players[sound_id]['player'].audio_set_volume(volume)

    def get_active_sounds(self):
        """Aktif seslerin listesini döndür"""
        return [sid for sid, info in self.players.items() if info['active']]


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

        # Uygulama ikonu ayarla
        self.setWindowIcon(create_app_icon())

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
        self.volume_slider.setMaximum(200)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)

        self.volume_value_label = QLabel("100%")
        self.volume_value_label.setFixedWidth(40)

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

        # Uygulama ikonu ayarla
        self.setWindowIcon(create_app_icon())

        # VLC player instance
        self.vlc_instance = vlc.Instance('--no-xlib')
        self.player = self.vlc_instance.media_player_new()

        # Noise player
        self.noise_player = NoisePlayer()
        self.current_mode = "radio"  # "radio" veya "noise"

        # Equalizer
        self.equalizer = None
        self.eq_preamp = 0.0
        self.eq_values = [0.0] * 10  # 10 bant değerlerini sakla
        self.eq_settings_file = "radio_equalizer.json"

        # Durum değişkenleri
        self.is_playing = False
        self.current_url = ""
        self.current_title = ""  # Çalan şarkı adı
        self.metadata_update_counter = 0  # Metadata güncelleme sayacı
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

        # Equalizer ayarlarını yükle
        self.load_equalizer_settings()

        # Ses seviyesini başlangıçta 100% ile sınırla
        if self.volume_slider.value() > 100:
            self.volume_slider.setValue(100)

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

        # Başlık ve mode switch
        header_layout = QHBoxLayout()

        title = QLabel("🎵 Internet Radyo Çalar")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Mode switch button
        self.mode_switch_btn = QPushButton("🎵 Noise")
        self.mode_switch_btn.setFixedSize(120, 40)
        self.mode_switch_btn.clicked.connect(self.toggle_mode)
        self.mode_switch_btn.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        header_layout.addStretch()
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_switch_btn)

        main_layout.addLayout(header_layout)

        # Stacked widget for mode switching
        from PyQt5.QtWidgets import QStackedWidget
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Radio mode widget
        self.radio_widget = QWidget()
        self.init_radio_ui()
        self.stacked_widget.addWidget(self.radio_widget)

        # Noise mode widget
        self.noise_widget = QWidget()
        self.init_noise_ui()
        self.stacked_widget.addWidget(self.noise_widget)

        # Start with radio mode
        self.stacked_widget.setCurrentIndex(0)

        # Durum çubuğu
        self.statusBar().showMessage("Hazır")

    def init_radio_ui(self):
        """Radio mode arayüzü"""
        radio_layout = QVBoxLayout()
        self.radio_widget.setLayout(radio_layout)

        # Splitter ile sol ve sağ paneli ayır
        splitter = QSplitter(Qt.Horizontal)
        radio_layout.addWidget(splitter)

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

        # Ana ses slider (0-200% - VLC amplification)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(200)
        self.volume_slider.setValue(100)
        self.volume_slider.setTickPosition(QSlider.TicksBelow)
        self.volume_slider.setTickInterval(25)
        self.volume_slider.valueChanged.connect(self.change_volume)

        self.volume_label = QLabel("100%")
        self.volume_label.setAlignment(Qt.AlignCenter)
        self.volume_label.setFont(QFont("Arial", 11, QFont.Bold))

        # Hızlı ses butonları
        volume_buttons = QHBoxLayout()

        vol_50_btn = QPushButton("50%")
        vol_50_btn.clicked.connect(lambda: self.volume_slider.setValue(50))
        vol_50_btn.setFixedWidth(50)

        vol_100_btn = QPushButton("100%")
        vol_100_btn.clicked.connect(lambda: self.volume_slider.setValue(100))
        vol_100_btn.setFixedWidth(50)
        vol_100_btn.setStyleSheet("background-color: #2196F3; color: white;")

        vol_150_btn = QPushButton("150%")
        vol_150_btn.clicked.connect(lambda: self.volume_slider.setValue(150))
        vol_150_btn.setFixedWidth(50)
        vol_150_btn.setStyleSheet("background-color: #FF9800; color: white;")

        vol_200_btn = QPushButton("200%")
        vol_200_btn.clicked.connect(lambda: self.volume_slider.setValue(200))
        vol_200_btn.setFixedWidth(50)
        vol_200_btn.setStyleSheet("background-color: #f44336; color: white;")

        volume_buttons.addWidget(vol_50_btn)
        volume_buttons.addWidget(vol_100_btn)
        volume_buttons.addWidget(vol_150_btn)
        volume_buttons.addWidget(vol_200_btn)

        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        volume_layout.addLayout(volume_buttons)

        # Uyarı etiketi
        warning_label = QLabel("⚠️ 100% üzeri hoparlöre zarar verebilir")
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setStyleSheet("color: #FF9800; font-size: 9px;")
        volume_layout.addWidget(warning_label)

        volume_group.setLayout(volume_layout)
        left_layout.addWidget(volume_group)

        # Durum bilgisi
        status_group = QGroupBox("Durum")
        status_layout = QVBoxLayout()

        self.status_label = QLabel("Hazır")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11))
        self.status_label.setStyleSheet("color: #2196F3; padding: 10px;")

        # Şarkı adı etiketi
        self.now_playing_label = QLabel("♪ ...")
        self.now_playing_label.setAlignment(Qt.AlignCenter)
        self.now_playing_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.now_playing_label.setStyleSheet("color: #9C27B0; padding: 5px; background-color: #f0f0f0; border-radius: 5px;")
        self.now_playing_label.setWordWrap(True)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.now_playing_label)
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

    def init_noise_ui(self):
        """Noise mode arayüzü - 30 ambient ses"""
        noise_layout = QVBoxLayout()
        self.noise_widget.setLayout(noise_layout)

        # Bilgi etiketi
        info_label = QLabel("🎵 Ambient Noise Sistemi - İstediğin seslere tıkla (kombinasyon yapabilirsin)")
        info_label.setFont(QFont("Arial", 11, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #9C27B0; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        noise_layout.addWidget(info_label)

        # Scroll area for sounds
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        # Ses dosyası kontrol uyarısı
        sounds_dir_exists = os.path.exists(SOUNDS_DIR)
        if not sounds_dir_exists or not any(os.path.exists(os.path.join(SOUNDS_DIR, s['file'])) for s in AMBIENT_SOUNDS.values()):
            warning_box = QGroupBox("⚠️ Ses Dosyaları Bulunamadı")
            warning_layout = QVBoxLayout()
            warning_text = QLabel(
                "Ambient sesler için ses dosyalarını indirmen gerekiyor.\n\n"
                "1. 'download_sounds.py' scriptini çalıştır\n"
                "2. 'sounds/' klasörüne manuel olarak ses dosyalarını koy\n"
                "3. Detaylı bilgi için AMBIENT_SOUNDS_README.md dosyasına bak"
            )
            warning_text.setWordWrap(True)
            warning_text.setStyleSheet("color: #f44336; font-size: 11px; padding: 10px;")
            warning_layout.addWidget(warning_text)
            warning_box.setLayout(warning_layout)
            scroll_layout.addWidget(warning_box)

        # Kategorilere göre grupla
        categories = {
            'nature': {'name': '🌿 Doğa Sesleri', 'sounds': []},
            'ambient': {'name': '🎧 Ambient Sesleri', 'sounds': []},
            'relax': {'name': '😌 Rahatlama Sesleri', 'sounds': []}
        }

        for sound_id, sound_info in AMBIENT_SOUNDS.items():
            category = sound_info.get('category', 'ambient')
            if category in categories:
                categories[category]['sounds'].append((sound_id, sound_info))

        # Her kategori için butonlar oluştur
        self.noise_buttons = {}  # {sound_id: button}

        for category_id, category_info in categories.items():
            if not category_info['sounds']:
                continue

            category_group = QGroupBox(category_info['name'])
            category_layout = QGridLayout()

            # Sesleri grid içine yerleştir (5 sütun)
            sounds = sorted(category_info['sounds'], key=lambda x: x[1]['name'])
            for idx, (sound_id, sound_info) in enumerate(sounds):
                row = idx // 5
                col = idx % 5

                btn = QPushButton(f"{sound_info['icon']}\n{sound_info['name']}")
                btn.setFixedSize(100, 70)
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, sid=sound_id: self.toggle_noise_sound(sid))

                # Ses dosyası var mı kontrol et
                sound_file = os.path.join(SOUNDS_DIR, sound_info['file'])
                if not os.path.exists(sound_file):
                    btn.setEnabled(False)
                    btn.setToolTip(f"Ses dosyası bulunamadı: {sound_info['file']}")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #cccccc;
                            color: #666666;
                            font-size: 10px;
                            border: 1px solid #999999;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #f5f5f5;
                            color: #333333;
                            font-size: 10px;
                            border: 2px solid #9C27B0;
                            border-radius: 5px;
                        }
                        QPushButton:hover {
                            background-color: #e0e0e0;
                        }
                        QPushButton:checked {
                            background-color: #4CAF50;
                            color: white;
                            border: 2px solid #2E7D32;
                            font-weight: bold;
                        }
                    """)

                category_layout.addWidget(btn, row, col)
                self.noise_buttons[sound_id] = btn

            category_group.setLayout(category_layout)
            scroll_layout.addWidget(category_group)

        scroll.setWidget(scroll_content)
        noise_layout.addWidget(scroll)

        # Alt kontrol paneli
        control_panel = QGroupBox("Kontroller")
        control_layout = QVBoxLayout()

        # Aktif sesler göstergesi
        self.active_sounds_label = QLabel("Aktif sesler: Yok")
        self.active_sounds_label.setAlignment(Qt.AlignCenter)
        self.active_sounds_label.setFont(QFont("Arial", 10))
        self.active_sounds_label.setStyleSheet("color: #2196F3; padding: 5px;")
        control_layout.addWidget(self.active_sounds_label)

        # Tümünü durdur butonu
        stop_all_btn = QPushButton("⏹ Tümünü Durdur")
        stop_all_btn.clicked.connect(self.stop_all_noise)
        stop_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        control_layout.addWidget(stop_all_btn)

        control_panel.setLayout(control_layout)
        noise_layout.addWidget(control_panel)

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

            # Playlist dosyalarını parse et (.pls, .m3u, .asx, vb.)
            stream_url = parse_playlist_url(url)

            # Create new media
            media = self.vlc_instance.media_new(stream_url)
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

        # Ses seviyesine göre renk değiştir
        if value > 150:
            self.volume_label.setStyleSheet("color: #f44336; font-weight: bold;")  # Kırmızı
        elif value > 100:
            self.volume_label.setStyleSheet("color: #FF9800; font-weight: bold;")  # Turuncu
        else:
            self.volume_label.setStyleSheet("color: #4CAF50; font-weight: bold;")  # Yeşil

    def change_eq_band(self, band, value):
        """Equalizer bandını değiştir"""
        # Değeri sakla
        self.eq_values[band] = float(value)

        # Update value label
        if self.eq_sliders[band].value_label:
            self.eq_sliders[band].value_label.setText(f"{value}")

        # Equalizer'ı güncelle
        self.apply_equalizer()

        # Ayarları kaydet
        self.save_equalizer_settings()

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

        # Ayarları kaydet
        self.save_equalizer_settings()

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

    def load_equalizer_settings(self):
        """Equalizer ayarlarını dosyadan yükle"""
        if os.path.exists(self.eq_settings_file):
            try:
                with open(self.eq_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.eq_values = settings.get('eq_values', [0.0] * 10)

                    # Slider'ları güncelle
                    for i, value in enumerate(self.eq_values):
                        if i < len(self.eq_sliders):
                            self.eq_sliders[i].setValue(int(value))

                    # Equalizer'ı uygula
                    self.apply_equalizer()

            except Exception as e:
                print(f"Equalizer ayarları yüklenemedi: {e}")

    def save_equalizer_settings(self):
        """Equalizer ayarlarını dosyaya kaydet"""
        try:
            settings = {
                'eq_values': self.eq_values
            }
            with open(self.eq_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Equalizer ayarları kaydedilemedi: {e}")

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

                # Şarkı adını al (metadata) - Her 3 saniyede bir
                self.metadata_update_counter += 1
                if self.metadata_update_counter >= 3:  # 3 saniye (timer 1 saniyede bir)
                    self.metadata_update_counter = 0
                    self.update_now_playing()

            elif state == vlc.State.Buffering:
                self.status_label.setText("⏳ Yükleniyor...")
            elif state == vlc.State.Error:
                self.status_label.setText("❌ Hata!")
                self.status_label.setStyleSheet("color: #f44336; padding: 10px;")
                self.is_playing = False
                self.play_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.now_playing_label.setText("♪ ...")

    def update_now_playing(self):
        """Çalan şarkı bilgisini güncelle"""
        try:
            media = self.player.get_media()
            if not media:
                return

            # Parse ETME - GUI donmasına sebep oluyor!
            # VLC zaten arka planda parse ediyor, direkt meta okuyabiliriz

            # Şarkı adını al (non-blocking)
            title = media.get_meta(vlc.Meta.Title)
            artist = media.get_meta(vlc.Meta.Artist)
            now_playing = media.get_meta(vlc.Meta.NowPlaying)

            # En uygun metni seç
            display_text = None
            if now_playing:
                display_text = now_playing
            elif title and artist:
                display_text = f"{artist} - {title}"
            elif title:
                display_text = title

            # Eğer yeni bilgi varsa güncelle
            if display_text and display_text != self.current_title:
                self.current_title = display_text
                self.now_playing_label.setText(f"♪ {display_text}")

                # Mini player'ı da güncelle
                if self.mini_player and self.mini_player.isVisible():
                    # İlk 30 karakteri göster (mini player küçük)
                    short_text = display_text[:30] + "..." if len(display_text) > 30 else display_text
                    self.mini_player.update_status(f"♪ {short_text}", "#9C27B0")

        except Exception as e:
            # Metadata okuma hatası - sessizce devam et
            pass

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

    def toggle_mode(self):
        """Radio ve Noise modu arasında geçiş yap"""
        if self.current_mode == "radio":
            # Noise moduna geç
            self.current_mode = "noise"
            self.mode_switch_btn.setText("📻 Radio")
            self.stacked_widget.setCurrentIndex(1)  # Noise widget

            # Radio'yu durdur
            if self.is_playing:
                self.stop_radio()

            self.statusBar().showMessage("Noise Modu Aktif")

        else:
            # Radio moduna geç
            self.current_mode = "radio"
            self.mode_switch_btn.setText("🎵 Noise")
            self.stacked_widget.setCurrentIndex(0)  # Radio widget

            # Tüm noise'ları durdur
            self.noise_player.stop_all()
            self.update_noise_buttons_state()

            self.statusBar().showMessage("Radio Modu Aktif")

    def toggle_noise_sound(self, sound_id):
        """Ambient sesi aç/kapat"""
        success = self.noise_player.toggle_sound(sound_id)

        # Buton durumunu güncelle
        if sound_id in self.noise_buttons:
            btn = self.noise_buttons[sound_id]
            is_playing = self.noise_player.is_playing(sound_id)
            btn.setChecked(is_playing)

        # Aktif sesler etiketini güncelle
        self.update_active_sounds_display()

        # Durum mesajı
        sound_name = AMBIENT_SOUNDS[sound_id]['name']
        if self.noise_player.is_playing(sound_id):
            self.statusBar().showMessage(f"▶ {sound_name} çalıyor")
        else:
            self.statusBar().showMessage(f"⏹ {sound_name} durduruldu")

    def stop_all_noise(self):
        """Tüm ambient sesleri durdur"""
        self.noise_player.stop_all()
        self.update_noise_buttons_state()
        self.statusBar().showMessage("Tüm sesler durduruldu")

    def update_noise_buttons_state(self):
        """Tüm noise butonlarının durumunu güncelle"""
        for sound_id, btn in self.noise_buttons.items():
            is_playing = self.noise_player.is_playing(sound_id)
            btn.setChecked(is_playing)

        self.update_active_sounds_display()

    def update_active_sounds_display(self):
        """Aktif sesler göstergesini güncelle"""
        active_sounds = self.noise_player.get_active_sounds()

        if not active_sounds:
            self.active_sounds_label.setText("Aktif sesler: Yok")
            self.active_sounds_label.setStyleSheet("color: #999999; padding: 5px;")
        else:
            sound_names = [AMBIENT_SOUNDS[sid]['icon'] for sid in active_sounds[:10]]  # İlk 10 ikonu göster
            display_text = " ".join(sound_names)
            if len(active_sounds) > 10:
                display_text += f" +{len(active_sounds) - 10}"

            self.active_sounds_label.setText(f"Aktif sesler ({len(active_sounds)}): {display_text}")
            self.active_sounds_label.setStyleSheet("color: #4CAF50; padding: 5px; font-weight: bold;")

    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap"""
        if self.is_playing:
            self.player.stop()

        # Noise player'ı durdur
        self.noise_player.stop_all()

        # Mini player'ı kapat
        if self.mini_player:
            self.mini_player.close()

        event.accept()


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Uygulama ikonu ayarla (görev çubuğu için)
    app.setWindowIcon(create_app_icon())

    player = InternetRadioPlayer()
    player.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

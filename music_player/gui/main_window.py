"""
Müzik Çalar - Ana Pencere (Main Window)
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QListWidget, QTabWidget,
    QSplitter, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QFileDialog, QLineEdit, QComboBox, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap
from pathlib import Path


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""

    def __init__(self, music_app):
        """
        Ana pencere başlat

        Args:
            music_app: MusicPlayerApp instance
        """
        super().__init__()

        self.music_app = music_app
        self.current_playlist = None
        self.current_track_index = 0
        self.playlist_tracks = []
        self.is_radio_mode = False

        self.setup_ui()
        self.setup_connections()
        self.setup_timers()
        self.load_initial_data()

    def setup_ui(self):
        """UI bileşenlerini oluştur"""

        self.setWindowTitle("Müzik Çalar")
        self.setGeometry(100, 100, 1200, 800)

        # Merkezi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # === MENU BAR ===
        self.create_menu_bar()

        # === TOP: SEARCH BAR ===
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Şarkı, artist veya album ara...")
        self.search_input.setMinimumHeight(35)
        search_layout.addWidget(self.search_input)

        self.search_source = QComboBox()
        self.search_source.addItems(["Tümü", "Spotify", "YouTube Music"])
        self.search_source.setMinimumWidth(150)
        search_layout.addWidget(self.search_source)

        self.search_button = QPushButton("Ara")
        self.search_button.setMinimumWidth(100)
        search_layout.addWidget(self.search_button)

        main_layout.addLayout(search_layout)

        # === MIDDLE: TABS ===
        self.tabs = QTabWidget()

        # Tab 1: Playlist'ler ve Çalan Şarkı
        self.playlist_tab = self.create_playlist_tab()
        self.tabs.addTab(self.playlist_tab, "Playlist'ler")

        # Tab 2: Arama Sonuçları
        self.search_tab = self.create_search_tab()
        self.tabs.addTab(self.search_tab, "Arama")

        # Tab 3: Favoriler
        self.favorites_tab = self.create_favorites_tab()
        self.tabs.addTab(self.favorites_tab, "Favoriler")

        # Tab 4: Online Radyo
        self.radio_tab = self.create_radio_tab()
        self.tabs.addTab(self.radio_tab, "Radyo")

        # Tab 5: Equalizer
        self.equalizer_tab = self.create_equalizer_tab()
        self.tabs.addTab(self.equalizer_tab, "Ekolayzır")

        main_layout.addWidget(self.tabs)

        # === BOTTOM: PLAYER CONTROLS ===
        player_layout = self.create_player_controls()
        main_layout.addLayout(player_layout)

        # === STATUS BAR ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")

    def create_menu_bar(self):
        """Menu bar oluştur"""
        menubar = self.menuBar()

        # Dosya Menüsü
        file_menu = menubar.addMenu("Dosya")

        import_action = QAction("Playlist İçe Aktar...", self)
        import_action.triggered.connect(self.import_playlist)
        file_menu.addAction(import_action)

        export_action = QAction("Playlist Dışa Aktar...", self)
        export_action.triggered.connect(self.export_playlist)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Görünüm Menüsü
        view_menu = menubar.addMenu("Görünüm")

        mini_player_action = QAction("Mini Player", self)
        mini_player_action.triggered.connect(self.open_mini_player)
        view_menu.addAction(mini_player_action)

        # Ayarlar Menüsü
        settings_menu = menubar.addMenu("Ayarlar")

        api_keys_action = QAction("API Ayarları...", self)
        api_keys_action.triggered.connect(self.open_api_settings)
        settings_menu.addAction(api_keys_action)

        # Hakkında Menüsü
        help_menu = menubar.addMenu("Yardım")

        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_playlist_tab(self):
        """Playlist tab oluştur"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Sol: Playlist listesi
        left_layout = QVBoxLayout()

        # Playlist oluştur butonu
        create_playlist_btn = QPushButton("+ Yeni Playlist")
        create_playlist_btn.clicked.connect(self.create_new_playlist)
        left_layout.addWidget(create_playlist_btn)

        # Playlist listesi
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self.on_playlist_selected)
        left_layout.addWidget(self.playlist_list)

        # Playlist düğmeleri
        playlist_buttons = QHBoxLayout()
        delete_playlist_btn = QPushButton("Sil")
        delete_playlist_btn.clicked.connect(self.delete_playlist)
        playlist_buttons.addWidget(delete_playlist_btn)
        left_layout.addLayout(playlist_buttons)

        # Sağ: Playlist içeriği
        right_layout = QVBoxLayout()

        self.current_playlist_label = QLabel("Playlist seçin")
        self.current_playlist_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        right_layout.addWidget(self.current_playlist_label)

        self.tracks_list = QListWidget()
        self.tracks_list.itemDoubleClicked.connect(self.on_track_double_clicked)
        right_layout.addWidget(self.tracks_list)

        # Track düğmeleri
        track_buttons = QHBoxLayout()
        remove_track_btn = QPushButton("Çıkar")
        remove_track_btn.clicked.connect(self.remove_track_from_playlist)
        track_buttons.addWidget(remove_track_btn)

        add_to_favorites_btn = QPushButton("Favorilere Ekle")
        add_to_favorites_btn.clicked.connect(self.add_to_favorites)
        track_buttons.addWidget(add_to_favorites_btn)

        right_layout.addLayout(track_buttons)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)
        return tab

    def create_search_tab(self):
        """Arama sonuçları tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.search_results_label = QLabel("Arama sonuçları burada görünecek")
        layout.addWidget(self.search_results_label)

        self.search_results_list = QListWidget()
        self.search_results_list.itemDoubleClicked.connect(self.play_search_result)
        layout.addWidget(self.search_results_list)

        # Sonuç düğmeleri
        buttons_layout = QHBoxLayout()

        play_btn = QPushButton("Çal")
        play_btn.clicked.connect(self.play_search_result)
        buttons_layout.addWidget(play_btn)

        add_to_playlist_btn = QPushButton("Playlist'e Ekle")
        add_to_playlist_btn.clicked.connect(self.add_search_result_to_playlist)
        buttons_layout.addWidget(add_to_playlist_btn)

        layout.addLayout(buttons_layout)

        return tab

    def create_favorites_tab(self):
        """Favoriler tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        label = QLabel("Beğenilen Şarkılar")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self.play_favorite)
        layout.addWidget(self.favorites_list)

        # Favorilerden çıkar butonu
        remove_btn = QPushButton("Favorilerden Çıkar")
        remove_btn.clicked.connect(self.remove_from_favorites)
        layout.addWidget(remove_btn)

        return tab

    def create_radio_tab(self):
        """Online radyo tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Radyo filtreleri
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Ülke:"))
        self.radio_country_combo = QComboBox()
        self.radio_country_combo.addItems(["Tümü", "TR", "US", "GB", "DE", "FR"])
        filter_layout.addWidget(self.radio_country_combo)

        filter_layout.addWidget(QLabel("Tür:"))
        self.radio_genre_combo = QComboBox()
        self.radio_genre_combo.addItems(["Tümü", "pop", "rock", "jazz", "classical", "news", "talk"])
        filter_layout.addWidget(self.radio_genre_combo)

        search_radio_btn = QPushButton("Ara")
        search_radio_btn.clicked.connect(self.search_radio_stations)
        filter_layout.addWidget(search_radio_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Radyo istasyon listesi
        self.radio_list = QListWidget()
        self.radio_list.itemDoubleClicked.connect(self.play_radio_station)
        layout.addWidget(self.radio_list)

        return tab

    def create_equalizer_tab(self):
        """Ekolayzır tab'ı oluştur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Preset seçici
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))

        self.eq_preset_combo = QComboBox()
        self.eq_preset_combo.addItems(self.music_app.equalizer.get_preset_names())
        self.eq_preset_combo.currentTextChanged.connect(self.on_eq_preset_changed)
        preset_layout.addWidget(self.eq_preset_combo)

        self.eq_enable_check = QPushButton("EQ Aktif")
        self.eq_enable_check.setCheckable(True)
        self.eq_enable_check.setChecked(self.music_app.equalizer.is_enabled())
        self.eq_enable_check.clicked.connect(self.toggle_equalizer)
        preset_layout.addWidget(self.eq_enable_check)

        preset_layout.addStretch()
        layout.addLayout(preset_layout)

        # Equalizer sliders (10-band)
        self.eq_sliders = []
        sliders_layout = QHBoxLayout()

        for i, freq in enumerate(self.music_app.equalizer.FREQUENCIES):
            band_layout = QVBoxLayout()

            # Slider
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setMinimum(-200)  # -20 dB * 10
            slider.setMaximum(200)   # +20 dB * 10
            slider.setValue(0)
            slider.setTickPosition(QSlider.TickPosition.TicksBothSides)
            slider.setTickInterval(50)
            slider.valueChanged.connect(lambda val, idx=i: self.on_eq_slider_changed(idx, val))
            self.eq_sliders.append(slider)
            band_layout.addWidget(slider)

            # Frekans label
            if freq >= 1000:
                label = QLabel(f"{freq // 1000}kHz")
            else:
                label = QLabel(f"{freq}Hz")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            band_layout.addWidget(label)

            sliders_layout.addLayout(band_layout)

        layout.addLayout(sliders_layout)

        return tab

    def create_player_controls(self):
        """Oynatıcı kontrolleri oluştur"""
        layout = QVBoxLayout()

        # Şarkı bilgisi
        info_layout = QHBoxLayout()

        self.track_thumbnail = QLabel()
        self.track_thumbnail.setFixedSize(60, 60)
        self.track_thumbnail.setStyleSheet("border: 1px solid gray;")
        info_layout.addWidget(self.track_thumbnail)

        track_info = QVBoxLayout()
        self.track_title_label = QLabel("Şarkı seçilmedi")
        self.track_title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        track_info.addWidget(self.track_title_label)

        self.track_artist_label = QLabel("")
        track_info.addWidget(self.track_artist_label)

        info_layout.addLayout(track_info)
        info_layout.addStretch()

        layout.addLayout(info_layout)

        # Progress bar
        progress_layout = QHBoxLayout()

        self.current_time_label = QLabel("0:00")
        progress_layout.addWidget(self.current_time_label)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setMinimum(0)
        self.progress_slider.setMaximum(1000)
        self.progress_slider.sliderMoved.connect(self.on_progress_slider_moved)
        progress_layout.addWidget(self.progress_slider)

        self.total_time_label = QLabel("0:00")
        progress_layout.addWidget(self.total_time_label)

        layout.addLayout(progress_layout)

        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.addStretch()

        self.prev_button = QPushButton("⏮")
        self.prev_button.setFixedSize(50, 50)
        self.prev_button.clicked.connect(self.play_previous)
        controls_layout.addWidget(self.prev_button)

        self.play_pause_button = QPushButton("▶")
        self.play_pause_button.setFixedSize(60, 60)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        controls_layout.addWidget(self.play_pause_button)

        self.next_button = QPushButton("⏭")
        self.next_button.setFixedSize(50, 50)
        self.next_button.clicked.connect(self.play_next)
        controls_layout.addWidget(self.next_button)

        controls_layout.addStretch()

        # Volume
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        controls_layout.addWidget(QLabel("🔊"))
        controls_layout.addWidget(self.volume_slider)

        layout.addLayout(controls_layout)

        return layout

    def setup_connections(self):
        """Sinyal bağlantılarını kur"""
        # Arama butonu
        self.search_button.clicked.connect(self.perform_search)
        self.search_input.returnPressed.connect(self.perform_search)

        # Audio player callbacks
        self.music_app.audio_player.on_track_ended = self.on_track_ended

    def setup_timers(self):
        """Timer'ları kur"""
        # Progress güncelleme timer'ı
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_timer.start(1000)  # Her saniye

    def load_initial_data(self):
        """İlk verileri yükle"""
        self.refresh_playlists()
        self.refresh_favorites()

    # === PLAYLIST METHODLARI ===

    def refresh_playlists(self):
        """Playlist listesini yenile"""
        self.playlist_list.clear()
        playlists = self.music_app.playlist_manager.get_all_playlists()

        for playlist in playlists:
            item = QListWidgetItem(f"{playlist['name']} ({playlist.get('track_count', 0)} şarkı)")
            item.setData(Qt.ItemDataRole.UserRole, playlist['id'])
            self.playlist_list.addItem(item)

    def create_new_playlist(self):
        """Yeni playlist oluştur"""
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "Yeni Playlist", "Playlist adı:")
        if ok and name:
            playlist_id = self.music_app.playlist_manager.create_playlist(name)
            self.refresh_playlists()
            self.status_bar.showMessage(f"Playlist oluşturuldu: {name}")

    def on_playlist_selected(self, item):
        """Playlist seçildiğinde"""
        playlist_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_playlist = playlist_id

        playlist = self.music_app.playlist_manager.get_playlist(playlist_id)
        self.current_playlist_label.setText(f"Playlist: {playlist['name']}")

        # Şarkıları listele
        self.refresh_playlist_tracks()

    def refresh_playlist_tracks(self):
        """Playlist şarkılarını yenile"""
        if not self.current_playlist:
            return

        self.tracks_list.clear()
        tracks = self.music_app.playlist_manager.get_playlist_tracks(self.current_playlist)
        self.playlist_tracks = tracks

        for track in tracks:
            item_text = f"{track['artist']} - {track['title']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.tracks_list.addItem(item)

    def on_track_double_clicked(self, item):
        """Şarkıya çift tıklandığında çal"""
        track = item.data(Qt.ItemDataRole.UserRole)
        self.current_track_index = self.tracks_list.row(item)
        self.play_track(track)

    def delete_playlist(self):
        """Seçili playlist'i sil"""
        if not self.current_playlist:
            return

        reply = QMessageBox.question(self, "Playlist Sil",
                                     "Bu playlist'i silmek istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.music_app.playlist_manager.delete_playlist(self.current_playlist)
            self.current_playlist = None
            self.refresh_playlists()
            self.status_bar.showMessage("Playlist silindi")

    def remove_track_from_playlist(self):
        """Seçili şarkıyı playlist'ten çıkar"""
        current_item = self.tracks_list.currentItem()
        if not current_item or not self.current_playlist:
            return

        track = current_item.data(Qt.ItemDataRole.UserRole)
        self.music_app.playlist_manager.remove_track_from_playlist(
            self.current_playlist, track['id']
        )
        self.refresh_playlist_tracks()
        self.status_bar.showMessage("Şarkı playlist'ten çıkarıldı")

    # === ARAMA METHODLARI ===

    def perform_search(self):
        """Arama yap"""
        query = self.search_input.text().strip()
        if not query:
            return

        source_map = {"Tümü": "all", "Spotify": "spotify", "YouTube Music": "youtube"}
        source = source_map.get(self.search_source.currentText(), "all")

        self.status_bar.showMessage(f"Aranıyor: {query}...")

        results = self.music_app.stream_manager.search(query, source=source, limit=20)

        self.search_results_list.clear()
        self.search_results = results

        for track in results:
            source_icon = "🎵" if track['source'] == 'spotify' else "📺"
            item_text = f"{source_icon} {track['artist']} - {track['title']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.search_results_list.addItem(item)

        self.tabs.setCurrentWidget(self.search_tab)
        self.search_results_label.setText(f"{len(results)} sonuç bulundu")
        self.status_bar.showMessage(f"{len(results)} sonuç bulundu")

    def play_search_result(self):
        """Arama sonucunu çal"""
        current_item = self.search_results_list.currentItem()
        if current_item:
            track = current_item.data(Qt.ItemDataRole.UserRole)
            self.play_track(track)

    def add_search_result_to_playlist(self):
        """Arama sonucunu playlist'e ekle"""
        current_item = self.search_results_list.currentItem()
        if not current_item or not self.current_playlist:
            QMessageBox.warning(self, "Uyarı", "Önce bir playlist seçin")
            return

        track = current_item.data(Qt.ItemDataRole.UserRole)
        self.music_app.playlist_manager.add_track_to_playlist(self.current_playlist, track)
        self.status_bar.showMessage("Şarkı playlist'e eklendi")

    # === FAVORİLER ===

    def refresh_favorites(self):
        """Favori şarkıları yenile"""
        self.favorites_list.clear()
        favorites = self.music_app.db_manager.get_favorites()

        for track in favorites:
            item_text = f"{track['artist']} - {track['title']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, track)
            self.favorites_list.addItem(item)

    def add_to_favorites(self):
        """Seçili şarkıyı favorilere ekle"""
        current_item = self.tracks_list.currentItem()
        if not current_item:
            return

        track = current_item.data(Qt.ItemDataRole.UserRole)
        self.music_app.db_manager.set_favorite(track['id'], True)
        self.refresh_favorites()
        self.status_bar.showMessage("Favorilere eklendi")

    def remove_from_favorites(self):
        """Şarkıyı favorilerden çıkar"""
        current_item = self.favorites_list.currentItem()
        if not current_item:
            return

        track = current_item.data(Qt.ItemDataRole.UserRole)
        self.music_app.db_manager.set_favorite(track['id'], False)
        self.refresh_favorites()
        self.status_bar.showMessage("Favorilerden çıkarıldı")

    def play_favorite(self):
        """Favori şarkıyı çal"""
        current_item = self.favorites_list.currentItem()
        if current_item:
            track = current_item.data(Qt.ItemDataRole.UserRole)
            self.play_track(track)

    # === RADYO ===

    def search_radio_stations(self):
        """Radyo istasyonları ara"""
        country = self.radio_country_combo.currentText()
        genre = self.radio_genre_combo.currentText()

        if country == "Tümü":
            country = ""
        if genre == "Tümü":
            genre = ""

        self.status_bar.showMessage("Radyo istasyonları aranıyor...")

        stations = self.music_app.radio_browser.search_stations(
            country=country, tag=genre, limit=50
        )

        self.radio_list.clear()

        for station in stations:
            item_text = f"{station['name']} - {station['country']} ({station['codec']} {station['bitrate']}kbps)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, station)
            self.radio_list.addItem(item)

        self.status_bar.showMessage(f"{len(stations)} radyo istasyonu bulundu")

    def play_radio_station(self):
        """Radyo istasyonu çal"""
        current_item = self.radio_list.currentItem()
        if not current_item:
            return

        station = current_item.data(Qt.ItemDataRole.UserRole)

        # Radyo moduna geç
        self.is_radio_mode = True

        # Stream URL al ve çal
        stream_url = station['stream_url']

        track_info = {
            'title': station['name'],
            'artist': f"{station['country']} - {', '.join(station['tags'][:3])}",
            'source': 'radio'
        }

        self.music_app.audio_player.play(stream_url, track_info)
        self.update_now_playing_info(track_info)
        self.play_pause_button.setText("⏸")

        self.status_bar.showMessage(f"Radyo çalıyor: {station['name']}")

    # === EQUALIZER ===

    def on_eq_preset_changed(self, preset_name):
        """EQ preset değiştiğinde"""
        self.music_app.equalizer.load_preset(preset_name)
        self.update_eq_sliders()
        self.apply_equalizer()

    def on_eq_slider_changed(self, band_index, value):
        """EQ slider değiştiğinde"""
        gain_db = value / 10.0  # -20 ile +20 dB
        self.music_app.equalizer.set_band_gain(band_index, gain_db)
        self.apply_equalizer()

    def update_eq_sliders(self):
        """EQ slider'ları güncelle"""
        gains = self.music_app.equalizer.get_all_gains()
        for i, gain in enumerate(gains):
            self.eq_sliders[i].setValue(int(gain * 10))

    def toggle_equalizer(self):
        """Equalizer'ı aç/kapa"""
        self.music_app.equalizer.toggle_enable()
        self.eq_enable_check.setChecked(self.music_app.equalizer.is_enabled())
        self.apply_equalizer()

    def apply_equalizer(self):
        """Equalizer ayarlarını player'a uygula"""
        eq_values = self.music_app.equalizer.get_vlc_equalizer_values()
        self.music_app.audio_player.set_equalizer(eq_values)

    # === PLAYER CONTROLS ===

    def play_track(self, track):
        """Şarkı çal"""
        self.is_radio_mode = False

        # Stream URL al
        stream_url = self.music_app.stream_manager.get_stream_url(track)

        if not stream_url:
            QMessageBox.warning(self, "Hata", "Şarkı stream URL'i alınamadı")
            return

        # Çal
        self.music_app.audio_player.play(stream_url, track)

        # UI güncelle
        self.update_now_playing_info(track)
        self.play_pause_button.setText("⏸")

        # History'e ekle
        self.music_app.db_manager.add_to_history(track['id'])

        self.status_bar.showMessage(f"Çalınıyor: {track['artist']} - {track['title']}")

    def toggle_play_pause(self):
        """Play/Pause toggle"""
        if self.music_app.audio_player.is_playing():
            self.music_app.audio_player.pause()
            self.play_pause_button.setText("▶")
        elif self.music_app.audio_player.is_paused():
            self.music_app.audio_player.resume()
            self.play_pause_button.setText("⏸")

    def play_next(self):
        """Sonraki şarkıyı çal"""
        if self.is_radio_mode or not self.playlist_tracks:
            return

        self.current_track_index = (self.current_track_index + 1) % len(self.playlist_tracks)
        next_track = self.playlist_tracks[self.current_track_index]
        self.play_track(next_track)

    def play_previous(self):
        """Önceki şarkıyı çal"""
        if self.is_radio_mode or not self.playlist_tracks:
            return

        self.current_track_index = (self.current_track_index - 1) % len(self.playlist_tracks)
        prev_track = self.playlist_tracks[self.current_track_index]
        self.play_track(prev_track)

    def on_track_ended(self):
        """Şarkı bittiğinde otomatik sonrakini çal"""
        if not self.is_radio_mode:
            self.play_next()

    def on_volume_changed(self, value):
        """Ses seviyesi değiştiğinde"""
        self.music_app.audio_player.set_volume(value)

    def on_progress_slider_moved(self, position):
        """Progress slider hareket ettirildiğinde"""
        # Position 0-1000 arası, 0-1 arası çevir
        new_position = position / 1000.0
        self.music_app.audio_player.set_position(new_position)

    def update_progress(self):
        """Progress bar'ı güncelle"""
        if self.music_app.audio_player.is_playing() and not self.is_radio_mode:
            current_time = self.music_app.audio_player.get_time() // 1000  # Saniye
            total_time = self.music_app.audio_player.get_length() // 1000

            if total_time > 0:
                position = int((current_time / total_time) * 1000)
                self.progress_slider.setValue(position)

                self.current_time_label.setText(self.format_time(current_time))
                self.total_time_label.setText(self.format_time(total_time))

    def format_time(self, seconds):
        """Saniyeyi MM:SS formatına çevir"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"

    def update_now_playing_info(self, track):
        """Çalan şarkı bilgilerini güncelle"""
        self.track_title_label.setText(track.get('title', 'Unknown'))
        self.track_artist_label.setText(track.get('artist', ''))

        # TODO: Thumbnail yükle

    # === IMPORT/EXPORT ===

    def import_playlist(self):
        """Playlist import et"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Playlist İçe Aktar",
            "", "Playlist Files (*.m3u *.m3u8 *.json *.xspf)"
        )

        if file_path:
            file_path = Path(file_path)
            format_type = self.music_app.playlist_import_export.auto_detect_format(file_path)

            if format_type == 'm3u':
                playlist_id = self.music_app.playlist_import_export.import_from_m3u(file_path)
            elif format_type == 'json':
                playlist_id = self.music_app.playlist_import_export.import_from_json(file_path)
            else:
                QMessageBox.warning(self, "Hata", "Desteklenmeyen dosya formatı")
                return

            if playlist_id:
                self.refresh_playlists()
                self.status_bar.showMessage("Playlist import edildi")
            else:
                QMessageBox.warning(self, "Hata", "Playlist import edilemedi")

    def export_playlist(self):
        """Playlist export et"""
        if not self.current_playlist:
            QMessageBox.warning(self, "Uyarı", "Önce bir playlist seçin")
            return

        file_path, filter_used = QFileDialog.getSaveFileName(
            self, "Playlist Dışa Aktar",
            "", "M3U Playlist (*.m3u);;JSON Playlist (*.json);;XSPF Playlist (*.xspf)"
        )

        if file_path:
            file_path = Path(file_path)

            if "M3U" in filter_used:
                success = self.music_app.playlist_import_export.export_to_m3u(
                    self.current_playlist, file_path
                )
            elif "JSON" in filter_used:
                success = self.music_app.playlist_import_export.export_to_json(
                    self.current_playlist, file_path
                )
            elif "XSPF" in filter_used:
                success = self.music_app.playlist_import_export.export_to_xspf(
                    self.current_playlist, file_path
                )
            else:
                success = False

            if success:
                self.status_bar.showMessage("Playlist export edildi")
            else:
                QMessageBox.warning(self, "Hata", "Playlist export edilemedi")

    # === DİĞER ===

    def open_mini_player(self):
        """Mini player aç"""
        # TODO: Mini player window oluştur
        QMessageBox.information(self, "Mini Player", "Mini Player özelliği yakında eklenecek")

    def open_api_settings(self):
        """API ayarları aç"""
        # TODO: API settings dialog oluştur
        QMessageBox.information(self, "API Ayarları", "API ayarları yakında eklenecek")

    def show_about(self):
        """Hakkında diyaloğu göster"""
        QMessageBox.about(self, "Hakkında",
                         "<h2>Müzik Çalar</h2>"
                         "<p>Versiyon 1.0.0</p>"
                         "<p>Multi-platform music player with streaming support</p>"
                         "<p>Spotify, YouTube Music ve Online Radyo desteği</p>")

    def closeEvent(self, event):
        """Pencere kapatılırken"""
        self.music_app.save_settings()
        event.accept()

"""
Müzik Çalar - 10-Band Equalizer
"""
import numpy as np
from scipy import signal
from typing import List, Dict, Optional
from enum import Enum


class EqualizerBand(Enum):
    """10-band equalizer frekans bantları"""
    BAND_31HZ = (31, 0)
    BAND_62HZ = (62, 1)
    BAND_125HZ = (125, 2)
    BAND_250HZ = (250, 3)
    BAND_500HZ = (500, 4)
    BAND_1KHZ = (1000, 5)
    BAND_2KHZ = (2000, 6)
    BAND_4KHZ = (4000, 7)
    BAND_8KHZ = (8000, 8)
    BAND_16KHZ = (16000, 9)


class Equalizer:
    """10-band parametric equalizer"""

    # Band center frequencies (Hz)
    FREQUENCIES = [31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

    # Default Q factor (bandwidth)
    DEFAULT_Q = 1.0

    def __init__(self, sample_rate: int = 44100):
        """
        Equalizer başlat

        Args:
            sample_rate: Örnekleme hızı (Hz)
        """
        self.sample_rate = sample_rate
        self.gains = [0.0] * 10  # dB cinsinden, -20 ile +20 arası
        self.enabled = True

        # Preset'ler
        self.presets: Dict[str, List[float]] = {
            "Flat": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "Pop": [-1, -0.5, 0, 2, 4, 4, 2, 0, -0.5, -1],
            "Rock": [4, 3, -2, -3, -1, 1, 3, 4, 4, 4],
            "Jazz": [3, 2, 1, 1, -1, -1, 0, 1, 2, 3],
            "Classical": [3, 2, -1, -1, 0, 0, -1, -1, 2, 3],
            "Bass Boost": [6, 5, 4, 2, 0, -1, -2, -2, -2, -2],
            "Treble Boost": [-2, -2, -2, -1, 0, 2, 4, 5, 6, 6],
            "Vocal": [-2, -1, 1, 3, 3, 2, 1, -1, -2, -3],
            "Electronic": [3, 3, 1, 0, -2, 1, 0, 1, 3, 4],
            "Latin": [4, 2, 0, 0, -2, -2, -2, 0, 3, 4],
        }

        self.current_preset = "Flat"

    def set_band_gain(self, band_index: int, gain_db: float):
        """
        Belirli bir bandın gain'ini ayarla

        Args:
            band_index: Band index (0-9)
            gain_db: Gain değeri (dB, -20 ile +20 arası)
        """
        if 0 <= band_index < 10:
            self.gains[band_index] = max(-20, min(20, gain_db))
            self.current_preset = "Custom"

    def get_band_gain(self, band_index: int) -> float:
        """Band gain değerini al"""
        if 0 <= band_index < 10:
            return self.gains[band_index]
        return 0.0

    def set_all_gains(self, gains: List[float]):
        """
        Tüm band gain'lerini ayarla

        Args:
            gains: 10 elemanlı gain listesi (dB)
        """
        if len(gains) == 10:
            self.gains = [max(-20, min(20, g)) for g in gains]
            self.current_preset = "Custom"

    def get_all_gains(self) -> List[float]:
        """Tüm band gain'lerini al"""
        return self.gains.copy()

    def load_preset(self, preset_name: str) -> bool:
        """
        Preset yükle

        Args:
            preset_name: Preset adı

        Returns:
            True: Başarılı, False: Preset bulunamadı
        """
        if preset_name in self.presets:
            self.gains = self.presets[preset_name].copy()
            self.current_preset = preset_name
            return True
        return False

    def save_custom_preset(self, name: str):
        """
        Mevcut ayarları preset olarak kaydet

        Args:
            name: Preset adı
        """
        self.presets[name] = self.gains.copy()
        self.current_preset = name

    def get_preset_names(self) -> List[str]:
        """Tüm preset isimlerini al"""
        return list(self.presets.keys())

    def reset(self):
        """Equalizer'ı sıfırla (Flat preset)"""
        self.load_preset("Flat")

    def toggle_enable(self):
        """Equalizer'ı aç/kapa"""
        self.enabled = not self.enabled

    def is_enabled(self) -> bool:
        """Equalizer aktif mi?"""
        return self.enabled

    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Audio veriye equalizer uygula

        Args:
            audio_data: Numpy array (mono veya stereo)

        Returns:
            İşlenmiş audio data
        """
        if not self.enabled:
            return audio_data

        # Her band için peaking filter uygula
        processed = audio_data.copy()

        for i, (freq, gain) in enumerate(zip(self.FREQUENCIES, self.gains)):
            if abs(gain) > 0.1:  # Küçük gain'leri skip et
                processed = self._apply_peaking_filter(
                    processed, freq, gain, self.DEFAULT_Q
                )

        return processed

    def _apply_peaking_filter(self, audio_data: np.ndarray, center_freq: float,
                              gain_db: float, q: float) -> np.ndarray:
        """
        Peaking (bell) filter uygula

        Args:
            audio_data: Audio veri
            center_freq: Merkez frekans (Hz)
            gain_db: Gain (dB)
            q: Q factor (bandwidth)

        Returns:
            Filtrelenmiş audio
        """
        # Normalize frequency
        w0 = 2 * np.pi * center_freq / self.sample_rate

        # Gain linear
        A = 10 ** (gain_db / 40)

        # Alpha
        alpha = np.sin(w0) / (2 * q)

        # Biquad coefficients
        b0 = 1 + alpha * A
        b1 = -2 * np.cos(w0)
        b2 = 1 - alpha * A
        a0 = 1 + alpha / A
        a1 = -2 * np.cos(w0)
        a2 = 1 - alpha / A

        # Normalize
        b = np.array([b0, b1, b2]) / a0
        a = np.array([1, a1 / a0, a2 / a0])

        # Apply filter
        if audio_data.ndim == 1:
            # Mono
            return signal.lfilter(b, a, audio_data)
        else:
            # Stereo
            left = signal.lfilter(b, a, audio_data[:, 0])
            right = signal.lfilter(b, a, audio_data[:, 1])
            return np.column_stack((left, right))

    def get_frequency_response(self, num_points: int = 1000) -> tuple:
        """
        Equalizer frekans cevabını hesapla (görselleştirme için)

        Args:
            num_points: Hesaplama noktası sayısı

        Returns:
            (frequencies, magnitude_db) tuple
        """
        # Frekans dizisi (logaritmik)
        freqs = np.logspace(np.log10(20), np.log10(20000), num_points)

        # Her frekans için toplam gain hesapla
        magnitude = np.ones(num_points)

        for i, (center_freq, gain_db) in enumerate(zip(self.FREQUENCIES, self.gains)):
            if abs(gain_db) > 0.1:
                # Her band için peaking filter response
                w0 = 2 * np.pi * center_freq / self.sample_rate
                A = 10 ** (gain_db / 40)
                alpha = np.sin(w0) / (2 * self.DEFAULT_Q)

                # Biquad coefficients
                b0 = 1 + alpha * A
                b1 = -2 * np.cos(w0)
                b2 = 1 - alpha * A
                a0 = 1 + alpha / A
                a1 = -2 * np.cos(w0)
                a2 = 1 - alpha / A

                b = np.array([b0, b1, b2]) / a0
                a = np.array([1, a1 / a0, a2 / a0])

                # Frequency response
                w, h = signal.freqz(b, a, worN=2 * np.pi * freqs / self.sample_rate)
                magnitude *= np.abs(h)

        # Convert to dB
        magnitude_db = 20 * np.log10(magnitude + 1e-10)

        return freqs, magnitude_db

    def export_settings(self) -> Dict:
        """
        Equalizer ayarlarını export et

        Returns:
            Settings dictionary
        """
        return {
            'enabled': self.enabled,
            'preset': self.current_preset,
            'gains': self.gains.copy(),
            'custom_presets': {k: v for k, v in self.presets.items() if k not in [
                "Flat", "Pop", "Rock", "Jazz", "Classical",
                "Bass Boost", "Treble Boost", "Vocal", "Electronic", "Latin"
            ]}
        }

    def import_settings(self, settings: Dict):
        """
        Equalizer ayarlarını import et

        Args:
            settings: Settings dictionary
        """
        self.enabled = settings.get('enabled', True)
        self.gains = settings.get('gains', [0] * 10)
        self.current_preset = settings.get('preset', 'Custom')

        # Custom preset'leri ekle
        custom_presets = settings.get('custom_presets', {})
        self.presets.update(custom_presets)

    def get_band_frequency(self, band_index: int) -> int:
        """Band frekansını al"""
        if 0 <= band_index < 10:
            return self.FREQUENCIES[band_index]
        return 0

    def get_vlc_equalizer_values(self) -> List[float]:
        """
        VLC için equalizer değerlerini al
        VLC kullanırken bu değerler kullanılmalı

        Returns:
            10 elemanlı gain listesi
        """
        return self.gains.copy()

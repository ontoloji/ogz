"""
Altyazı overlay modülü
Ekran üzerinde şeffaf bir pencerede altyazı gösterir
"""
import tkinter as tk
from tkinter import font
import threading
from config import Config

class SubtitleOverlay:
    def __init__(self):
        self.config = Config()
        self.root = None
        self.label_en = None
        self.label_tr = None
        self.is_running = False

    def create_window(self):
        """Overlay penceresini oluştur"""
        # Zaten bir pencere varsa yeni pencere oluşturma
        if self.root is not None:
            return
        
        self.root = tk.Tk()

        # Pencere ayarları
        self.root.title("Meeting Translator")

        # Ekranın boyutunu al
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Pencere boyutunu ayarla
        window_width = self.config.SUBTITLE_WIDTH
        window_height = self.config.SUBTITLE_HEIGHT

        # Pencereyi konumlandır
        if self.config.SUBTITLE_POSITION == "bottom":
            x = (screen_width - window_width) // 2
            y = screen_height - window_height - 50
        else:  # top
            x = (screen_width - window_width) // 2
            y = 50

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Pencereyi her zaman üstte tut
        self.root.attributes('-topmost', True)

        # Pencereyi şeffaf yap (Windows)
        try:
            self.root.attributes('-alpha', self.config.SUBTITLE_OPACITY)
        except:
            pass

        # Pencereyi taşınabilir yap ama çerçevesiz
        self.root.overrideredirect(True)

        # Arkaplan rengi
        self.root.configure(bg=self.config.SUBTITLE_BG_COLOR)

        # Kapatma butonu için frame
        control_frame = tk.Frame(self.root, bg=self.config.SUBTITLE_BG_COLOR)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        # Küçük kontrol butonları
        btn_close = tk.Button(
            control_frame,
            text="✕",
            command=self.stop,
            bg="#FF4444",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            width=3
        )
        btn_close.pack(side=tk.RIGHT, padx=2, pady=2)

        btn_minimize = tk.Button(
            control_frame,
            text="−",
            command=self.minimize,
            bg="#444444",
            fg="white",
            relief=tk.FLAT,
            font=("Arial", 10, "bold"),
            width=3
        )
        btn_minimize.pack(side=tk.RIGHT, padx=2, pady=2)

        # Başlık (taşımak için)
        title_label = tk.Label(
            control_frame,
            text="Meeting Translator - Sürükle",
            bg=self.config.SUBTITLE_BG_COLOR,
            fg=self.config.SUBTITLE_TEXT_COLOR,
            font=("Arial", 8)
        )
        title_label.pack(side=tk.LEFT, padx=5)

        # Pencereyi taşıma işlevselliği
        title_label.bind('<Button-1>', self.start_move)
        title_label.bind('<B1-Motion>', self.do_move)
        control_frame.bind('<Button-1>', self.start_move)
        control_frame.bind('<B1-Motion>', self.do_move)

        # Ana içerik frame
        content_frame = tk.Frame(self.root, bg=self.config.SUBTITLE_BG_COLOR)
        content_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        # Font ayarları
        subtitle_font = font.Font(
            family="Arial",
            size=self.config.SUBTITLE_FONT_SIZE,
            weight="bold"
        )

        small_font = font.Font(
            family="Arial",
            size=int(self.config.SUBTITLE_FONT_SIZE * 0.7)
        )

        # İngilizce metin (orijinal) - küçük font
        self.label_en = tk.Label(
            content_frame,
            text="",
            fg="#AAAAAA",
            bg=self.config.SUBTITLE_BG_COLOR,
            font=small_font,
            wraplength=window_width - 20,
            justify=tk.CENTER
        )
        self.label_en.pack(expand=True)

        # Türkçe metin (çeviri) - büyük font
        self.label_tr = tk.Label(
            content_frame,
            text="Altyazılar burada görünecek...",
            fg=self.config.SUBTITLE_TEXT_COLOR,
            bg=self.config.SUBTITLE_BG_COLOR,
            font=subtitle_font,
            wraplength=window_width - 20,
            justify=tk.CENTER
        )
        self.label_tr.pack(expand=True)

        self.is_running = True

        # Pencere kapatma olayı
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

    def start_move(self, event):
        """Pencereyi taşımaya başla"""
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        """Pencereyi taşı"""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def minimize(self):
        """Pencereyi küçült"""
        self.root.withdraw()
        # 3 saniye sonra tekrar göster
        self.root.after(3000, self.root.deiconify)

    def update_text(self, english_text, turkish_text):
        """Altyazı metnini güncelle"""
        if self.root and self.is_running:
            self.root.after(0, lambda: self._update_labels(english_text, turkish_text))

    def _update_labels(self, english_text, turkish_text):
        """Label'ları güncelle (thread-safe)"""
        if self.label_en:
            self.label_en.config(text=english_text)
        if self.label_tr:
            self.label_tr.config(text=turkish_text)

    def clear_text(self):
        """Altyazı metnini temizle"""
        self.update_text("", "")

    def run(self):
        """Pencereyi başlat (blocking)"""
        if self.root is None:
            self.create_window()
        self.root.mainloop()

    def run_async(self):
        """Pencereyi asenkron başlat"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def stop(self):
        """Pencereyi kapat"""
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()


if __name__ == "__main__":
    # Test kodu
    overlay = SubtitleOverlay()
    overlay.create_window()

    # Test metinleri
    import time

    def test_updates():
        time.sleep(2)
        overlay.update_text(
            "Hello, how are you?",
            "Merhaba, nasılsınız?"
        )

        time.sleep(3)
        overlay.update_text(
            "This is a test of the subtitle system.",
            "Bu altyazı sisteminin bir testidir."
        )

        time.sleep(3)
        overlay.update_text(
            "Thank you for your attention.",
            "İlginiz için teşekkür ederim."
        )

    test_thread = threading.Thread(target=test_updates, daemon=True)
    test_thread.start()

    overlay.root.mainloop()

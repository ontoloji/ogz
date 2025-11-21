"""
Windows AI Kişisel Asistan
Ana Uygulama Dosyası
"""

import sys
import threading
import keyboard
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import scrolledtext, messagebox

from database import Database
from nlp_processor import NLPProcessor
from automation import AutomationManager
from file_search import FileSearcher


class AIAssistant:
    def __init__(self):
        self.db = Database()
        self.nlp = NLPProcessor(self.db)
        self.automation = AutomationManager(self.db)
        self.file_searcher = FileSearcher()

        self.icon = None
        self.window = None
        self.running = True

        # Global hotkey ayarı (Ctrl+Shift+A)
        self.setup_hotkey()

    def setup_hotkey(self):
        """Global hotkey'i yapılandır"""
        try:
            keyboard.add_hotkey('ctrl+shift+a', self.show_assistant_window)
        except Exception as e:
            print(f"Hotkey ayarlanamadı: {e}")

    def create_image(self):
        """System tray için icon oluştur"""
        # Basit bir daire icon
        width = 64
        height = 64
        color1 = "blue"
        color2 = "white"

        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse((width // 4, height // 4, 3 * width // 4, 3 * height // 4), fill=color2)

        return image

    def show_assistant_window(self):
        """Asistan penceresini göster"""
        if self.window is None or not self.window.winfo_exists():
            self.window = AssistantWindow(self)
        else:
            self.window.lift()
            self.window.focus_force()

    def quit_app(self):
        """Uygulamayı kapat"""
        self.running = False
        self.automation.stop()
        if self.icon:
            self.icon.stop()
        if self.window and self.window.winfo_exists():
            self.window.destroy()
        keyboard.unhook_all()
        sys.exit(0)

    def setup_tray_icon(self):
        """System tray icon'u ayarla"""
        menu = Menu(
            MenuItem('Asistanı Aç', self.show_assistant_window),
            MenuItem('Hatırlatıcılar', self.show_reminders),
            MenuItem('Notlar', self.show_notes),
            MenuItem('Çıkış', self.quit_app)
        )

        self.icon = Icon("AI Asistan", self.create_image(), "AI Kişisel Asistan", menu)

    def show_reminders(self):
        """Hatırlatıcıları göster"""
        reminders = self.db.get_active_reminders()
        msg = "Aktif Hatırlatıcılar:\n\n"
        if reminders:
            for r in reminders:
                msg += f"• {r[2]} - {r[3]}\n"
        else:
            msg = "Aktif hatırlatıcı bulunmuyor."
        messagebox.showinfo("Hatırlatıcılar", msg)

    def show_notes(self):
        """Notları göster"""
        notes = self.db.get_all_notes()
        msg = "Notlarım:\n\n"
        if notes:
            for n in notes:
                msg += f"• {n[1]}\n"
        else:
            msg = "Henüz not bulunmuyor."
        messagebox.showinfo("Notlar", msg)

    def run(self):
        """Uygulamayı başlat"""
        # Otomasyonu başlat
        self.automation.start()

        # System tray icon'u ayarla ve çalıştır
        self.setup_tray_icon()

        print("AI Asistan başlatıldı!")
        print("Ctrl+Shift+A ile asistanı açabilirsiniz.")

        # Tray icon'u çalıştır (blocking)
        self.icon.run()


class AssistantWindow(tk.Toplevel):
    """Asistan penceresi"""

    def __init__(self, assistant):
        super().__init__()
        self.assistant = assistant

        self.title("AI Kişisel Asistan")
        self.geometry("600x500")
        self.configure(bg='#2b2b2b')

        self.setup_ui()

        # Pencere kapatıldığında sadece gizle
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def setup_ui(self):
        """UI bileşenlerini oluştur"""
        # Başlık
        header = tk.Label(
            self,
            text="🤖 AI Kişisel Asistan",
            font=("Arial", 16, "bold"),
            bg='#2b2b2b',
            fg='white'
        )
        header.pack(pady=10)

        # Konuşma geçmişi
        self.chat_history = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 10),
            bg='#1e1e1e',
            fg='white',
            insertbackground='white'
        )
        self.chat_history.pack(padx=10, pady=5)
        self.chat_history.config(state=tk.DISABLED)

        # Giriş çerçevesi
        input_frame = tk.Frame(self, bg='#2b2b2b')
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Komut giriş alanı
        self.command_entry = tk.Entry(
            input_frame,
            font=("Arial", 11),
            bg='#1e1e1e',
            fg='white',
            insertbackground='white'
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.command_entry.bind('<Return>', self.process_command)

        # Gönder butonu
        send_btn = tk.Button(
            input_frame,
            text="Gönder",
            command=self.process_command,
            bg='#0d7377',
            fg='white',
            font=("Arial", 10, "bold"),
            relief=tk.FLAT,
            padx=20
        )
        send_btn.pack(side=tk.RIGHT)

        # Hoşgeldin mesajı
        self.add_message("Asistan", "Merhaba! Size nasıl yardımcı olabilirim?")
        self.add_message("Asistan", "Örnek komutlar:\n" +
                        "• 'yarın saat 10'da toplantı hatırlat'\n" +
                        "• 'proje fikirleri diye bir not al'\n" +
                        "• 'chrome'u aç'\n" +
                        "• '15 çarpı 8 kaç'\n" +
                        "• 'python dosyalarını ara'")

    def add_message(self, sender, message):
        """Sohbet geçmişine mesaj ekle"""
        self.chat_history.config(state=tk.NORMAL)

        if sender == "Siz":
            self.chat_history.insert(tk.END, f"\n{'='*60}\n", "separator")
            self.chat_history.insert(tk.END, f"➤ Siz: ", "you")
            self.chat_history.insert(tk.END, f"{message}\n", "you_msg")
        else:
            self.chat_history.insert(tk.END, f"🤖 Asistan: ", "assistant")
            self.chat_history.insert(tk.END, f"{message}\n", "assistant_msg")

        # Renk etiketleri
        self.chat_history.tag_config("you", foreground="#4CAF50", font=("Arial", 10, "bold"))
        self.chat_history.tag_config("you_msg", foreground="white")
        self.chat_history.tag_config("assistant", foreground="#2196F3", font=("Arial", 10, "bold"))
        self.chat_history.tag_config("assistant_msg", foreground="#e0e0e0")
        self.chat_history.tag_config("separator", foreground="#555555")

        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def process_command(self, event=None):
        """Kullanıcı komutunu işle"""
        command = self.command_entry.get().strip()

        if not command:
            return

        # Komutu göster
        self.add_message("Siz", command)
        self.command_entry.delete(0, tk.END)

        # Komutu işle
        response = self.assistant.nlp.process_command(command)

        # Cevabı göster
        self.add_message("Asistan", response)


def main():
    """Ana fonksiyon"""
    try:
        app = AIAssistant()
        app.run()
    except KeyboardInterrupt:
        print("\nUygulama kapatılıyor...")
        sys.exit(0)
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

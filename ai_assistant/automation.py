"""
Otomasyon Modülü
Hatırlatıcıları kontrol eder ve zamanlanmış görevleri yönetir
"""

import threading
import time
from datetime import datetime
from tkinter import messagebox
import winsound


class AutomationManager:
    def __init__(self, database):
        self.db = database
        self.running = False
        self.thread = None
        self.check_interval = 30  # Saniye cinsinden kontrol aralığı

    def start(self):
        """Otomasyon sistemini başlat"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._automation_loop, daemon=True)
            self.thread.start()
            print("Otomasyon sistemi başlatıldı.")

    def stop(self):
        """Otomasyon sistemini durdur"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Otomasyon sistemi durduruldu.")

    def _automation_loop(self):
        """Ana otomasyon döngüsü"""
        while self.running:
            try:
                # Hatırlatıcıları kontrol et
                self._check_reminders()

                # Belirlenen süre kadar bekle
                time.sleep(self.check_interval)

            except Exception as e:
                print(f"Otomasyon hatası: {e}")
                time.sleep(self.check_interval)

    def _check_reminders(self):
        """Zamanı gelmiş hatırlatıcıları kontrol et"""
        try:
            due_reminders = self.db.get_due_reminders()

            for reminder in due_reminders:
                reminder_id = reminder[0]
                title = reminder[1]
                description = reminder[2]
                remind_time = reminder[3]

                # Bildirimi göster
                self._show_notification(title, description, remind_time)

                # Hatırlatıcıyı tamamlandı olarak işaretle
                self.db.complete_reminder(reminder_id)

        except Exception as e:
            print(f"Hatırlatıcı kontrol hatası: {e}")

    def _show_notification(self, title, description, remind_time):
        """
        Hatırlatıcı bildirimi göster

        Windows için toast notification veya messagebox kullanır
        """
        try:
            # Ses çal (Windows beep)
            try:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except:
                pass

            # Mesaj oluştur
            message = f"⏰ Hatırlatma Zamanı!\n\n"
            message += f"📌 {title}\n"
            if description:
                message += f"\n{description}\n"
            message += f"\n⏰ Zaman: {remind_time}"

            # MessageBox göster (non-blocking)
            threading.Thread(
                target=lambda: messagebox.showinfo("Hatırlatıcı", message),
                daemon=True
            ).start()

            # Windows 10+ için toast notification denemesi
            try:
                self._show_windows_toast(title, description)
            except:
                pass

        except Exception as e:
            print(f"Bildirim gösterme hatası: {e}")

    def _show_windows_toast(self, title, description):
        """
        Windows 10+ toast notification göster
        (win10toast kütüphanesi gerektirir, opsiyonel)
        """
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()

            message = description if description else title

            toaster.show_toast(
                "AI Kişisel Asistan",
                f"⏰ {title}\n{message}",
                duration=10,
                threaded=True
            )
        except ImportError:
            # win10toast yüklü değilse sessizce geç
            pass
        except Exception as e:
            print(f"Toast notification hatası: {e}")

    def schedule_task(self, task_time, callback, *args, **kwargs):
        """
        Belirli bir zamanda çalışacak görev planla

        Args:
            task_time: Görev zamanı (datetime)
            callback: Çalıştırılacak fonksiyon
            *args, **kwargs: Fonksiyon parametreleri
        """
        def wait_and_execute():
            # Görev zamanına kadar bekle
            while datetime.now() < task_time and self.running:
                time.sleep(1)

            if self.running:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Zamanlanmış görev hatası: {e}")

        thread = threading.Thread(target=wait_and_execute, daemon=True)
        thread.start()

    def schedule_recurring_task(self, interval_seconds, callback, *args, **kwargs):
        """
        Belirli aralıklarla tekrarlanan görev planla

        Args:
            interval_seconds: Tekrar aralığı (saniye)
            callback: Çalıştırılacak fonksiyon
            *args, **kwargs: Fonksiyon parametreleri
        """
        def recurring_execute():
            while self.running:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Tekrarlanan görev hatası: {e}")

                time.sleep(interval_seconds)

        thread = threading.Thread(target=recurring_execute, daemon=True)
        thread.start()


# Test için
if __name__ == "__main__":
    from database import Database

    db = Database()
    automation = AutomationManager(db)

    # Test hatırlatıcısı ekle
    from datetime import timedelta
    test_time = (datetime.now() + timedelta(seconds=5)).strftime('%Y-%m-%d %H:%M:%S')
    db.add_reminder("Test Hatırlatıcı", test_time, "Bu bir test hatırlatıcısıdır")

    # Otomasyonu başlat
    automation.start()

    print("Otomasyon testi başlatıldı. 10 saniye beklenecek...")
    time.sleep(10)

    automation.stop()
    print("Test tamamlandı.")

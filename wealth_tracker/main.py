"""
Wealth Tracker - Finansal Birikim Takip Uygulaması
Cross-platform (Windows & macOS) masaüstü uygulaması
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import Database
from price_fetcher import PriceFetcher
import sys


class LoginWindow:
    """Giriş ekranı"""

    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.db = Database()

        self.root.title("Wealth Tracker - Giriş")
        self.root.geometry("400x300")
        self.center_window(400, 300)

        self.create_widgets()

    def center_window(self, width, height):
        """Pencereyi ekranın ortasına yerleştir"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Giriş ekranı bileşenlerini oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Başlık
        title_label = ttk.Label(
            main_frame,
            text="Wealth Tracker",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        subtitle_label = ttk.Label(
            main_frame,
            text="Finansal Birikim Takip Sistemi",
            font=("Arial", 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 30))

        # Kullanıcı adı
        ttk.Label(main_frame, text="Kullanıcı Adı:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.username_entry = ttk.Entry(main_frame, width=25)
        self.username_entry.grid(row=2, column=1, pady=5)

        # Şifre
        ttk.Label(main_frame, text="Şifre:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )
        self.password_entry = ttk.Entry(main_frame, width=25, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Giriş",
            command=self.login
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="Yeni Kullanıcı",
            command=self.register
        ).grid(row=0, column=1, padx=5)

        # Enter tuşu ile giriş
        self.password_entry.bind('<Return>', lambda e: self.login())

        # İlk alana odaklan
        self.username_entry.focus()

    def login(self):
        """Giriş yap"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        user_id = self.db.verify_user(username, password)

        if user_id:
            self.on_login_success(user_id, username)
        else:
            messagebox.showerror(
                "Hata",
                "Kullanıcı adı veya şifre yanlış!"
            )
            self.password_entry.delete(0, tk.END)

    def register(self):
        """Yeni kullanıcı kaydı"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        if len(password) < 4:
            messagebox.showwarning("Uyarı", "Şifre en az 4 karakter olmalı!")
            return

        if self.db.create_user(username, password):
            messagebox.showinfo(
                "Başarılı",
                "Kullanıcı oluşturuldu! Şimdi giriş yapabilirsiniz."
            )
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Hata",
                "Bu kullanıcı adı zaten kullanılıyor!"
            )


class MainWindow:
    """Ana uygulama penceresi"""

    def __init__(self, root, user_id, username):
        self.root = root
        self.user_id = user_id
        self.username = username
        self.db = Database()
        self.price_fetcher = PriceFetcher()

        self.root.title(f"Wealth Tracker - {username}")
        self.root.geometry("1000x700")
        self.center_window(1000, 700)

        self.create_widgets()
        self.refresh_data()

    def center_window(self, width, height):
        """Pencereyi ekranın ortasına yerleştir"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Ana pencere bileşenlerini oluştur"""
        # Ana container
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        # Üst panel - Özet bilgiler
        self.create_summary_panel(main_container)

        # Orta panel - Birikimler tablosu
        self.create_table_panel(main_container)

        # Alt panel - Kontroller
        self.create_control_panel(main_container)

    def create_summary_panel(self, parent):
        """Özet bilgi paneli"""
        summary_frame = ttk.LabelFrame(
            parent,
            text="Portföy Özeti",
            padding="10"
        )
        summary_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Toplam değer
        self.total_value_label = ttk.Label(
            summary_frame,
            text="Toplam Değer: Hesaplanıyor...",
            font=("Arial", 14, "bold")
        )
        self.total_value_label.grid(row=0, column=0, sticky=tk.W, padx=10)

        # Güncel fiyatlar butonu
        ttk.Button(
            summary_frame,
            text="Fiyatları Güncelle",
            command=self.update_prices
        ).grid(row=0, column=1, padx=10)

        # Fiyat bilgisi
        self.price_info_label = ttk.Label(
            summary_frame,
            text="",
            font=("Arial", 9)
        )
        self.price_info_label.grid(
            row=1, column=0, columnspan=2, sticky=tk.W, padx=10, pady=(5, 0)
        )

    def create_table_panel(self, parent):
        """Birikimler tablosu paneli"""
        table_frame = ttk.LabelFrame(parent, text="Birikimlerim", padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        # Treeview oluştur
        columns = (
            "Varlık Tipi", "Varlık Adı", "Miktar", "Alış Fiyatı",
            "Güncel Fiyat", "Toplam Değer", "Tarih", "Notlar"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        # Kolonları ayarla
        widths = [120, 120, 100, 100, 100, 120, 100, 200]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)

        # Scrollbar ekle
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

    def create_control_panel(self, parent):
        """Kontrol butonları paneli"""
        control_frame = ttk.Frame(parent, padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        ttk.Button(
            control_frame,
            text="Yeni Birikim Ekle",
            command=self.add_saving
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            control_frame,
            text="Seçili Kaydı Sil",
            command=self.delete_saving
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            control_frame,
            text="Yenile",
            command=self.refresh_data
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            control_frame,
            text="Çıkış",
            command=self.logout
        ).grid(row=0, column=3, padx=5)

    def add_saving(self):
        """Yeni birikim ekle"""
        dialog = AddSavingDialog(self.root, self.db, self.user_id)
        self.root.wait_window(dialog.dialog)
        self.refresh_data()

    def delete_saving(self):
        """Seçili birikim kaydını sil"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir kayıt seçin!")
            return

        if messagebox.askyesno("Onay", "Seçili kaydı silmek istediğinizden emin misiniz?"):
            item = self.tree.item(selected[0])
            saving_id = item['values'][0] if item['values'] else None

            # ID'yi tree'nin tag'lerinden al
            tags = self.tree.item(selected[0], 'tags')
            if tags:
                saving_id = int(tags[0])
                if self.db.delete_saving(saving_id, self.user_id):
                    messagebox.showinfo("Başarılı", "Kayıt silindi!")
                    self.refresh_data()
                else:
                    messagebox.showerror("Hata", "Kayıt silinemedi!")

    def update_prices(self):
        """Fiyatları güncelle"""
        self.price_fetcher.clear_cache()
        self.refresh_data()
        messagebox.showinfo("Başarılı", "Fiyatlar güncellendi!")

    def refresh_data(self):
        """Verileri yenile"""
        # Tabloyu temizle
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Birikimlerini getir
        savings = self.db.get_savings(self.user_id)

        total_value = 0.0

        for saving in savings:
            asset_type = saving['asset_type']
            asset_name = saving['asset_name']
            quantity = saving['quantity']
            purchase_price = saving['purchase_price'] or 0

            # Güncel fiyatı al
            current_price = self.price_fetcher.get_asset_price(
                asset_type, asset_name, "TRY"
            )

            # Değer hesapla
            if current_price:
                value = quantity * current_price
            elif purchase_price:
                value = quantity * purchase_price
                current_price = purchase_price
            else:
                value = 0
                current_price = 0

            total_value += value

            # Tabloya ekle
            self.tree.insert(
                '',
                'end',
                values=(
                    asset_type,
                    asset_name,
                    f"{quantity:.2f}",
                    f"{purchase_price:.2f} ₺" if purchase_price else "-",
                    f"{current_price:.2f} ₺" if current_price else "-",
                    f"{value:.2f} ₺",
                    saving['purchase_date'],
                    saving['notes']
                ),
                tags=(saving['id'],)
            )

        # Toplam değeri güncelle
        self.total_value_label.config(
            text=f"Toplam Değer: {total_value:,.2f} ₺"
        )

        # Güncel fiyat bilgilerini göster
        prices = self.price_fetcher.get_all_prices("TRY")
        price_text = " | ".join([f"{k}: {v:.2f} ₺" for k, v in prices.items()])
        self.price_info_label.config(text=price_text)

    def logout(self):
        """Çıkış yap"""
        if messagebox.askyesno("Çıkış", "Çıkmak istediğinizden emin misiniz?"):
            self.root.quit()


class AddSavingDialog:
    """Yeni birikim ekleme diyalogu"""

    def __init__(self, parent, db, user_id):
        self.db = db
        self.user_id = user_id

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Birikim Ekle")
        self.dialog.geometry("400x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """Dialog bileşenlerini oluştur"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        row = 0

        # Varlık Tipi
        ttk.Label(main_frame, text="Varlık Tipi:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.asset_type_combo = ttk.Combobox(
            main_frame,
            values=["Değerli Maden", "Döviz", "Vadeli Yatırım"],
            state="readonly",
            width=22
        )
        self.asset_type_combo.grid(row=row, column=1, pady=5)
        self.asset_type_combo.current(0)
        row += 1

        # Varlık Adı
        ttk.Label(main_frame, text="Varlık Adı:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.asset_name_combo = ttk.Combobox(
            main_frame,
            values=["Altın", "Gümüş", "Platin"],
            width=22
        )
        self.asset_name_combo.grid(row=row, column=1, pady=5)
        row += 1

        # Varlık tipine göre seçenekleri güncelle
        self.asset_type_combo.bind('<<ComboboxSelected>>', self.update_asset_names)

        # Miktar
        ttk.Label(main_frame, text="Miktar:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.quantity_entry = ttk.Entry(main_frame, width=25)
        self.quantity_entry.grid(row=row, column=1, pady=5)
        row += 1

        # Alış Fiyatı
        ttk.Label(main_frame, text="Alış Fiyatı (₺):").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.purchase_price_entry = ttk.Entry(main_frame, width=25)
        self.purchase_price_entry.grid(row=row, column=1, pady=5)
        row += 1

        # Alış Tarihi
        ttk.Label(main_frame, text="Alış Tarihi:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.purchase_date_entry = ttk.Entry(main_frame, width=25)
        self.purchase_date_entry.insert(
            0, datetime.now().strftime("%Y-%m-%d")
        )
        self.purchase_date_entry.grid(row=row, column=1, pady=5)
        row += 1

        # Notlar
        ttk.Label(main_frame, text="Notlar:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.notes_text = tk.Text(main_frame, width=25, height=5)
        self.notes_text.grid(row=row, column=1, pady=5)
        row += 1

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)

        ttk.Button(
            button_frame,
            text="Kaydet",
            command=self.save
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            button_frame,
            text="İptal",
            command=self.dialog.destroy
        ).grid(row=0, column=1, padx=5)

    def update_asset_names(self, event=None):
        """Varlık tipine göre varlık adlarını güncelle"""
        asset_type = self.asset_type_combo.get()

        if asset_type == "Değerli Maden":
            values = ["Altın", "Gümüş", "Platin", "Paladyum"]
        elif asset_type == "Döviz":
            values = ["Dolar", "Euro", "Pound", "Sterlin"]
        else:  # Vadeli Yatırım
            values = ["Mevduat", "Tahvil", "Bono", "Diğer"]

        self.asset_name_combo.config(values=values)
        self.asset_name_combo.set(values[0])

    def save(self):
        """Birikim kaydını kaydet"""
        try:
            asset_type = self.asset_type_combo.get()
            asset_name = self.asset_name_combo.get()
            quantity = float(self.quantity_entry.get())
            purchase_price_str = self.purchase_price_entry.get().strip()
            purchase_price = float(purchase_price_str) if purchase_price_str else None
            purchase_date = self.purchase_date_entry.get()
            notes = self.notes_text.get("1.0", tk.END).strip()

            if not asset_type or not asset_name:
                messagebox.showwarning("Uyarı", "Lütfen tüm gerekli alanları doldurun!")
                return

            if quantity <= 0:
                messagebox.showwarning("Uyarı", "Miktar 0'dan büyük olmalı!")
                return

            if self.db.add_saving(
                self.user_id, asset_type, asset_name, quantity,
                purchase_price, purchase_date, notes
            ):
                messagebox.showinfo("Başarılı", "Birikim kaydedildi!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Hata", "Birikim kaydedilemedi!")

        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli sayısal değerler girin!")


def main():
    """Ana uygulama başlangıcı"""
    root = tk.Tk()

    def on_login_success(user_id, username):
        """Giriş başarılı olduğunda"""
        # Giriş penceresini kapat
        for widget in root.winfo_children():
            widget.destroy()

        # Ana pencereyi aç
        MainWindow(root, user_id, username)

    # Giriş ekranını başlat
    LoginWindow(root, on_login_success)

    # Uygulamayı çalıştır
    root.mainloop()


if __name__ == "__main__":
    main()

"""
CAN Bus Analyzer - Ana GUI Uygulaması
Windows için Tkinter tabanlı CAN Bus veri analiz aracı.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sys
import os
import threading
import time
from datetime import datetime
from typing import Optional, List, Dict

# Modül importları
try:
    from can_reader import CANReader
    from dbc_parser import DBCParser
    from log_reader import LogReader
    from data_exporter import DataExporter
    from plotter import SignalPlotter
except ImportError:
    # Relative import için
    sys.path.insert(0, os.path.dirname(__file__))
    from can_reader import CANReader
    from dbc_parser import DBCParser
    from log_reader import LogReader
    from data_exporter import DataExporter
    from plotter import SignalPlotter


class CANAnalyzerGUI:
    """
    CAN Bus Analyzer ana GUI sınıfı.
    Tüm özellikleri tek bir arayüzde toplar.
    """

    def __init__(self, root):
        """
        GUI başlatıcı.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("CAN Bus Analyzer - v1.0")
        self.root.geometry("1400x900")

        # Modüller
        self.can_reader = CANReader()
        self.dbc_parser = DBCParser()
        self.log_reader = LogReader()
        self.data_exporter = DataExporter()
        self.plotter = SignalPlotter(max_points=1000)

        # Veri depolama
        self.recorded_messages: List[Dict] = []
        self.is_recording = False
        self.selected_signals: List[str] = []

        # GUI bileşenleri
        self.setup_menu()
        self.setup_main_layout()

        # Periyodik güncelleme
        self.update_interval = 100  # ms
        self.schedule_updates()

        # Pencere kapatma event'i
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_menu(self):
        """Menü çubuğu oluştur."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="DBC Yükle...", command=self.load_dbc_file)
        file_menu.add_command(label="Log Dosyası Aç...", command=self.load_log_file)
        file_menu.add_separator()
        file_menu.add_command(label="CSV Export...", command=self.export_to_csv)
        file_menu.add_command(label="Excel Export...", command=self.export_to_excel)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.on_closing)

        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        tools_menu.add_command(label="İstatistikler", command=self.show_statistics)
        tools_menu.add_command(label="Grafik Kaydet...", command=self.save_plot)
        tools_menu.add_command(label="Verileri Temizle", command=self.clear_all_data)

        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self.show_about)

    def setup_main_layout(self):
        """Ana layout oluştur."""
        # Ana container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sol panel (Kontroller)
        left_panel = ttk.Frame(main_container, width=350)
        main_container.add(left_panel, weight=0)

        # Sağ panel (İçerik)
        right_panel = ttk.Frame(main_container)
        main_container.add(right_panel, weight=1)

        # Sol panel içeriği
        self.setup_left_panel(left_panel)

        # Sağ panel içeriği (Notebook)
        self.setup_right_panel(right_panel)

    def setup_left_panel(self, parent):
        """Sol kontrol panelini oluştur."""
        # CAN Bağlantı Grubu
        conn_frame = ttk.LabelFrame(parent, text="CAN Bağlantısı", padding=10)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="Kanal:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.channel_var = tk.IntVar(value=0)
        ttk.Spinbox(conn_frame, from_=0, to=7, textvariable=self.channel_var,
                   width=10).grid(row=0, column=1, pady=2)

        ttk.Label(conn_frame, text="Bitrate:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.bitrate_var = tk.StringVar(value="500000")
        bitrate_combo = ttk.Combobox(conn_frame, textvariable=self.bitrate_var,
                                     values=["125000", "250000", "500000", "1000000"],
                                     width=15)
        bitrate_combo.grid(row=1, column=1, pady=2)

        self.connect_btn = ttk.Button(conn_frame, text="Bağlan",
                                      command=self.toggle_connection)
        self.connect_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)

        self.connection_status = ttk.Label(conn_frame, text="Bağlı Değil",
                                          foreground="red")
        self.connection_status.grid(row=3, column=0, columnspan=2)

        # DBC Grubu
        dbc_frame = ttk.LabelFrame(parent, text="DBC Dosyası", padding=10)
        dbc_frame.pack(fill=tk.X, padx=5, pady=5)

        self.dbc_label = ttk.Label(dbc_frame, text="Yüklü değil", wraplength=280)
        self.dbc_label.pack(fill=tk.X)

        ttk.Button(dbc_frame, text="DBC Yükle",
                  command=self.load_dbc_file).pack(fill=tk.X, pady=2)

        # Kayıt Grubu
        record_frame = ttk.LabelFrame(parent, text="Veri Kaydı", padding=10)
        record_frame.pack(fill=tk.X, padx=5, pady=5)

        self.record_btn = ttk.Button(record_frame, text="Kaydı Başlat",
                                     command=self.toggle_recording)
        self.record_btn.pack(fill=tk.X, pady=2)

        self.record_status = ttk.Label(record_frame, text="Kayıt yapılmıyor")
        self.record_status.pack()

        self.message_count_label = ttk.Label(record_frame, text="Mesaj: 0")
        self.message_count_label.pack()

        # Sinyal Seçimi Grubu
        signal_frame = ttk.LabelFrame(parent, text="Sinyal Seçimi", padding=10)
        signal_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sinyal listesi
        list_frame = ttk.Frame(signal_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.signal_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE,
                                         yscrollcommand=scrollbar.set)
        self.signal_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.signal_listbox.yview)

        ttk.Button(signal_frame, text="Grafik Güncelle",
                  command=self.update_plot).pack(fill=tk.X, pady=2)

    def setup_right_panel(self, parent):
        """Sağ içerik panelini oluştur."""
        # Notebook (Sekmeler)
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 1. Mesaj Monitör Sekmesi
        self.setup_message_monitor_tab()

        # 2. Grafik Sekmesi
        self.setup_plot_tab()

        # 3. Log Analiz Sekmesi
        self.setup_log_analysis_tab()

        # 4. DBC İnceleme Sekmesi
        self.setup_dbc_viewer_tab()

    def setup_message_monitor_tab(self):
        """Mesaj monitör sekmesi."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Mesaj Monitör")

        # Filtre
        filter_frame = ttk.Frame(tab)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(filter_frame, text="CAN ID Filtre:").pack(side=tk.LEFT, padx=5)
        self.filter_entry = ttk.Entry(filter_frame, width=20)
        self.filter_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Uygula",
                  command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Temizle",
                  command=self.clear_filter).pack(side=tk.LEFT)

        # Mesaj tablosu
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview
        columns = ("Timestamp", "CAN ID", "DLC", "Data", "Decoded")
        self.message_tree = ttk.Treeview(table_frame, columns=columns,
                                        show='headings', height=20)

        # Kolonlar
        self.message_tree.heading("Timestamp", text="Zaman")
        self.message_tree.heading("CAN ID", text="CAN ID")
        self.message_tree.heading("DLC", text="DLC")
        self.message_tree.heading("Data", text="Data")
        self.message_tree.heading("Decoded", text="Decode")

        self.message_tree.column("Timestamp", width=150)
        self.message_tree.column("CAN ID", width=100)
        self.message_tree.column("DLC", width=50)
        self.message_tree.column("Data", width=200)
        self.message_tree.column("Decoded", width=300)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.message_tree.yview)
        self.message_tree.configure(yscrollcommand=scrollbar.set)

        self.message_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_plot_tab(self):
        """Grafik sekmesi."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Grafik")

        # Grafik kontrolü
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Grafiği Temizle",
                  command=self.clear_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Grafiği Kaydet",
                  command=self.save_plot).pack(side=tk.LEFT, padx=5)

        # Grafik frame
        self.plot_frame = ttk.Frame(tab)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Başlangıç mesajı
        ttk.Label(self.plot_frame,
                 text="Grafik görmek için sol panelden sinyal seçin ve 'Grafik Güncelle' butonuna basın",
                 font=('Arial', 12)).pack(expand=True)

    def setup_log_analysis_tab(self):
        """Log analiz sekmesi."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Log Analizi")

        # Kontroller
        control_frame = ttk.Frame(tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Log Dosyası Aç",
                  command=self.load_log_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="İstatistikler",
                  command=self.show_log_statistics).pack(side=tk.LEFT, padx=5)

        # Log bilgileri
        self.log_text = scrolledtext.ScrolledText(tab, height=25, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def setup_dbc_viewer_tab(self):
        """DBC inceleme sekmesi."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="DBC Bilgileri")

        # DBC mesaj listesi
        self.dbc_text = scrolledtext.ScrolledText(tab, height=25, width=80)
        self.dbc_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Event Handler Metodları

    def toggle_connection(self):
        """CAN bağlantısını aç/kapat."""
        if not self.can_reader.is_connected:
            # Bağlan
            channel = self.channel_var.get()
            bitrate = int(self.bitrate_var.get())

            self.can_reader.channel = channel
            self.can_reader.bitrate = bitrate

            if self.can_reader.connect():
                self.can_reader.start_reading()
                self.connect_btn.config(text="Bağlantıyı Kes")
                self.connection_status.config(text="Bağlı", foreground="green")
                messagebox.showinfo("Başarılı", "CAN Bus'a bağlanıldı")
            else:
                messagebox.showerror("Hata", "CAN Bus'a bağlanılamadı!\nKvaser cihazının bağlı olduğundan emin olun.")
        else:
            # Bağlantıyı kes
            self.can_reader.disconnect()
            self.connect_btn.config(text="Bağlan")
            self.connection_status.config(text="Bağlı Değil", foreground="red")

    def toggle_recording(self):
        """Kayıt yap/durdur."""
        self.is_recording = not self.is_recording

        if self.is_recording:
            self.recorded_messages = []
            self.record_btn.config(text="Kaydı Durdur")
            self.record_status.config(text="Kayıt yapılıyor...", foreground="red")
        else:
            self.record_btn.config(text="Kaydı Başlat")
            self.record_status.config(text=f"{len(self.recorded_messages)} mesaj kaydedildi",
                                     foreground="green")

    def load_dbc_file(self):
        """DBC dosyası yükle."""
        file_path = filedialog.askopenfilename(
            title="DBC Dosyası Seç",
            filetypes=[("DBC Files", "*.dbc"), ("All Files", "*.*")]
        )

        if file_path:
            if self.dbc_parser.load_dbc(file_path):
                filename = os.path.basename(file_path)
                self.dbc_label.config(text=f"Yüklü: {filename}")
                messagebox.showinfo("Başarılı", f"DBC dosyası yüklendi:\n{filename}")

                # Sinyal listesini güncelle
                self.update_signal_list()

                # DBC bilgilerini göster
                self.display_dbc_info()
            else:
                messagebox.showerror("Hata", "DBC dosyası yüklenemedi!")

    def load_log_file(self):
        """Log dosyası yükle."""
        file_path = filedialog.askopenfilename(
            title="Log Dosyası Seç",
            filetypes=[("ASC Files", "*.asc"), ("BLF Files", "*.blf"),
                      ("All Files", "*.*")]
        )

        if file_path:
            if self.log_reader.load_log_file(file_path):
                messagebox.showinfo("Başarılı",
                                   f"{len(self.log_reader.messages)} mesaj yüklendi")

                # Log bilgilerini göster
                self.display_log_info()
            else:
                messagebox.showerror("Hata", "Log dosyası yüklenemedi!")

    def update_signal_list(self):
        """Sinyal listesini güncelle."""
        self.signal_listbox.delete(0, tk.END)

        if self.dbc_parser.is_loaded:
            # Tüm mesajları al
            messages = self.dbc_parser.get_all_messages()

            # Her mesajın sinyallerini ekle
            for msg in messages:
                can_id = msg['id_decimal']
                signal_names = self.dbc_parser.get_signal_list(can_id)

                for signal_name in signal_names:
                    display_name = f"{msg['name']}.{signal_name}"
                    self.signal_listbox.insert(tk.END, display_name)

    def update_plot(self):
        """Grafiği güncelle."""
        # Seçili sinyalleri al
        selected_indices = self.signal_listbox.curselection()
        self.selected_signals = [self.signal_listbox.get(i) for i in selected_indices]

        if not self.selected_signals:
            messagebox.showwarning("Uyarı", "Lütfen en az bir sinyal seçin")
            return

        # Plotteri temizle
        self.plotter.clear_data()

        # Sinyalleri ekle
        for signal in self.selected_signals:
            self.plotter.add_signal(signal)

        # Grafik canvas'ını oluştur
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        self.plot_canvas = self.plotter.create_embedded_plot(
            self.plot_frame,
            self.selected_signals
        )

        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def clear_plot(self):
        """Grafiği temizle."""
        self.plotter.clear_data()
        if hasattr(self, 'plot_canvas'):
            self.plotter.update_embedded_plot()

    def save_plot(self):
        """Grafiği dosyaya kaydet."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Files", "*.png"), ("PDF Files", "*.pdf"),
                      ("All Files", "*.*")]
        )

        if file_path:
            fig = self.plotter.create_static_plot(
                signals_to_plot=self.selected_signals,
                save_file=file_path
            )
            if fig:
                messagebox.showinfo("Başarılı", f"Grafik kaydedildi:\n{file_path}")

    def export_to_csv(self):
        """CSV export."""
        if not self.recorded_messages:
            messagebox.showwarning("Uyarı", "Kaydedilmiş mesaj yok!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            include_decoded = self.dbc_parser.is_loaded
            if self.data_exporter.export_messages_to_csv(
                self.recorded_messages, file_path, include_decoded):
                messagebox.showinfo("Başarılı", f"CSV dosyası oluşturuldu:\n{file_path}")

    def export_to_excel(self):
        """Excel export."""
        if not self.recorded_messages:
            messagebox.showwarning("Uyarı", "Kaydedilmiş mesaj yok!")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )

        if file_path:
            include_decoded = self.dbc_parser.is_loaded
            if self.data_exporter.export_messages_to_excel(
                self.recorded_messages, file_path, include_decoded):
                messagebox.showinfo("Başarılı", f"Excel dosyası oluşturuldu:\n{file_path}")

    def show_statistics(self):
        """İstatistikleri göster."""
        if not self.recorded_messages:
            messagebox.showinfo("İstatistikler", "Henüz veri yok")
            return

        stats = f"Toplam Mesaj: {len(self.recorded_messages)}\n"

        # CAN ID bazında sayım
        id_counts = {}
        for msg in self.recorded_messages:
            can_id = msg['arbitration_id']
            id_counts[can_id] = id_counts.get(can_id, 0) + 1

        stats += f"Unique CAN ID: {len(id_counts)}\n\n"
        stats += "CAN ID Dağılımı:\n"

        for can_id, count in sorted(id_counts.items()):
            stats += f"  0x{can_id:X}: {count} mesaj\n"

        messagebox.showinfo("İstatistikler", stats)

    def show_log_statistics(self):
        """Log istatistiklerini göster."""
        if not self.log_reader.messages:
            messagebox.showinfo("İstatistikler", "Log dosyası yüklü değil")
            return

        stats = self.log_reader.get_statistics()

        info = f"""Log Dosyası İstatistikleri:

Toplam Mesaj: {stats['total_messages']}
Unique CAN ID: {stats['unique_can_ids']}
Süre: {stats['duration']:.2f} saniye
Mesaj/Saniye: {stats['messages_per_second']:.2f}
Başlangıç: {stats['start_time']}
Bitiş: {stats['end_time']}
"""
        messagebox.showinfo("Log İstatistikleri", info)

    def display_log_info(self):
        """Log bilgilerini göster."""
        self.log_text.delete(1.0, tk.END)

        if not self.log_reader.messages:
            return

        stats = self.log_reader.get_statistics()

        info = f"""Log Dosyası: {stats['file_path']}
Format: {stats['file_format']}
Toplam Mesaj: {stats['total_messages']}
Unique CAN ID: {stats['unique_can_ids']}
Süre: {stats['duration']:.2f} saniye
Mesaj/Saniye: {stats['messages_per_second']:.2f}

CAN ID Listesi:
{', '.join(stats['can_id_list'])}

Mesaj Dağılımı:
"""
        for can_id, count in sorted(stats['id_message_counts'].items()):
            info += f"  {can_id}: {count} mesaj\n"

        self.log_text.insert(1.0, info)

    def display_dbc_info(self):
        """DBC bilgilerini göster."""
        self.dbc_text.delete(1.0, tk.END)

        if not self.dbc_parser.is_loaded:
            return

        db_info = self.dbc_parser.get_database_info()
        messages = self.dbc_parser.get_all_messages()

        info = f"""DBC Dosyası: {db_info['file_path']}
Toplam Mesaj: {db_info['message_count']}
Toplam Sinyal: {db_info['signal_count']}
Node Sayısı: {db_info['node_count']}
Versiyon: {db_info['version']}

Mesajlar:
{'='*80}

"""
        for msg in messages:
            info += f"\n{msg['name']} (ID: {msg['id']})\n"
            info += f"  DLC: {msg['dlc']}, Sinyaller: {msg['signal_count']}\n"

            if msg['comment']:
                info += f"  Açıklama: {msg['comment']}\n"

        self.dbc_text.insert(1.0, info)

    def apply_filter(self):
        """CAN ID filtresi uygula."""
        filter_text = self.filter_entry.get().strip()

        if not filter_text:
            self.can_reader.clear_filters()
            return

        try:
            # Virgülle ayrılmış ID'leri parse et
            can_ids = []
            for id_str in filter_text.split(','):
                id_str = id_str.strip()
                if id_str.startswith('0x') or id_str.startswith('0X'):
                    can_ids.append(int(id_str, 16))
                else:
                    can_ids.append(int(id_str))

            self.can_reader.set_filters(can_ids, enabled=True)
            messagebox.showinfo("Filtre", f"{len(can_ids)} CAN ID filtresi aktif")

        except ValueError:
            messagebox.showerror("Hata", "Geçersiz CAN ID formatı!\nÖrnek: 0x123, 0x456")

    def clear_filter(self):
        """Filtreyi temizle."""
        self.filter_entry.delete(0, tk.END)
        self.can_reader.clear_filters()

    def clear_all_data(self):
        """Tüm verileri temizle."""
        self.recorded_messages = []
        self.plotter.clear_data()
        self.message_tree.delete(*self.message_tree.get_children())
        self.message_count_label.config(text="Mesaj: 0")

    def show_about(self):
        """Hakkında penceresi."""
        about_text = """CAN Bus Analyzer v1.0

Windows için profesyonel CAN Bus veri analiz aracı

Özellikler:
• Kvaser cihaz desteği
• DBC dosya parsing
• Real-time görselleştirme
• Log dosyası analizi (ASC, BLF)
• CSV/Excel export

© 2024 - Tüm hakları saklıdır.
"""
        messagebox.showinfo("Hakkında", about_text)

    def schedule_updates(self):
        """Periyodik GUI güncellemelerini zamanla."""
        self.update_gui()
        self.root.after(self.update_interval, self.schedule_updates)

    def update_gui(self):
        """GUI'yi güncelle."""
        # CAN mesajlarını al
        if self.can_reader.is_reading:
            messages = self.can_reader.get_messages(timeout=0.01)

            for msg in messages:
                # DBC ile decode et
                if self.dbc_parser.is_loaded:
                    decoded = self.dbc_parser.decode_message(
                        msg['arbitration_id'],
                        bytes(msg['data'])
                    )
                    msg['decoded'] = decoded
                else:
                    msg['decoded'] = None

                # Kayıt yap
                if self.is_recording:
                    self.recorded_messages.append(msg)

                # Mesaj tablosuna ekle (son 100 mesaj)
                if len(self.message_tree.get_children()) > 100:
                    self.message_tree.delete(self.message_tree.get_children()[0])

                self.add_message_to_tree(msg)

                # Grafiği güncelle
                if msg['decoded'] and self.selected_signals:
                    timestamp = msg['timestamp']
                    signal_values = {}

                    for signal in self.selected_signals:
                        msg_name = msg['decoded']['message_name']
                        signal_only = signal.split('.')[-1]

                        if signal.startswith(msg_name) and signal_only in msg['decoded']['signals']:
                            signal_values[signal] = msg['decoded']['signals'][signal_only]

                    if signal_values:
                        self.plotter.update_data(timestamp, signal_values)
                        if hasattr(self, 'plot_canvas'):
                            self.plotter.update_embedded_plot()

        # Mesaj sayacını güncelle
        if self.is_recording:
            self.message_count_label.config(text=f"Mesaj: {len(self.recorded_messages)}")

    def add_message_to_tree(self, msg):
        """Mesajı tabloya ekle."""
        timestamp_str = msg['datetime'].strftime('%H:%M:%S.%f')[:-3]
        can_id_str = f"0x{msg['arbitration_id']:X}"
        data_str = ' '.join(f"{b:02X}" for b in msg['data'])

        decoded_str = ""
        if msg['decoded']:
            decoded_str = msg['decoded']['message_name']

        self.message_tree.insert('', 0, values=(
            timestamp_str,
            can_id_str,
            msg['dlc'],
            data_str,
            decoded_str
        ))

    def on_closing(self):
        """Pencere kapatılırken temizlik yap."""
        if self.can_reader.is_connected:
            self.can_reader.disconnect()

        self.root.destroy()


def main():
    """Ana fonksiyon."""
    root = tk.Tk()
    app = CANAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

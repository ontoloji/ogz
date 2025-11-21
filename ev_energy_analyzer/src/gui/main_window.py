"""
Ana GUI Penceresi
Windows 10/11 uyumlu, Türkçe arayüzlü tkinter uygulaması
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import sys
import os

# Parent dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.excel_reader import load_excel_data
from modules.sort_calculator import analyze_sort_cycle
from modules.energy_analyzer import EnergyAnalyzer
from modules.chart_generator import ChartGenerator
from modules.pdf_reporter import create_full_report
from modules.comparison import TestComparison
from utils.config import (GUI_SETTINGS, BATTERY_CAPACITIES, SORT_CYCLES,
                          format_turkish_number)

class EVEnergyAnalyzer(tk.Tk):
    """Ana uygulama penceresi"""

    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.title(GUI_SETTINGS['window_title'])
        self.geometry(GUI_SETTINGS['window_size'])
        self.configure(bg=GUI_SETTINGS['theme_colors']['bg'])

        # Windows ikon (varsa)
        # self.iconbitmap('icon.ico')

        # Veri değişkenleri
        self.current_file = None
        self.current_data = None
        self.current_results = {}
        self.comparison_mode = False
        self.comparison_tests = []

        # GUI oluştur
        self.create_widgets()

        # Pencereyi merkeze al
        self.center_window()

    def center_window(self):
        """Pencereyi ekranın ortasına yerleştirir"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """GUI bileşenlerini oluşturur"""
        # Ana stil
        style = ttk.Style()
        style.theme_use('clam')

        # Stil tanımlamaları
        style.configure('Title.TLabel',
                       font=(GUI_SETTINGS['font_family'],
                             GUI_SETTINGS['font_sizes']['title'], 'bold'),
                       background=GUI_SETTINGS['theme_colors']['bg'])

        style.configure('Heading.TLabel',
                       font=(GUI_SETTINGS['font_family'],
                             GUI_SETTINGS['font_sizes']['heading'], 'bold'),
                       background=GUI_SETTINGS['theme_colors']['bg'])

        style.configure('TButton',
                       font=(GUI_SETTINGS['font_family'],
                             GUI_SETTINGS['font_sizes']['normal']),
                       background=GUI_SETTINGS['theme_colors']['button'])

        # Üst başlık çerçevesi
        header_frame = tk.Frame(self, bg=GUI_SETTINGS['theme_colors']['accent'], height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = tk.Label(
            header_frame,
            text="⚡ Elektrikli Araç Enerji Tüketimi Analiz Sistemi",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['title'], 'bold'),
            bg=GUI_SETTINGS['theme_colors']['accent'],
            fg='white',
            pady=20
        )
        title_label.pack()

        # Ana içerik çerçevesi
        main_frame = tk.Frame(self, bg=GUI_SETTINGS['theme_colors']['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Sol panel - Dosya ve ayarlar
        left_panel = tk.LabelFrame(
            main_frame,
            text=" 📂 Dosya ve Ayarlar ",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['heading'], 'bold'),
            bg=GUI_SETTINGS['theme_colors']['bg'],
            pady=10,
            padx=10
        )
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        # Dosya seçimi
        file_btn = tk.Button(
            left_panel,
            text="📁 Excel Dosyası Seç",
            command=self.load_file,
            bg=GUI_SETTINGS['theme_colors']['button'],
            fg='white',
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        file_btn.pack(fill=tk.X, pady=5)

        self.file_label = tk.Label(
            left_panel,
            text="Dosya seçilmedi",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['small']),
            bg=GUI_SETTINGS['theme_colors']['bg'],
            fg='gray',
            wraplength=250
        )
        self.file_label.pack(pady=5)

        # Ayırıcı
        tk.Frame(left_panel, height=2, bg='lightgray').pack(fill=tk.X, pady=10)

        # SORT döngüsü seçimi
        sort_label = tk.Label(
            left_panel,
            text="SORT Döngüsü:",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            bg=GUI_SETTINGS['theme_colors']['bg']
        )
        sort_label.pack(anchor='w', pady=(5, 2))

        self.sort_var = tk.StringVar(value='auto')
        sort_options = ['auto'] + list(SORT_CYCLES.keys())

        for option in sort_options:
            rb = tk.Radiobutton(
                left_panel,
                text=SORT_CYCLES[option]['name'] if option != 'auto' else 'Otomatik Tespit',
                variable=self.sort_var,
                value=option,
                font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['small']),
                bg=GUI_SETTINGS['theme_colors']['bg'],
                activebackground=GUI_SETTINGS['theme_colors']['bg']
            )
            rb.pack(anchor='w')

        # Ayırıcı
        tk.Frame(left_panel, height=2, bg='lightgray').pack(fill=tk.X, pady=10)

        # Batarya kapasitesi
        battery_label = tk.Label(
            left_panel,
            text="Batarya Kapasitesi (kWh):",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            bg=GUI_SETTINGS['theme_colors']['bg']
        )
        battery_label.pack(anchor='w', pady=(5, 2))

        self.battery_var = tk.IntVar(value=100)
        battery_combo = ttk.Combobox(
            left_panel,
            textvariable=self.battery_var,
            values=BATTERY_CAPACITIES,
            state='readonly',
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal']),
            width=15
        )
        battery_combo.pack(fill=tk.X, pady=5)

        # Başlangıç SOC
        soc_label = tk.Label(
            left_panel,
            text="Başlangıç SOC (%):",
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            bg=GUI_SETTINGS['theme_colors']['bg']
        )
        soc_label.pack(anchor='w', pady=(10, 2))

        self.soc_var = tk.IntVar(value=100)
        soc_spinbox = tk.Spinbox(
            left_panel,
            from_=0,
            to=100,
            textvariable=self.soc_var,
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal']),
            width=15
        )
        soc_spinbox.pack(fill=tk.X, pady=5)

        # Analiz butonu
        analyze_btn = tk.Button(
            left_panel,
            text="🔍 Analiz Başlat",
            command=self.start_analysis,
            bg='#06A77D',
            fg='white',
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        analyze_btn.pack(fill=tk.X, pady=(15, 5))

        # PDF oluştur butonu
        pdf_btn = tk.Button(
            left_panel,
            text="📄 PDF Rapor Oluştur",
            command=self.generate_pdf,
            bg='#C73E1D',
            fg='white',
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        pdf_btn.pack(fill=tk.X, pady=5)

        # Karşılaştırma butonu
        compare_btn = tk.Button(
            left_panel,
            text="📊 Karşılaştırma Modu",
            command=self.toggle_comparison_mode,
            bg='#A23B72',
            fg='white',
            font=(GUI_SETTINGS['font_family'], GUI_SETTINGS['font_sizes']['normal'], 'bold'),
            cursor='hand2',
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        compare_btn.pack(fill=tk.X, pady=5)

        # Sağ panel - Sonuçlar
        right_panel = tk.Frame(main_frame, bg=GUI_SETTINGS['theme_colors']['bg'])
        right_panel.grid(row=0, column=1, sticky='nsew')

        # Notebook (sekmeler)
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Sonuç sekmeleri
        self.result_tab = self.create_result_tab()
        self.notebook.add(self.result_tab, text='📊 Sonuçlar')

        self.log_tab = self.create_log_tab()
        self.notebook.add(self.log_tab, text='📝 İşlem Günlüğü')

        # Grid ağırlıkları
        main_frame.columnconfigure(0, weight=1, minsize=300)
        main_frame.columnconfigure(1, weight=3)
        main_frame.rowconfigure(0, weight=1)

        # İlk mesaj
        self.log_message("Uygulama başlatıldı. Excel dosyası seçerek başlayabilirsiniz.")

    def create_result_tab(self):
        """Sonuç sekmesini oluşturur"""
        tab = tk.Frame(self.notebook, bg='white')

        # Sonuç metin alanı
        self.result_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='white',
            fg='black'
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        return tab

    def create_log_tab(self):
        """Log sekmesini oluşturur"""
        tab = tk.Frame(self.notebook, bg='white')

        # Log metin alanı
        self.log_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1E1E1E',
            fg='#D4D4D4'
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        return tab

    def log_message(self, message, level='INFO'):
        """Log mesajı ekler"""
        import datetime
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level}: {message}\n"

        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.update_idletasks()

    def load_file(self):
        """Excel dosyası yükler"""
        filename = filedialog.askopenfilename(
            title="Excel Dosyası Seç",
            filetypes=[
                ("Excel Dosyaları", "*.xlsx *.xls"),
                ("Tüm Dosyalar", "*.*")
            ]
        )

        if filename:
            self.current_file = filename
            self.file_label.config(text=Path(filename).name, fg='green')
            self.log_message(f"Dosya seçildi: {Path(filename).name}")

    def start_analysis(self):
        """Analiz işlemini başlatır"""
        if not self.current_file:
            messagebox.showwarning("Uyarı", "Lütfen önce bir Excel dosyası seçin!")
            return

        # Arka planda analiz yap
        thread = threading.Thread(target=self.run_analysis, daemon=True)
        thread.start()

    def run_analysis(self):
        """Analiz işlemini çalıştırır"""
        try:
            self.log_message("Analiz başlatılıyor...")
            self.result_text.delete(1.0, tk.END)

            # Excel verilerini yükle
            self.log_message("Excel dosyası okunuyor...")
            df, metadata, test_info, warnings = load_excel_data(self.current_file)

            self.log_message(f"✓ {len(df)} satır veri yüklendi")

            if warnings:
                for warning in warnings:
                    self.log_message(f"⚠ {warning}", 'WARNING')

            # SORT analizi
            self.log_message("SORT döngüsü analizi yapılıyor...")
            sort_results, sort_calc = analyze_sort_cycle(df, self.sort_var.get())
            self.log_message("✓ SORT analizi tamamlandı")

            # Enerji analizi
            self.log_message("Enerji analizi yapılıyor...")
            energy_analyzer = EnergyAnalyzer(df)
            energy_results = energy_analyzer.full_analysis()
            self.log_message("✓ Enerji analizi tamamlandı")

            # Grafikleri oluştur
            self.log_message("Grafikler oluşturuluyor...")
            chart_gen = ChartGenerator(df, title_prefix="")
            chart_paths = chart_gen.create_all_charts(
                energy_results,
                self.battery_var.get(),
                self.soc_var.get()
            )
            self.log_message(f"✓ {len(chart_paths)} grafik oluşturuldu")

            # Sonuçları kaydet
            self.current_data = df
            self.current_results = {
                'test_info': test_info,
                'sort_results': sort_results,
                'energy_results': energy_results,
                'chart_paths': chart_paths
            }

            # Sonuçları göster
            self.display_results()

            self.log_message("✅ Analiz başarıyla tamamlandı!", 'SUCCESS')

            # Karşılaştırma modunda ise test ekle
            if self.comparison_mode:
                self.add_to_comparison()

        except Exception as e:
            self.log_message(f"❌ Hata: {str(e)}", 'ERROR')
            messagebox.showerror("Hata", f"Analiz sırasında hata oluştu:\n{str(e)}")

    def display_results(self):
        """Sonuçları gösterir"""
        if not self.current_results:
            return

        output = ""

        # Test bilgileri
        output += "=" * 70 + "\n"
        output += "TEST BİLGİLERİ\n"
        output += "=" * 70 + "\n\n"

        for key, value in self.current_results['test_info'].items():
            output += f"{key:25s}: {value}\n"

        # SORT sonuçları
        output += "\n" + "=" * 70 + "\n"
        output += "UITP SORT TEST DÖNGÜSÜ ANALİZİ\n"
        output += "=" * 70 + "\n\n"

        sort_res = self.current_results['sort_results']
        output += f"Döngü Tipi               : {sort_res['cycle_name']}\n"
        output += f"Enerji Tüketimi          : {format_turkish_number(sort_res['energy_per_100km'], 2)} kWh/100km\n"
        output += f"Maksimum Hız             : {format_turkish_number(sort_res['max_speed'], 1)} km/h\n"
        output += f"Ortalama Hız             : {format_turkish_number(sort_res['avg_speed'], 1)} km/h\n"
        output += f"Maksimum Güç             : {format_turkish_number(sort_res['max_power'], 1)} kW\n"
        output += f"Ortalama Güç             : {format_turkish_number(sort_res['avg_power'], 1)} kW\n"

        # Enerji analizi
        output += "\n" + "=" * 70 + "\n"
        output += "ENERJİ ANALİZİ\n"
        output += "=" * 70 + "\n\n"

        energy_res = self.current_results['energy_results']
        cons = energy_res['consumption']

        output += f"Toplam Enerji            : {format_turkish_number(cons['total_energy'], 3)} kWh\n"
        output += f"Toplam Mesafe            : {format_turkish_number(cons['total_distance'], 2)} km\n"
        output += f"Tüketim (100km)          : {format_turkish_number(cons['consumption_per_100km'], 2)} kWh/100km\n"

        # Regeneratif frenleme
        if energy_res['regenerative_braking'].get('available'):
            output += "\nREGENERATİF FRENLEME:\n"
            regen = energy_res['regenerative_braking']
            output += f"  Geri Kazanılan Enerji  : {format_turkish_number(regen['total_regen_energy'], 3)} kWh\n"
            output += f"  Regen Verimliliği      : %{format_turkish_number(regen['regen_efficiency'], 1)}\n"

        # Verimlilik
        output += "\nVERİMLİLİK:\n"
        eff = energy_res['efficiency']
        output += f"  Verimlilik Skoru       : {format_turkish_number(eff['efficiency_score'], 1)}/100\n"

        # Menzil tahminleri (örnek)
        output += "\n" + "=" * 70 + "\n"
        output += "MENZİL TAHMİNLERİ (Seçili Batarya)\n"
        output += "=" * 70 + "\n\n"

        battery_cap = self.battery_var.get()
        if battery_cap in energy_res['range']:
            range_data = energy_res['range'][battery_cap]
            output += f"{battery_cap} kWh Batarya:\n"
            output += f"  Teorik Menzil          : {format_turkish_number(range_data['theoretical'], 1)} km\n"
            output += f"  Gerçekçi Menzil        : {format_turkish_number(range_data['realistic'], 1)} km\n"
            output += f"  Minimum Menzil         : {format_turkish_number(range_data['minimum'], 1)} km\n"

        self.result_text.insert(1.0, output)
        self.notebook.select(self.result_tab)

    def generate_pdf(self):
        """PDF rapor oluşturur"""
        if not self.current_results:
            messagebox.showwarning("Uyarı", "Önce analiz yapmalısınız!")
            return

        try:
            self.log_message("PDF rapor oluşturuluyor...")

            pdf_path = create_full_report(
                self.current_results['test_info'],
                self.current_results['sort_results'],
                self.current_results['energy_results'],
                self.current_results['chart_paths']
            )

            if pdf_path:
                self.log_message(f"✅ PDF rapor oluşturuldu: {Path(pdf_path).name}", 'SUCCESS')
                messagebox.showinfo("Başarılı", f"PDF rapor oluşturuldu:\n{pdf_path}")

                # PDF'yi aç
                import subprocess
                if os.name == 'nt':  # Windows
                    os.startfile(pdf_path)
            else:
                raise Exception("PDF oluşturulamadı")

        except Exception as e:
            self.log_message(f"❌ PDF oluşturma hatası: {str(e)}", 'ERROR')
            messagebox.showerror("Hata", f"PDF oluşturulamadı:\n{str(e)}")

    def toggle_comparison_mode(self):
        """Karşılaştırma modunu açar/kapatır"""
        self.comparison_mode = not self.comparison_mode

        if self.comparison_mode:
            self.log_message("📊 Karşılaştırma modu AÇIK", 'INFO')
            messagebox.showinfo(
                "Karşılaştırma Modu",
                "Karşılaştırma modu etkinleştirildi.\n\n"
                "Birden fazla test dosyası yükleyip analiz edin.\n"
                "Sonra 'Karşılaştırma Raporu Oluştur' butonuna tıklayın."
            )
        else:
            self.log_message("📊 Karşılaştırma modu KAPALI", 'INFO')
            self.comparison_tests = []

    def add_to_comparison(self):
        """Mevcut testi karşılaştırmaya ekler"""
        if not self.current_data or not self.current_results:
            return

        test_name = Path(self.current_file).stem

        self.comparison_tests.append({
            'name': test_name,
            'dataframe': self.current_data,
            'sort_results': self.current_results['sort_results'],
            'energy_results': self.current_results['energy_results']
        })

        self.log_message(f"Test karşılaştırmaya eklendi: {test_name} ({len(self.comparison_tests)} test)")


def main():
    """Uygulamayı başlatır"""
    app = EVEnergyAnalyzer()
    app.mainloop()


if __name__ == "__main__":
    main()

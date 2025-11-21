"""
Batarya Test Maliyeti Hesaplama GUI Uygulaması

Profesyonel bir tkinter tabanlı GUI uygulaması
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
from datetime import datetime
from typing import Dict, List
import os

from cost_calculator import BatteryTestCostCalculator, CostBreakdown


class BatteryTestCostGUI:
    """Ana GUI sınıfı"""

    def __init__(self, root):
        """GUI'yi başlat"""
        self.root = root
        self.root.title("Batarya Test Maliyeti Hesaplama Aracı")
        self.root.geometry("1400x900")

        # Hesaplayıcı
        self.calculator = BatteryTestCostCalculator()

        # Tema renkleri
        self.colors = {
            'bg': '#f0f0f0',
            'fg': '#333333',
            'primary': '#2196F3',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'danger': '#F44336',
            'info': '#00BCD4'
        }

        # Stil ayarları
        self.setup_styles()

        # Ana frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Başlık
        title_label = ttk.Label(
            main_frame,
            text="🔋 Batarya Test Maliyeti Hesaplama Aracı",
            font=('Helvetica', 20, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Sekme yapısı
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Sekmeleri oluştur
        self.create_single_calculation_tab()
        self.create_comparison_tab()
        self.create_scenario_tab()
        self.create_timeline_tab()
        self.create_export_tab()

        # Grid ağırlıkları
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Son hesaplama sonuçları
        self.last_calculation = None

    def setup_styles(self):
        """Stil ayarlarını yap"""
        style = ttk.Style()
        style.theme_use('clam')

        # Label stili
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))

        # Button stili
        style.configure('Primary.TButton', font=('Helvetica', 10, 'bold'))

    def create_single_calculation_tab(self):
        """Tekli hesaplama sekmesi"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Maliyet Hesaplama")

        # Sol panel - Girdi parametreleri
        left_frame = ttk.LabelFrame(tab, text="Parametreler", padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Test tipi
        ttk.Label(left_frame, text="Test Tipi:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.test_type_var = tk.StringVar()
        test_types = list(self.calculator.TEST_PROFILES.keys())
        test_type_combo = ttk.Combobox(
            left_frame,
            textvariable=self.test_type_var,
            values=test_types,
            state='readonly'
        )
        test_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        test_type_combo.current(0)
        test_type_combo.bind('<<ComboboxSelected>>', self.on_test_type_changed)

        # Test açıklaması
        self.test_desc_label = ttk.Label(left_frame, text="", foreground='gray', wraplength=300)
        self.test_desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)
        self.update_test_description()

        # Bölge
        ttk.Label(left_frame, text="Bölge:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.region_var = tk.StringVar()
        regions = [data.region for data in self.calculator.REGIONAL_DATA.values()]
        region_combo = ttk.Combobox(
            left_frame,
            textvariable=self.region_var,
            values=regions,
            state='readonly'
        )
        region_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        region_combo.current(0)

        # Para birimi
        ttk.Label(left_frame, text="Para Birimi:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.currency_var = tk.StringVar(value='USD')
        currency_combo = ttk.Combobox(
            left_frame,
            textvariable=self.currency_var,
            values=list(self.calculator.CURRENCY_RATES.keys()),
            state='readonly'
        )
        currency_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Test süresi
        ttk.Label(left_frame, text="Test Süresi (saat):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar()
        duration_entry = ttk.Entry(left_frame, textvariable=self.duration_var)
        duration_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Güç tüketimi
        ttk.Label(left_frame, text="Güç Tüketimi (kW):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.power_var = tk.StringVar()
        power_entry = ttk.Entry(left_frame, textvariable=self.power_var)
        power_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Personel sayısı
        ttk.Label(left_frame, text="Personel Sayısı:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.personnel_var = tk.StringVar()
        personnel_entry = ttk.Entry(left_frame, textvariable=self.personnel_var)
        personnel_entry.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Batarya sayısı
        ttk.Label(left_frame, text="Batarya Sayısı:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.battery_count_var = tk.StringVar(value='1')
        battery_entry = ttk.Entry(left_frame, textvariable=self.battery_count_var)
        battery_entry.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Ekipman maliyeti
        ttk.Label(left_frame, text="Ekipman Maliyeti (USD):").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.equipment_var = tk.StringVar()
        equipment_entry = ttk.Entry(left_frame, textvariable=self.equipment_var)
        equipment_entry.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Dış kaynak
        self.outsource_var = tk.BooleanVar(value=False)
        outsource_check = ttk.Checkbutton(
            left_frame,
            text="Dış Kaynak Kullan",
            variable=self.outsource_var
        )
        outsource_check.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=10)

        # Hesapla butonu
        calc_button = ttk.Button(
            left_frame,
            text="Hesapla",
            command=self.calculate_single,
            style='Primary.TButton'
        )
        calc_button.grid(row=10, column=0, columnspan=2, pady=10)

        # Varsayılana dön butonu
        reset_button = ttk.Button(
            left_frame,
            text="Varsayılana Dön",
            command=self.reset_to_defaults
        )
        reset_button.grid(row=11, column=0, columnspan=2, pady=5)

        # Sağ panel - Sonuçlar
        right_frame = ttk.LabelFrame(tab, text="Maliyet Analizi", padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Sonuç alanı
        self.result_text = tk.Text(right_frame, height=30, width=60, font=('Courier', 10))
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text['yscrollcommand'] = scrollbar.set

        # Grid weights
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)

    def create_comparison_tab(self):
        """Bölgesel karşılaştırma sekmesi"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Bölge Karşılaştırma")

        # Üst panel - Parametreler
        top_frame = ttk.LabelFrame(tab, text="Karşılaştırma Parametreleri", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Test tipi
        ttk.Label(top_frame, text="Test Tipi:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.comp_test_type_var = tk.StringVar()
        test_types = list(self.calculator.TEST_PROFILES.keys())
        comp_test_combo = ttk.Combobox(
            top_frame,
            textvariable=self.comp_test_type_var,
            values=test_types,
            state='readonly'
        )
        comp_test_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        comp_test_combo.current(0)

        # Para birimi
        ttk.Label(top_frame, text="Para Birimi:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.comp_currency_var = tk.StringVar(value='USD')
        comp_currency_combo = ttk.Combobox(
            top_frame,
            textvariable=self.comp_currency_var,
            values=list(self.calculator.CURRENCY_RATES.keys()),
            state='readonly'
        )
        comp_currency_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Batarya sayısı
        ttk.Label(top_frame, text="Batarya Sayısı:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=5)
        self.comp_battery_var = tk.StringVar(value='1')
        comp_battery_entry = ttk.Entry(top_frame, textvariable=self.comp_battery_var, width=10)
        comp_battery_entry.grid(row=0, column=5, sticky=tk.W, pady=5, padx=5)

        # Karşılaştır butonu
        compare_button = ttk.Button(
            top_frame,
            text="Karşılaştır",
            command=self.compare_regions,
            style='Primary.TButton'
        )
        compare_button.grid(row=0, column=6, pady=5, padx=10)

        # Alt panel - Sonuçlar ve grafik
        bottom_frame = ttk.Frame(tab)
        bottom_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Sol - Tablo
        table_frame = ttk.LabelFrame(bottom_frame, text="Karşılaştırma Tablosu", padding="10")
        table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Treeview
        columns = ('Bölge', 'Toplam Maliyet', 'Birim Maliyet', 'İşçilik', 'Enerji')
        self.comparison_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.comparison_tree.heading(col, text=col)
            self.comparison_tree.column(col, width=150)

        self.comparison_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.comparison_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.comparison_tree['yscrollcommand'] = tree_scroll.set

        # Sağ - Grafik
        graph_frame = ttk.LabelFrame(bottom_frame, text="Grafik Gösterim", padding="10")
        graph_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        # Matplotlib figure
        self.comp_figure = Figure(figsize=(7, 6), dpi=100)
        self.comp_canvas = FigureCanvasTkAgg(self.comp_figure, graph_frame)
        self.comp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Grid weights
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=2)
        bottom_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

    def create_scenario_tab(self):
        """Senaryo karşılaştırma sekmesi"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Senaryo Karşılaştırma")

        # Üst panel
        top_frame = ttk.LabelFrame(tab, text="Senaryo Parametreleri", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Parametreler
        ttk.Label(top_frame, text="Test Tipi:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.scen_test_type_var = tk.StringVar()
        scen_test_combo = ttk.Combobox(
            top_frame,
            textvariable=self.scen_test_type_var,
            values=list(self.calculator.TEST_PROFILES.keys()),
            state='readonly'
        )
        scen_test_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        scen_test_combo.current(0)

        ttk.Label(top_frame, text="Bölge:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.scen_region_var = tk.StringVar()
        scen_region_combo = ttk.Combobox(
            top_frame,
            textvariable=self.scen_region_var,
            values=[data.region for data in self.calculator.REGIONAL_DATA.values()],
            state='readonly'
        )
        scen_region_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        scen_region_combo.current(0)

        ttk.Label(top_frame, text="Para Birimi:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=5)
        self.scen_currency_var = tk.StringVar(value='USD')
        scen_currency_combo = ttk.Combobox(
            top_frame,
            textvariable=self.scen_currency_var,
            values=list(self.calculator.CURRENCY_RATES.keys()),
            state='readonly'
        )
        scen_currency_combo.grid(row=0, column=5, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Karşılaştır butonu
        scenario_button = ttk.Button(
            top_frame,
            text="Karşılaştır",
            command=self.compare_scenarios,
            style='Primary.TButton'
        )
        scenario_button.grid(row=0, column=6, pady=5, padx=10)

        # Sonuç alanı
        result_frame = ttk.LabelFrame(tab, text="Karşılaştırma Sonuçları", padding="10")
        result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Sol - Metin sonuçlar
        left_result = ttk.Frame(result_frame)
        left_result.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        self.scenario_text = tk.Text(left_result, height=25, width=50, font=('Courier', 10))
        self.scenario_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scen_scroll = ttk.Scrollbar(left_result, orient=tk.VERTICAL, command=self.scenario_text.yview)
        scen_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scenario_text['yscrollcommand'] = scen_scroll.set

        # Sağ - Grafik
        right_result = ttk.Frame(result_frame)
        right_result.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)

        self.scen_figure = Figure(figsize=(7, 6), dpi=100)
        self.scen_canvas = FigureCanvasTkAgg(self.scen_figure, right_result)
        self.scen_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Grid weights
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        result_frame.columnconfigure(1, weight=1)
        result_frame.rowconfigure(0, weight=1)
        left_result.columnconfigure(0, weight=1)
        left_result.rowconfigure(0, weight=1)

    def create_timeline_tab(self):
        """Zaman-maliyet grafiği sekmesi"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Zaman-Maliyet Grafiği")

        # Üst panel
        top_frame = ttk.LabelFrame(tab, text="Grafik Parametreleri", padding="10")
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Parametreler
        ttk.Label(top_frame, text="Test Tipi:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=5)
        self.time_test_type_var = tk.StringVar()
        time_test_combo = ttk.Combobox(
            top_frame,
            textvariable=self.time_test_type_var,
            values=list(self.calculator.TEST_PROFILES.keys()),
            state='readonly'
        )
        time_test_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        time_test_combo.current(0)

        ttk.Label(top_frame, text="Bölge:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=5)
        self.time_region_var = tk.StringVar()
        time_region_combo = ttk.Combobox(
            top_frame,
            textvariable=self.time_region_var,
            values=[data.region for data in self.calculator.REGIONAL_DATA.values()],
            state='readonly'
        )
        time_region_combo.grid(row=0, column=3, sticky=(tk.W, tk.E), pady=5, padx=5)
        time_region_combo.current(0)

        ttk.Label(top_frame, text="Para Birimi:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=5)
        self.time_currency_var = tk.StringVar(value='USD')
        time_currency_combo = ttk.Combobox(
            top_frame,
            textvariable=self.time_currency_var,
            values=list(self.calculator.CURRENCY_RATES.keys()),
            state='readonly'
        )
        time_currency_combo.grid(row=0, column=5, sticky=(tk.W, tk.E), pady=5, padx=5)

        # Grafik oluştur butonu
        timeline_button = ttk.Button(
            top_frame,
            text="Grafik Oluştur",
            command=self.create_timeline_graph,
            style='Primary.TButton'
        )
        timeline_button.grid(row=0, column=6, pady=5, padx=10)

        # Grafik alanı
        graph_frame = ttk.LabelFrame(tab, text="Zaman-Maliyet İlişkisi", padding="10")
        graph_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        self.timeline_figure = Figure(figsize=(12, 7), dpi=100)
        self.timeline_canvas = FigureCanvasTkAgg(self.timeline_figure, graph_frame)
        self.timeline_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Grid weights
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(1, weight=1)

    def create_export_tab(self):
        """Export ve raporlama sekmesi"""
        tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(tab, text="Export & Rapor")

        # Bilgi
        info_frame = ttk.LabelFrame(tab, text="Export Seçenekleri", padding="20")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=5, pady=5)

        info_text = """
        Bu sekmeden hesaplamalarınızı farklı formatlarda dışa aktarabilirsiniz.

        • Excel: Detaylı hesaplama tabloları ve grafikler
        • JSON: Ham veri formatında export
        • PDF: Profesyonel rapor formatı (yakında)

        Önce bir hesaplama yapın, sonra istediğiniz formatta dışa aktarın.
        """

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        # Export butonları
        button_frame = ttk.Frame(tab)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=5, pady=20)

        ttk.Button(
            button_frame,
            text="📊 Excel'e Aktar",
            command=self.export_to_excel,
            style='Primary.TButton'
        ).pack(pady=10)

        ttk.Button(
            button_frame,
            text="📄 JSON'a Aktar",
            command=self.export_to_json
        ).pack(pady=10)

        ttk.Button(
            button_frame,
            text="📑 PDF Rapor (Yakında)",
            command=self.export_to_pdf,
            state='disabled'
        ).pack(pady=10)

        # Son export bilgisi
        self.export_info_label = ttk.Label(
            tab,
            text="Henüz export yapılmadı",
            foreground='gray'
        )
        self.export_info_label.grid(row=2, column=0, pady=10)

    def on_test_type_changed(self, event=None):
        """Test tipi değiştiğinde açıklamayı güncelle"""
        self.update_test_description()

    def update_test_description(self):
        """Test açıklamasını güncelle"""
        test_type = self.test_type_var.get()
        if test_type and test_type in self.calculator.TEST_PROFILES:
            profile = self.calculator.TEST_PROFILES[test_type]
            desc = profile.description
            self.test_desc_label.config(text=f"ℹ️ {desc}")

    def get_region_key(self, region_name: str) -> str:
        """Bölge adından key'i bul"""
        for key, data in self.calculator.REGIONAL_DATA.items():
            if data.region == region_name:
                return key
        return 'turkey'

    def reset_to_defaults(self):
        """Varsayılan değerlere dön"""
        test_type = self.test_type_var.get()
        if test_type and test_type in self.calculator.TEST_PROFILES:
            profile = self.calculator.TEST_PROFILES[test_type]
            self.duration_var.set(str(profile.typical_duration_hours))
            self.power_var.set(str(profile.power_consumption_kw))
            self.personnel_var.set(str(profile.required_personnel))
            self.equipment_var.set(str(profile.equipment_cost))
        else:
            self.duration_var.set('')
            self.power_var.set('')
            self.personnel_var.set('')
            self.equipment_var.set('')

    def calculate_single(self):
        """Tekli hesaplama yap"""
        try:
            # Parametreleri al
            test_type = self.test_type_var.get()
            region_name = self.region_var.get()
            region = self.get_region_key(region_name)
            currency = self.currency_var.get()

            duration = float(self.duration_var.get()) if self.duration_var.get() else None
            power = float(self.power_var.get()) if self.power_var.get() else None
            personnel = int(self.personnel_var.get()) if self.personnel_var.get() else None
            battery_count = int(self.battery_count_var.get())
            equipment = float(self.equipment_var.get()) if self.equipment_var.get() else None
            is_outsource = self.outsource_var.get()

            # Hesapla
            breakdown = self.calculator.calculate_cost(
                test_type=test_type,
                region=region,
                test_duration_hours=duration,
                power_consumption_kw=power,
                personnel_count=personnel,
                battery_count=battery_count,
                is_outsource=is_outsource,
                target_currency=currency,
                custom_equipment_cost=equipment
            )

            # Sonuçları göster
            self.display_single_result(breakdown, test_type, region_name, is_outsource)

            # Son hesaplamayı sakla
            self.last_calculation = {
                'type': 'single',
                'breakdown': breakdown,
                'test_type': test_type,
                'region': region_name,
                'battery_count': battery_count
            }

        except Exception as e:
            messagebox.showerror("Hata", f"Hesaplama hatası: {str(e)}")

    def display_single_result(self, breakdown: CostBreakdown, test_type: str, region: str, is_outsource: bool):
        """Tekli hesaplama sonucunu göster"""
        self.result_text.delete('1.0', tk.END)

        profile = self.calculator.TEST_PROFILES[test_type]

        output = "=" * 70 + "\n"
        output += "BATARYA TEST MALİYETİ HESAPLAMA RAPORU\n"
        output += "=" * 70 + "\n\n"

        output += f"Test Tipi      : {profile.test_type}\n"
        output += f"Bölge          : {region}\n"
        output += f"Senaryo        : {'Dış Kaynak' if is_outsource else 'Kendi Test'}\n"
        output += f"Para Birimi    : {breakdown.currency}\n"
        output += f"Tarih          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        output += "\n" + "-" * 70 + "\n"
        output += "MALİYET DAĞILIMI\n"
        output += "-" * 70 + "\n\n"

        costs = [
            ("İşçilik Maliyeti", breakdown.labor_cost),
            ("Enerji Maliyeti", breakdown.energy_cost),
            ("Ekipman Amortismanı", breakdown.equipment_depreciation),
            ("Bakım Maliyeti", breakdown.maintenance_cost),
            ("Tesis Maliyeti", breakdown.facility_cost),
            ("Kalibrasyon Maliyeti", breakdown.calibration_cost),
            ("Sarf Malzemeleri", breakdown.consumables_cost)
        ]

        for label, cost in costs:
            if cost > 0:
                percentage = (cost / breakdown.total_cost * 100) if breakdown.total_cost > 0 else 0
                output += f"{label:25s}: {cost:12,.2f} {breakdown.currency} ({percentage:5.1f}%)\n"

        output += "\n" + "=" * 70 + "\n"
        output += f"{'TOPLAM MALİYET':25s}: {breakdown.total_cost:12,.2f} {breakdown.currency}\n"
        output += f"{'BİRİM BAŞINA MALİYET':25s}: {breakdown.cost_per_unit:12,.2f} {breakdown.currency}\n"
        output += "=" * 70 + "\n"

        self.result_text.insert('1.0', output)

    def compare_regions(self):
        """Bölgeleri karşılaştır"""
        try:
            test_type = self.comp_test_type_var.get()
            currency = self.comp_currency_var.get()
            battery_count = int(self.comp_battery_var.get())

            # Karşılaştırma yap
            results = self.calculator.compare_regions(
                test_type=test_type,
                battery_count=battery_count,
                target_currency=currency
            )

            # Tabloyu temizle
            for item in self.comparison_tree.get_children():
                self.comparison_tree.delete(item)

            # Sonuçları tabloya ekle
            for region_key, breakdown in results.items():
                region_name = self.calculator.REGIONAL_DATA[region_key].region
                self.comparison_tree.insert('', 'end', values=(
                    region_name,
                    f"{breakdown.total_cost:,.2f}",
                    f"{breakdown.cost_per_unit:,.2f}",
                    f"{breakdown.labor_cost:,.2f}",
                    f"{breakdown.energy_cost:,.2f}"
                ))

            # Grafik çiz
            self.plot_comparison_graph(results, currency)

            # Son hesaplamayı sakla
            self.last_calculation = {
                'type': 'comparison',
                'results': results,
                'test_type': test_type,
                'currency': currency
            }

        except Exception as e:
            messagebox.showerror("Hata", f"Karşılaştırma hatası: {str(e)}")

    def plot_comparison_graph(self, results: Dict, currency: str):
        """Karşılaştırma grafiği çiz"""
        self.comp_figure.clear()

        # Veri hazırla
        regions = [self.calculator.REGIONAL_DATA[key].region for key in results.keys()]
        total_costs = [breakdown.total_cost for breakdown in results.values()]
        labor_costs = [breakdown.labor_cost for breakdown in results.values()]
        energy_costs = [breakdown.energy_cost for breakdown in results.values()]
        equipment_costs = [breakdown.equipment_depreciation for breakdown in results.values()]

        # İki grafik: toplam maliyet ve dağılım
        ax1 = self.comp_figure.add_subplot(2, 1, 1)
        ax1.bar(regions, total_costs, color='#2196F3', alpha=0.7)
        ax1.set_ylabel(f'Toplam Maliyet ({currency})')
        ax1.set_title('Bölgesel Toplam Maliyet Karşılaştırması')
        ax1.grid(True, alpha=0.3)

        # Değerleri göster
        for i, v in enumerate(total_costs):
            ax1.text(i, v, f'{v:,.0f}', ha='center', va='bottom')

        # Yığılmış bar grafiği
        ax2 = self.comp_figure.add_subplot(2, 1, 2)
        width = 0.6
        x = range(len(regions))

        p1 = ax2.bar(x, labor_costs, width, label='İşçilik', color='#4CAF50')
        p2 = ax2.bar(x, energy_costs, width, bottom=labor_costs, label='Enerji', color='#FF9800')

        bottom = [l + e for l, e in zip(labor_costs, energy_costs)]
        p3 = ax2.bar(x, equipment_costs, width, bottom=bottom, label='Ekipman', color='#F44336')

        ax2.set_ylabel(f'Maliyet ({currency})')
        ax2.set_title('Maliyet Bileşenleri Dağılımı')
        ax2.set_xticks(x)
        ax2.set_xticklabels(regions)
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        self.comp_figure.tight_layout()
        self.comp_canvas.draw()

    def compare_scenarios(self):
        """Senaryoları karşılaştır"""
        try:
            test_type = self.scen_test_type_var.get()
            region_name = self.scen_region_var.get()
            region = self.get_region_key(region_name)
            currency = self.scen_currency_var.get()

            # Karşılaştırma yap
            results = self.calculator.compare_scenarios(
                test_type=test_type,
                region=region,
                battery_count=1,
                target_currency=currency
            )

            # Metni göster
            self.scenario_text.delete('1.0', tk.END)

            output = "=" * 70 + "\n"
            output += "SENARYO KARŞILAŞTIRMASI: KENDİ TEST vs DIŞ KAYNAK\n"
            output += "=" * 70 + "\n\n"

            for scenario_name, breakdown in results.items():
                scenario_label = "KENDİ TEST" if scenario_name == "in_house" else "DIŞ KAYNAK"
                output += f"{scenario_label}\n"
                output += "-" * 70 + "\n"
                output += f"Toplam Maliyet        : {breakdown.total_cost:12,.2f} {currency}\n"
                output += f"İşçilik               : {breakdown.labor_cost:12,.2f} {currency}\n"
                output += f"Enerji                : {breakdown.energy_cost:12,.2f} {currency}\n"
                output += f"Ekipman Amortismanı   : {breakdown.equipment_depreciation:12,.2f} {currency}\n"
                output += f"Bakım                 : {breakdown.maintenance_cost:12,.2f} {currency}\n"
                output += f"Tesis                 : {breakdown.facility_cost:12,.2f} {currency}\n"
                output += f"Kalibrasyon           : {breakdown.calibration_cost:12,.2f} {currency}\n"
                output += f"Sarf Malzemeleri      : {breakdown.consumables_cost:12,.2f} {currency}\n"
                output += "\n"

            # Fark hesapla
            diff = results['in_house'].total_cost - results['outsource'].total_cost
            diff_pct = (diff / results['outsource'].total_cost * 100) if results['outsource'].total_cost > 0 else 0

            output += "=" * 70 + "\n"
            output += "SONUÇ\n"
            output += "=" * 70 + "\n"
            output += f"Maliyet Farkı         : {abs(diff):12,.2f} {currency}\n"
            output += f"Fark Yüzdesi          : {abs(diff_pct):12.1f}%\n"

            if diff > 0:
                output += f"\n✓ DIŞ KAYNAK {diff:,.2f} {currency} DAHA AVANTAJLI\n"
            elif diff < 0:
                output += f"\n✓ KENDİ TEST {abs(diff):,.2f} {currency} DAHA AVANTAJLI\n"
            else:
                output += f"\n• Maliyetler eşit\n"

            self.scenario_text.insert('1.0', output)

            # Grafik çiz
            self.plot_scenario_graph(results, currency)

            # Son hesaplamayı sakla
            self.last_calculation = {
                'type': 'scenario',
                'results': results,
                'test_type': test_type,
                'region': region_name,
                'currency': currency
            }

        except Exception as e:
            messagebox.showerror("Hata", f"Karşılaştırma hatası: {str(e)}")

    def plot_scenario_graph(self, results: Dict, currency: str):
        """Senaryo karşılaştırma grafiği"""
        self.scen_figure.clear()

        # Veri hazırla
        scenarios = ['Kendi Test', 'Dış Kaynak']
        in_house = results['in_house']
        outsource = results['outsource']

        # Maliyet bileşenleri
        categories = ['İşçilik', 'Enerji', 'Ekipman', 'Bakım', 'Tesis', 'Diğer']
        in_house_costs = [
            in_house.labor_cost,
            in_house.energy_cost,
            in_house.equipment_depreciation,
            in_house.maintenance_cost,
            in_house.facility_cost,
            in_house.calibration_cost + in_house.consumables_cost
        ]
        outsource_costs = [
            outsource.labor_cost,
            outsource.energy_cost,
            outsource.equipment_depreciation,
            outsource.maintenance_cost,
            outsource.facility_cost,
            outsource.calibration_cost + outsource.consumables_cost
        ]

        # Toplam karşılaştırma
        ax1 = self.scen_figure.add_subplot(2, 1, 1)
        totals = [in_house.total_cost, outsource.total_cost]
        bars = ax1.bar(scenarios, totals, color=['#4CAF50', '#FF9800'], alpha=0.7)
        ax1.set_ylabel(f'Toplam Maliyet ({currency})')
        ax1.set_title('Toplam Maliyet Karşılaştırması')
        ax1.grid(True, alpha=0.3)

        for bar, total in zip(bars, totals):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{total:,.0f}', ha='center', va='bottom')

        # Detaylı karşılaştırma
        ax2 = self.scen_figure.add_subplot(2, 1, 2)
        x = range(len(categories))
        width = 0.35

        ax2.bar([i - width/2 for i in x], in_house_costs, width,
                label='Kendi Test', color='#4CAF50', alpha=0.7)
        ax2.bar([i + width/2 for i in x], outsource_costs, width,
                label='Dış Kaynak', color='#FF9800', alpha=0.7)

        ax2.set_ylabel(f'Maliyet ({currency})')
        ax2.set_title('Maliyet Bileşenleri Karşılaştırması')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        self.scen_figure.tight_layout()
        self.scen_canvas.draw()

    def create_timeline_graph(self):
        """Zaman-maliyet grafiği oluştur"""
        try:
            test_type = self.time_test_type_var.get()
            region_name = self.time_region_var.get()
            region = self.get_region_key(region_name)
            currency = self.time_currency_var.get()

            # Zaman serisini al
            times, costs = self.calculator.get_cost_timeline(
                test_type=test_type,
                region=region,
                battery_count=1,
                target_currency=currency,
                time_points=20
            )

            # Grafik çiz
            self.timeline_figure.clear()
            ax = self.timeline_figure.add_subplot(1, 1, 1)

            ax.plot(times, costs, 'b-', linewidth=2, marker='o', markersize=4, label='Toplam Maliyet')
            ax.fill_between(times, costs, alpha=0.3)

            ax.set_xlabel('Test Süresi (saat)')
            ax.set_ylabel(f'Toplam Maliyet ({currency})')
            ax.set_title(f'Zaman-Maliyet İlişkisi\n{self.calculator.TEST_PROFILES[test_type].test_type} - {region_name}')
            ax.grid(True, alpha=0.3)
            ax.legend()

            # İstatistikler ekle
            profile = self.calculator.TEST_PROFILES[test_type]
            typical_cost = costs[-1] if costs else 0
            cost_per_hour = typical_cost / profile.typical_duration_hours if profile.typical_duration_hours > 0 else 0

            textstr = f'Tipik Test Süresi: {profile.typical_duration_hours:.0f} saat\n'
            textstr += f'Toplam Maliyet: {typical_cost:,.2f} {currency}\n'
            textstr += f'Saatlik Maliyet: {cost_per_hour:,.2f} {currency}/saat'

            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=9,
                   verticalalignment='top', bbox=props)

            self.timeline_figure.tight_layout()
            self.timeline_canvas.draw()

            # Son hesaplamayı sakla
            self.last_calculation = {
                'type': 'timeline',
                'times': times,
                'costs': costs,
                'test_type': test_type,
                'region': region_name,
                'currency': currency
            }

        except Exception as e:
            messagebox.showerror("Hata", f"Grafik oluşturma hatası: {str(e)}")

    def export_to_excel(self):
        """Excel'e aktar"""
        if not self.last_calculation:
            messagebox.showwarning("Uyarı", "Önce bir hesaplama yapın!")
            return

        try:
            import openpyxl
            from openpyxl.styles import Font, Alignment, PatternFill
            from openpyxl.chart import BarChart, Reference

            # Dosya adı sor
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"batarya_test_maliyet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not filename:
                return

            # Workbook oluştur
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Maliyet Analizi"

            # Başlık
            ws['A1'] = 'BATARYA TEST MALİYETİ ANALİZİ'
            ws['A1'].font = Font(size=16, bold=True)
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:E1')

            # Tarih
            ws['A2'] = f'Rapor Tarihi: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            ws.merge_cells('A2:E2')

            row = 4

            calc_type = self.last_calculation['type']

            if calc_type == 'single':
                # Tekli hesaplama
                breakdown = self.last_calculation['breakdown']
                ws[f'A{row}'] = 'MALİYET DAĞILIMI'
                ws[f'A{row}'].font = Font(bold=True)
                row += 1

                headers = ['Maliyet Kalemi', 'Tutar', 'Para Birimi', 'Yüzde']
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=row, column=col, value=header)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
                row += 1

                items = [
                    ('İşçilik', breakdown.labor_cost),
                    ('Enerji', breakdown.energy_cost),
                    ('Ekipman Amortismanı', breakdown.equipment_depreciation),
                    ('Bakım', breakdown.maintenance_cost),
                    ('Tesis', breakdown.facility_cost),
                    ('Kalibrasyon', breakdown.calibration_cost),
                    ('Sarf Malzemeleri', breakdown.consumables_cost),
                    ('TOPLAM', breakdown.total_cost)
                ]

                for label, cost in items:
                    pct = (cost / breakdown.total_cost * 100) if breakdown.total_cost > 0 else 0
                    ws.cell(row=row, column=1, value=label)
                    ws.cell(row=row, column=2, value=cost)
                    ws.cell(row=row, column=3, value=breakdown.currency)
                    ws.cell(row=row, column=4, value=f'{pct:.1f}%')
                    if label == 'TOPLAM':
                        for col in range(1, 5):
                            ws.cell(row=row, column=col).font = Font(bold=True)
                    row += 1

            elif calc_type == 'comparison':
                # Bölgesel karşılaştırma
                results = self.last_calculation['results']
                currency = self.last_calculation['currency']

                ws[f'A{row}'] = 'BÖLGESEL KARŞILAŞTIRMA'
                ws[f'A{row}'].font = Font(bold=True)
                row += 1

                headers = ['Bölge', 'Toplam Maliyet', 'İşçilik', 'Enerji', 'Ekipman']
                for col, header in enumerate(headers, 1):
                    cell = ws.cell(row=row, column=col, value=header)
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color='CCCCCC', end_color='CCCCCC', fill_type='solid')
                row += 1

                for region_key, breakdown in results.items():
                    region_name = self.calculator.REGIONAL_DATA[region_key].region
                    ws.cell(row=row, column=1, value=region_name)
                    ws.cell(row=row, column=2, value=breakdown.total_cost)
                    ws.cell(row=row, column=3, value=breakdown.labor_cost)
                    ws.cell(row=row, column=4, value=breakdown.energy_cost)
                    ws.cell(row=row, column=5, value=breakdown.equipment_depreciation)
                    row += 1

            # Kaydet
            wb.save(filename)

            self.export_info_label.config(
                text=f"✓ Excel export başarılı: {os.path.basename(filename)}",
                foreground='green'
            )
            messagebox.showinfo("Başarılı", f"Excel dosyası oluşturuldu:\n{filename}")

        except ImportError:
            messagebox.showerror("Hata", "openpyxl kütüphanesi gerekli!\npip install openpyxl")
        except Exception as e:
            messagebox.showerror("Hata", f"Excel export hatası: {str(e)}")

    def export_to_json(self):
        """JSON'a aktar"""
        if not self.last_calculation:
            messagebox.showwarning("Uyarı", "Önce bir hesaplama yapın!")
            return

        try:
            # Dosya adı sor
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=f"batarya_test_maliyet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            if not filename:
                return

            # JSON hazırla
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'calculation_type': self.last_calculation['type'],
                'data': {}
            }

            calc_type = self.last_calculation['type']

            if calc_type == 'single':
                breakdown = self.last_calculation['breakdown']
                export_data['data'] = {
                    'test_type': self.last_calculation['test_type'],
                    'region': self.last_calculation['region'],
                    'battery_count': self.last_calculation['battery_count'],
                    'cost_breakdown': breakdown.to_dict()
                }

            elif calc_type == 'comparison':
                results = self.last_calculation['results']
                export_data['data'] = {
                    'test_type': self.last_calculation['test_type'],
                    'currency': self.last_calculation['currency'],
                    'regional_comparison': {
                        self.calculator.REGIONAL_DATA[key].region: breakdown.to_dict()
                        for key, breakdown in results.items()
                    }
                }

            elif calc_type == 'scenario':
                results = self.last_calculation['results']
                export_data['data'] = {
                    'test_type': self.last_calculation['test_type'],
                    'region': self.last_calculation['region'],
                    'currency': self.last_calculation['currency'],
                    'scenarios': {
                        'in_house': results['in_house'].to_dict(),
                        'outsource': results['outsource'].to_dict()
                    }
                }

            elif calc_type == 'timeline':
                export_data['data'] = {
                    'test_type': self.last_calculation['test_type'],
                    'region': self.last_calculation['region'],
                    'currency': self.last_calculation['currency'],
                    'timeline': {
                        'times': self.last_calculation['times'],
                        'costs': self.last_calculation['costs']
                    }
                }

            # Kaydet
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            self.export_info_label.config(
                text=f"✓ JSON export başarılı: {os.path.basename(filename)}",
                foreground='green'
            )
            messagebox.showinfo("Başarılı", f"JSON dosyası oluşturuldu:\n{filename}")

        except Exception as e:
            messagebox.showerror("Hata", f"JSON export hatası: {str(e)}")

    def export_to_pdf(self):
        """PDF'e aktar (şimdilik devre dışı)"""
        messagebox.showinfo("Bilgi", "PDF export özelliği yakında eklenecek!")


def main():
    """Ana uygulama"""
    root = tk.Tk()
    app = BatteryTestCostGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

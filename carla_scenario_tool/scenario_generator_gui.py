#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARLA Senaryo Oluşturma Arayüzü
Tkinter tabanlı GUI, Ubuntu 22.04 ve Python 3.7+ uyumlu
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from typing import Optional

from scenario_config import (
    ScenarioConfig, EgoVehicleConfig, NPCActorConfig, WeatherConfig, TimeConfig,
    Transform, Vector3D, Waypoint, WeatherPreset, ActorType,
    VEHICLE_BLUEPRINTS, PEDESTRIAN_BLUEPRINTS, CARLA_MAPS, BEHAVIOR_TYPES
)
from scenario_io import ScenarioIO


class ScenarioGeneratorGUI:
    """CARLA Senaryo Oluşturma Ana Arayüz"""

    def __init__(self, root):
        self.root = root
        self.root.title("CARLA Otonom Araç Test Senaryosu Oluşturucu")
        self.root.geometry("1200x800")

        # Mevcut senaryo
        self.current_scenario = ScenarioConfig()
        self.current_file_path = None

        # Ana layout
        self._create_menu()
        self._create_main_layout()
        self._update_ui_from_scenario()

    def _create_menu(self):
        """Menü çubuğu oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Yeni Senaryo", command=self.new_scenario)
        file_menu.add_command(label="Aç...", command=self.load_scenario)
        file_menu.add_command(label="Kaydet", command=self.save_scenario)
        file_menu.add_command(label="Farklı Kaydet...", command=self.save_scenario_as)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.root.quit)

        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self.show_about)

    def _create_main_layout(self):
        """Ana layout oluştur"""
        # Sol panel: Senaryo özellikleri
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Sağ panel: NPC Aktörler
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Grid ağırlıkları
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Sol panel içerik
        self._create_scenario_info_section(left_frame)
        self._create_ego_vehicle_section(left_frame)
        self._create_environment_section(left_frame)

        # Sağ panel içerik
        self._create_npc_actors_section(right_frame)

        # Alt butonlar
        self._create_bottom_buttons()

    def _create_scenario_info_section(self, parent):
        """Senaryo bilgileri bölümü"""
        frame = ttk.LabelFrame(parent, text="Senaryo Bilgileri", padding="10")
        frame.pack(fill=tk.X, pady=5)

        # Senaryo adı
        ttk.Label(frame, text="Senaryo Adı:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.scenario_name = tk.StringVar(value=self.current_scenario.name)
        ttk.Entry(frame, textvariable=self.scenario_name, width=40).grid(row=0, column=1, pady=2)

        # Açıklama
        ttk.Label(frame, text="Açıklama:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.scenario_desc = tk.Text(frame, width=40, height=3)
        self.scenario_desc.grid(row=1, column=1, pady=2)
        self.scenario_desc.insert("1.0", self.current_scenario.description)

        # Harita
        ttk.Label(frame, text="CARLA Harita:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.carla_map = tk.StringVar(value=self.current_scenario.carla_map)
        ttk.Combobox(frame, textvariable=self.carla_map, values=CARLA_MAPS,
                     state="readonly", width=37).grid(row=2, column=1, pady=2)

        # Süre
        ttk.Label(frame, text="Süre (saniye):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.duration = tk.DoubleVar(value=self.current_scenario.duration)
        ttk.Spinbox(frame, from_=0, to=3600, textvariable=self.duration,
                    width=38).grid(row=3, column=1, pady=2)

    def _create_ego_vehicle_section(self, parent):
        """Ego vehicle (test aracı) bölümü"""
        frame = ttk.LabelFrame(parent, text="Ego Vehicle (Test Edilen Araç)", padding="10")
        frame.pack(fill=tk.X, pady=5)

        # Araç modeli
        ttk.Label(frame, text="Araç Modeli:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ego_blueprint = tk.StringVar(value=self.current_scenario.ego_vehicle.blueprint)
        ttk.Combobox(frame, textvariable=self.ego_blueprint, values=VEHICLE_BLUEPRINTS,
                     width=37).grid(row=0, column=1, pady=2, columnspan=3)

        # Spawn pozisyonu
        ttk.Label(frame, text="Spawn Konumu:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.ego_spawn_x = tk.DoubleVar(value=self.current_scenario.ego_vehicle.spawn_point.location.x)
        self.ego_spawn_y = tk.DoubleVar(value=self.current_scenario.ego_vehicle.spawn_point.location.y)
        self.ego_spawn_z = tk.DoubleVar(value=self.current_scenario.ego_vehicle.spawn_point.location.z)

        ttk.Label(frame, text="X:").grid(row=1, column=1, sticky=tk.E)
        ttk.Spinbox(frame, from_=-1000, to=1000, textvariable=self.ego_spawn_x,
                    width=8, increment=0.1).grid(row=1, column=2, padx=2)
        ttk.Label(frame, text="Y:").grid(row=1, column=3, sticky=tk.E)
        ttk.Spinbox(frame, from_=-1000, to=1000, textvariable=self.ego_spawn_y,
                    width=8, increment=0.1).grid(row=1, column=4, padx=2)
        ttk.Label(frame, text="Z:").grid(row=1, column=5, sticky=tk.E)
        ttk.Spinbox(frame, from_=0, to=100, textvariable=self.ego_spawn_z,
                    width=8, increment=0.1).grid(row=1, column=6, padx=2)

        # Spawn rotasyonu (Yaw)
        ttk.Label(frame, text="Spawn Yönü (Yaw):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.ego_yaw = tk.DoubleVar(value=self.current_scenario.ego_vehicle.spawn_point.rotation.y)
        ttk.Spinbox(frame, from_=0, to=360, textvariable=self.ego_yaw,
                    width=10, increment=1).grid(row=2, column=1, columnspan=2, pady=2)

        # Hız ayarları
        ttk.Label(frame, text="Hedef Hız (km/h):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.ego_target_speed = tk.DoubleVar(value=self.current_scenario.ego_vehicle.target_speed)
        ttk.Spinbox(frame, from_=0, to=200, textvariable=self.ego_target_speed,
                    width=10, increment=5).grid(row=3, column=1, columnspan=2, pady=2)

        # Autopilot
        self.ego_autopilot = tk.BooleanVar(value=self.current_scenario.ego_vehicle.enable_autopilot)
        ttk.Checkbutton(frame, text="CARLA Autopilot Aktif",
                       variable=self.ego_autopilot).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=2)

        # Waypoint düzenleme butonu
        ttk.Button(frame, text="Waypoint Rotası Düzenle",
                  command=self.edit_ego_waypoints).grid(row=5, column=0, columnspan=4, pady=5)

    def _create_environment_section(self, parent):
        """Çevre koşulları bölümü"""
        frame = ttk.LabelFrame(parent, text="Çevre Koşulları", padding="10")
        frame.pack(fill=tk.X, pady=5)

        # Hava durumu preset
        ttk.Label(frame, text="Hava Durumu:").grid(row=0, column=0, sticky=tk.W, pady=2)
        weather_presets = [e.value for e in WeatherPreset]
        self.weather_preset = tk.StringVar(value=self.current_scenario.weather.preset)
        weather_combo = ttk.Combobox(frame, textvariable=self.weather_preset,
                                    values=weather_presets, state="readonly", width=37)
        weather_combo.grid(row=0, column=1, pady=2)
        weather_combo.bind("<<ComboboxSelected>>", self._on_weather_preset_change)

        # Özel hava ayarları frame
        self.custom_weather_frame = ttk.Frame(frame)
        self.custom_weather_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Bulutluluk
        ttk.Label(self.custom_weather_frame, text="Bulutluluk (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cloudiness = tk.DoubleVar(value=self.current_scenario.weather.cloudiness)
        ttk.Scale(self.custom_weather_frame, from_=0, to=100, variable=self.cloudiness,
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, pady=2)
        ttk.Label(self.custom_weather_frame, textvariable=self.cloudiness).grid(row=0, column=2, padx=5)

        # Yağmur
        ttk.Label(self.custom_weather_frame, text="Yağmur (%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.precipitation = tk.DoubleVar(value=self.current_scenario.weather.precipitation)
        ttk.Scale(self.custom_weather_frame, from_=0, to=100, variable=self.precipitation,
                 orient=tk.HORIZONTAL, length=200).grid(row=1, column=1, pady=2)
        ttk.Label(self.custom_weather_frame, textvariable=self.precipitation).grid(row=1, column=2, padx=5)

        # Sis
        ttk.Label(self.custom_weather_frame, text="Sis Yoğunluğu (%):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.fog_density = tk.DoubleVar(value=self.current_scenario.weather.fog_density)
        ttk.Scale(self.custom_weather_frame, from_=0, to=100, variable=self.fog_density,
                 orient=tk.HORIZONTAL, length=200).grid(row=2, column=1, pady=2)
        ttk.Label(self.custom_weather_frame, textvariable=self.fog_density).grid(row=2, column=2, padx=5)

        # Rüzgar
        ttk.Label(self.custom_weather_frame, text="Rüzgar Şiddeti (%):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.wind_intensity = tk.DoubleVar(value=self.current_scenario.weather.wind_intensity)
        ttk.Scale(self.custom_weather_frame, from_=0, to=100, variable=self.wind_intensity,
                 orient=tk.HORIZONTAL, length=200).grid(row=3, column=1, pady=2)
        ttk.Label(self.custom_weather_frame, textvariable=self.wind_intensity).grid(row=3, column=2, padx=5)

        # Zaman
        time_frame = ttk.Frame(frame)
        time_frame.grid(row=2, column=0, columnspan=2, pady=5)

        ttk.Label(time_frame, text="Saat:").pack(side=tk.LEFT, padx=5)
        self.time_hour = tk.IntVar(value=self.current_scenario.time.hour)
        ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.time_hour,
                   width=5).pack(side=tk.LEFT)

        ttk.Label(time_frame, text="Dakika:").pack(side=tk.LEFT, padx=5)
        self.time_minute = tk.IntVar(value=self.current_scenario.time.minute)
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.time_minute,
                   width=5).pack(side=tk.LEFT)

        self._update_custom_weather_visibility()

    def _create_npc_actors_section(self, parent):
        """NPC aktörler bölümü"""
        frame = ttk.LabelFrame(parent, text="NPC Aktörler (Hedef Araçlar ve Yayalar)", padding="10")
        frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Butonlar
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="+ Araç Ekle",
                  command=self.add_npc_vehicle).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="+ Yaya Ekle",
                  command=self.add_npc_pedestrian).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Düzenle",
                  command=self.edit_npc_actor).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil",
                  command=self.delete_npc_actor).pack(side=tk.LEFT, padx=5)

        # NPC listesi
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.npc_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, height=20)
        self.npc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.npc_listbox.yview)

        # Çift tıklama ile düzenleme
        self.npc_listbox.bind("<Double-Button-1>", lambda e: self.edit_npc_actor())

    def _create_bottom_buttons(self):
        """Alt butonlar"""
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Yeni Senaryo",
                  command=self.new_scenario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Senaryo Yükle",
                  command=self.load_scenario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Kaydet",
                  command=self.save_scenario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="Farklı Kaydet",
                  command=self.save_scenario_as).pack(side=tk.LEFT, padx=5)

        ttk.Separator(frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(frame, text="Senaryo Özeti",
                  command=self.show_scenario_summary).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame, text="CARLA'da Çalıştır",
                  command=self.run_in_carla).pack(side=tk.LEFT, padx=5)

    # Event handlers
    def _on_weather_preset_change(self, event=None):
        """Hava durumu preset değiştiğinde"""
        self._update_custom_weather_visibility()

    def _update_custom_weather_visibility(self):
        """Custom weather ayarlarını göster/gizle"""
        if self.weather_preset.get() == WeatherPreset.CUSTOM.value:
            for child in self.custom_weather_frame.winfo_children():
                child.config(state=tk.NORMAL)
        else:
            for child in self.custom_weather_frame.winfo_children():
                if isinstance(child, (ttk.Label, ttk.Scale)):
                    child.config(state=tk.DISABLED if isinstance(child, ttk.Scale) else tk.NORMAL)

    def _update_ui_from_scenario(self):
        """Mevcut senaryodan UI'yi güncelle"""
        # Temel bilgiler
        self.scenario_name.set(self.current_scenario.name)
        self.scenario_desc.delete("1.0", tk.END)
        self.scenario_desc.insert("1.0", self.current_scenario.description)
        self.carla_map.set(self.current_scenario.carla_map)
        self.duration.set(self.current_scenario.duration)

        # Ego vehicle
        ego = self.current_scenario.ego_vehicle
        self.ego_blueprint.set(ego.blueprint)
        self.ego_spawn_x.set(ego.spawn_point.location.x)
        self.ego_spawn_y.set(ego.spawn_point.location.y)
        self.ego_spawn_z.set(ego.spawn_point.location.z)
        self.ego_yaw.set(ego.spawn_point.rotation.y)
        self.ego_target_speed.set(ego.target_speed)
        self.ego_autopilot.set(ego.enable_autopilot)

        # Hava durumu
        weather = self.current_scenario.weather
        self.weather_preset.set(weather.preset)
        self.cloudiness.set(weather.cloudiness)
        self.precipitation.set(weather.precipitation)
        self.fog_density.set(weather.fog_density)
        self.wind_intensity.set(weather.wind_intensity)

        # Zaman
        self.time_hour.set(self.current_scenario.time.hour)
        self.time_minute.set(self.current_scenario.time.minute)

        # NPC listesi
        self._refresh_npc_list()

    def _update_scenario_from_ui(self):
        """UI'dan mevcut senaryoyu güncelle"""
        # Temel bilgiler
        self.current_scenario.name = self.scenario_name.get()
        self.current_scenario.description = self.scenario_desc.get("1.0", tk.END).strip()
        self.current_scenario.carla_map = self.carla_map.get()
        self.current_scenario.duration = self.duration.get()

        # Ego vehicle
        ego = self.current_scenario.ego_vehicle
        ego.blueprint = self.ego_blueprint.get()
        ego.spawn_point.location.x = self.ego_spawn_x.get()
        ego.spawn_point.location.y = self.ego_spawn_y.get()
        ego.spawn_point.location.z = self.ego_spawn_z.get()
        ego.spawn_point.rotation.y = self.ego_yaw.get()
        ego.target_speed = self.ego_target_speed.get()
        ego.enable_autopilot = self.ego_autopilot.get()

        # Hava durumu
        weather = self.current_scenario.weather
        weather.preset = self.weather_preset.get()
        weather.cloudiness = self.cloudiness.get()
        weather.precipitation = self.precipitation.get()
        weather.fog_density = self.fog_density.get()
        weather.wind_intensity = self.wind_intensity.get()

        # Zaman
        self.current_scenario.time.hour = self.time_hour.get()
        self.current_scenario.time.minute = self.time_minute.get()

    def _refresh_npc_list(self):
        """NPC listesini yenile"""
        self.npc_listbox.delete(0, tk.END)
        for npc in self.current_scenario.npc_actors:
            display_text = f"{npc.actor_id} ({npc.actor_type}) - {npc.blueprint}"
            self.npc_listbox.insert(tk.END, display_text)

    # Menü komutları
    def new_scenario(self):
        """Yeni senaryo oluştur"""
        if messagebox.askyesno("Yeni Senaryo", "Mevcut senaryodaki değişiklikler kaybolacak. Devam?"):
            self.current_scenario = ScenarioConfig()
            self.current_file_path = None
            self._update_ui_from_scenario()
            messagebox.showinfo("Başarılı", "Yeni senaryo oluşturuldu")

    def load_scenario(self):
        """Senaryo yükle"""
        file_path = filedialog.askopenfilename(
            title="Senaryo Yükle",
            initialdir="scenarios",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            scenario = ScenarioIO.load_scenario(file_path)
            if scenario:
                self.current_scenario = scenario
                self.current_file_path = file_path
                self._update_ui_from_scenario()
                messagebox.showinfo("Başarılı", f"Senaryo yüklendi: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Hata", "Senaryo yüklenemedi!")

    def save_scenario(self):
        """Mevcut senaryoyu kaydet"""
        if self.current_file_path:
            self._update_scenario_from_ui()
            if ScenarioIO.save_scenario(self.current_scenario, self.current_file_path):
                messagebox.showinfo("Başarılı", "Senaryo kaydedildi")
            else:
                messagebox.showerror("Hata", "Senaryo kaydedilemedi!")
        else:
            self.save_scenario_as()

    def save_scenario_as(self):
        """Farklı kaydet"""
        self._update_scenario_from_ui()

        file_path = filedialog.asksaveasfilename(
            title="Senaryo Kaydet",
            initialdir="scenarios",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            if ScenarioIO.save_scenario(self.current_scenario, file_path):
                self.current_file_path = file_path
                messagebox.showinfo("Başarılı", f"Senaryo kaydedildi: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Hata", "Senaryo kaydedilemedi!")

    def show_about(self):
        """Hakkında dialog"""
        messagebox.showinfo(
            "Hakkında",
            "CARLA Otonom Araç Test Senaryosu Oluşturucu\n\n"
            "Versiyon 1.0\n"
            "Python 3.7+ | Ubuntu 22.04\n\n"
            "CARLA simülatöründe otonom araç testleri için\n"
            "senaryo oluşturma ve yönetme aracı"
        )

    # NPC yönetim komutları
    def add_npc_vehicle(self):
        """Yeni NPC araç ekle"""
        NPCEditorDialog(self.root, self.current_scenario, actor_type=ActorType.VEHICLE,
                       callback=self._refresh_npc_list)

    def add_npc_pedestrian(self):
        """Yeni NPC yaya ekle"""
        NPCEditorDialog(self.root, self.current_scenario, actor_type=ActorType.PEDESTRIAN,
                       callback=self._refresh_npc_list)

    def edit_npc_actor(self):
        """Seçili NPC'yi düzenle"""
        selection = self.npc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir aktör seçin")
            return

        index = selection[0]
        npc = self.current_scenario.npc_actors[index]
        actor_type = ActorType.VEHICLE if npc.actor_type == ActorType.VEHICLE.value else ActorType.PEDESTRIAN

        NPCEditorDialog(self.root, self.current_scenario, actor_type=actor_type,
                       npc_actor=npc, callback=self._refresh_npc_list)

    def delete_npc_actor(self):
        """Seçili NPC'yi sil"""
        selection = self.npc_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir aktör seçin")
            return

        index = selection[0]
        npc = self.current_scenario.npc_actors[index]

        if messagebox.askyesno("Sil", f"{npc.actor_id} aktörünü silmek istediğinizden emin misiniz?"):
            del self.current_scenario.npc_actors[index]
            self._refresh_npc_list()

    def edit_ego_waypoints(self):
        """Ego vehicle waypoint'lerini düzenle"""
        WaypointEditorDialog(self.root, self.current_scenario.ego_vehicle.route_waypoints,
                           title="Ego Vehicle Waypoint Rotası")

    def show_scenario_summary(self):
        """Senaryo özetini göster"""
        self._update_scenario_from_ui()
        summary = ScenarioIO.export_scenario_summary(self.current_scenario)

        # Özet penceresi
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Senaryo Özeti")
        summary_window.geometry("700x600")

        text_widget = tk.Text(summary_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", summary)
        text_widget.config(state=tk.DISABLED)

        ttk.Button(summary_window, text="Kapat",
                  command=summary_window.destroy).pack(pady=5)

    def run_in_carla(self):
        """CARLA'da senaryoyu çalıştır"""
        self._update_scenario_from_ui()

        # Senaryo geçerliliğini kontrol et
        valid, errors = self.current_scenario.validate()
        if not valid:
            error_msg = "Senaryo geçerli değil:\n" + "\n".join(errors)
            messagebox.showerror("Geçersiz Senaryo", error_msg)
            return

        # Geçici dosyaya kaydet
        temp_file = "scenarios/temp_run.json"
        os.makedirs("scenarios", exist_ok=True)

        if ScenarioIO.save_scenario(self.current_scenario, temp_file):
            messagebox.showinfo(
                "CARLA'da Çalıştır",
                f"Senaryo '{temp_file}' olarak kaydedildi.\n\n"
                "Terminalde şu komutu çalıştırın:\n"
                f"python carla_runner.py {temp_file}"
            )
        else:
            messagebox.showerror("Hata", "Senaryo kaydedilemedi!")


class NPCEditorDialog:
    """NPC aktör düzenleme dialog"""

    def __init__(self, parent, scenario: ScenarioConfig, actor_type: ActorType,
                 npc_actor: Optional[NPCActorConfig] = None, callback=None):
        self.scenario = scenario
        self.actor_type = actor_type
        self.npc_actor = npc_actor
        self.callback = callback
        self.is_new = npc_actor is None

        # Dialog penceresi
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{'Yeni' if self.is_new else 'Düzenle'} NPC {actor_type.value.title()}")
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Yeni ise boş oluştur
        if self.is_new:
            self.npc_actor = NPCActorConfig(
                actor_id=f"npc_{actor_type.value}_{len(scenario.npc_actors)+1}",
                actor_type=actor_type.value
            )

        self._create_ui()

    def _create_ui(self):
        """Dialog UI oluştur"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ID
        ttk.Label(main_frame, text="Aktör ID:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.actor_id = tk.StringVar(value=self.npc_actor.actor_id)
        ttk.Entry(main_frame, textvariable=self.actor_id, width=40).grid(row=0, column=1, pady=5)

        # Blueprint
        ttk.Label(main_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        blueprints = VEHICLE_BLUEPRINTS if self.actor_type == ActorType.VEHICLE else PEDESTRIAN_BLUEPRINTS
        self.blueprint = tk.StringVar(value=self.npc_actor.blueprint)
        ttk.Combobox(main_frame, textvariable=self.blueprint, values=blueprints,
                    width=37).grid(row=1, column=1, pady=5)

        # Spawn konumu
        spawn_frame = ttk.LabelFrame(main_frame, text="Spawn Konumu", padding="5")
        spawn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(spawn_frame, text="X:").grid(row=0, column=0)
        self.spawn_x = tk.DoubleVar(value=self.npc_actor.spawn_point.location.x)
        ttk.Spinbox(spawn_frame, from_=-1000, to=1000, textvariable=self.spawn_x,
                   width=12, increment=0.1).grid(row=0, column=1, padx=5)

        ttk.Label(spawn_frame, text="Y:").grid(row=0, column=2)
        self.spawn_y = tk.DoubleVar(value=self.npc_actor.spawn_point.location.y)
        ttk.Spinbox(spawn_frame, from_=-1000, to=1000, textvariable=self.spawn_y,
                   width=12, increment=0.1).grid(row=0, column=3, padx=5)

        ttk.Label(spawn_frame, text="Z:").grid(row=0, column=4)
        self.spawn_z = tk.DoubleVar(value=self.npc_actor.spawn_point.location.z)
        ttk.Spinbox(spawn_frame, from_=0, to=100, textvariable=self.spawn_z,
                   width=12, increment=0.1).grid(row=0, column=5, padx=5)

        ttk.Label(spawn_frame, text="Yaw:").grid(row=1, column=0)
        self.spawn_yaw = tk.DoubleVar(value=self.npc_actor.spawn_point.rotation.y)
        ttk.Spinbox(spawn_frame, from_=0, to=360, textvariable=self.spawn_yaw,
                   width=12, increment=1).grid(row=1, column=1, padx=5)

        # Davranış
        ttk.Label(main_frame, text="Davranış:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.behavior = tk.StringVar(value=self.npc_actor.behavior)
        ttk.Combobox(main_frame, textvariable=self.behavior, values=BEHAVIOR_TYPES,
                    state="readonly", width=37).grid(row=3, column=1, pady=5)

        # Waypoints
        waypoint_frame = ttk.LabelFrame(main_frame, text="Hareket Rotası (Waypoints)", padding="5")
        waypoint_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        main_frame.rowconfigure(4, weight=1)

        ttk.Button(waypoint_frame, text="Waypoint'leri Düzenle",
                  command=self.edit_waypoints).pack(pady=10)

        self.waypoint_label = ttk.Label(waypoint_frame,
                                       text=f"Waypoint sayısı: {len(self.npc_actor.route_waypoints)}")
        self.waypoint_label.pack()

        # Auto destroy
        self.auto_destroy = tk.BooleanVar(value=self.npc_actor.auto_destroy)
        ttk.Checkbutton(main_frame, text="Rota bitince aktörü yok et",
                       variable=self.auto_destroy).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Kaydet", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_waypoints(self):
        """Waypoint'leri düzenle"""
        WaypointEditorDialog(self.dialog, self.npc_actor.route_waypoints,
                           title=f"{self.npc_actor.actor_id} Waypoint Rotası",
                           callback=self.update_waypoint_count)

    def update_waypoint_count(self):
        """Waypoint sayısını güncelle"""
        self.waypoint_label.config(text=f"Waypoint sayısı: {len(self.npc_actor.route_waypoints)}")

    def save(self):
        """NPC'yi kaydet"""
        # Verileri güncelle
        self.npc_actor.actor_id = self.actor_id.get()
        self.npc_actor.blueprint = self.blueprint.get()
        self.npc_actor.spawn_point.location.x = self.spawn_x.get()
        self.npc_actor.spawn_point.location.y = self.spawn_y.get()
        self.npc_actor.spawn_point.location.z = self.spawn_z.get()
        self.npc_actor.spawn_point.rotation.y = self.spawn_yaw.get()
        self.npc_actor.behavior = self.behavior.get()
        self.npc_actor.auto_destroy = self.auto_destroy.get()

        # Yeni ise listeye ekle
        if self.is_new:
            self.scenario.npc_actors.append(self.npc_actor)

        # Callback çağır
        if self.callback:
            self.callback()

        self.dialog.destroy()


class WaypointEditorDialog:
    """Waypoint düzenleme dialog"""

    def __init__(self, parent, waypoints: list, title="Waypoint Düzenle", callback=None):
        self.waypoints = waypoints
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_ui()

    def _create_ui(self):
        """Dialog UI oluştur"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="+ Waypoint Ekle",
                  command=self.add_waypoint).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Sil",
                  command=self.delete_waypoint).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Yukarı",
                  command=self.move_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Aşağı",
                  command=self.move_down).pack(side=tk.LEFT, padx=5)

        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(tree_frame, columns=("X", "Y", "Z", "Speed", "Wait"),
                                yscrollcommand=scrollbar.set, height=15)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Sütun başlıkları
        self.tree.heading("#0", text="#")
        self.tree.heading("X", text="X")
        self.tree.heading("Y", text="Y")
        self.tree.heading("Z", text="Z")
        self.tree.heading("Speed", text="Hız (km/h)")
        self.tree.heading("Wait", text="Bekleme (s)")

        self.tree.column("#0", width=50)
        self.tree.column("X", width=100)
        self.tree.column("Y", width=100)
        self.tree.column("Z", width=100)
        self.tree.column("Speed", width=100)
        self.tree.column("Wait", width=100)

        # Çift tıklama ile düzenleme
        self.tree.bind("<Double-Button-1>", lambda e: self.edit_waypoint())

        # Alt butonlar
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)

        ttk.Button(bottom_frame, text="Kapat",
                  command=self.close).pack(side=tk.RIGHT, padx=5)

        self._refresh_list()

    def _refresh_list(self):
        """Listeyi yenile"""
        self.tree.delete(*self.tree.get_children())
        for i, wp in enumerate(self.waypoints):
            self.tree.insert("", tk.END, text=str(i+1),
                           values=(f"{wp.location.x:.1f}", f"{wp.location.y:.1f}",
                                  f"{wp.location.z:.1f}", f"{wp.speed:.1f}", f"{wp.wait_time:.1f}"))

    def add_waypoint(self):
        """Yeni waypoint ekle"""
        new_wp = Waypoint()
        SingleWaypointEditorDialog(self.dialog, new_wp, is_new=True,
                                   callback=lambda: self._add_waypoint_callback(new_wp))

    def _add_waypoint_callback(self, waypoint):
        """Waypoint eklendiğinde"""
        self.waypoints.append(waypoint)
        self._refresh_list()
        if self.callback:
            self.callback()

    def edit_waypoint(self):
        """Seçili waypoint'i düzenle"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1

        SingleWaypointEditorDialog(self.dialog, self.waypoints[index], is_new=False,
                                   callback=self._refresh_list)

    def delete_waypoint(self):
        """Seçili waypoint'i sil"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir waypoint seçin")
            return

        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1

        if messagebox.askyesno("Sil", f"Waypoint #{index+1} silinsin mi?"):
            del self.waypoints[index]
            self._refresh_list()
            if self.callback:
                self.callback()

    def move_up(self):
        """Waypoint'i yukarı taşı"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1

        if index > 0:
            self.waypoints[index], self.waypoints[index-1] = self.waypoints[index-1], self.waypoints[index]
            self._refresh_list()
            if self.callback:
                self.callback()

    def move_down(self):
        """Waypoint'i aşağı taşı"""
        selection = self.tree.selection()
        if not selection:
            return

        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1

        if index < len(self.waypoints) - 1:
            self.waypoints[index], self.waypoints[index+1] = self.waypoints[index+1], self.waypoints[index]
            self._refresh_list()
            if self.callback:
                self.callback()

    def close(self):
        """Dialog'u kapat"""
        if self.callback:
            self.callback()
        self.dialog.destroy()


class SingleWaypointEditorDialog:
    """Tek waypoint düzenleme dialog"""

    def __init__(self, parent, waypoint: Waypoint, is_new=False, callback=None):
        self.waypoint = waypoint
        self.is_new = is_new
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Waypoint Düzenle" if not is_new else "Yeni Waypoint")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_ui()

    def _create_ui(self):
        """Dialog UI oluştur"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Konum
        ttk.Label(main_frame, text="X:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.x = tk.DoubleVar(value=self.waypoint.location.x)
        ttk.Spinbox(main_frame, from_=-1000, to=1000, textvariable=self.x,
                   width=20, increment=0.1).grid(row=0, column=1, pady=5)

        ttk.Label(main_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.y = tk.DoubleVar(value=self.waypoint.location.y)
        ttk.Spinbox(main_frame, from_=-1000, to=1000, textvariable=self.y,
                   width=20, increment=0.1).grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="Z:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.z = tk.DoubleVar(value=self.waypoint.location.z)
        ttk.Spinbox(main_frame, from_=0, to=100, textvariable=self.z,
                   width=20, increment=0.1).grid(row=2, column=1, pady=5)

        # Hız
        ttk.Label(main_frame, text="Hız (km/h):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.speed = tk.DoubleVar(value=self.waypoint.speed)
        ttk.Spinbox(main_frame, from_=0, to=200, textvariable=self.speed,
                   width=20, increment=5).grid(row=3, column=1, pady=5)

        # Bekleme süresi
        ttk.Label(main_frame, text="Bekleme (saniye):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.wait_time = tk.DoubleVar(value=self.waypoint.wait_time)
        ttk.Spinbox(main_frame, from_=0, to=300, textvariable=self.wait_time,
                   width=20, increment=1).grid(row=4, column=1, pady=5)

        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Kaydet", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="İptal", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save(self):
        """Waypoint'i kaydet"""
        self.waypoint.location.x = self.x.get()
        self.waypoint.location.y = self.y.get()
        self.waypoint.location.z = self.z.get()
        self.waypoint.speed = self.speed.get()
        self.waypoint.wait_time = self.wait_time.get()

        if self.callback:
            self.callback()

        self.dialog.destroy()


def main():
    """Ana program"""
    root = tk.Tk()
    app = ScenarioGeneratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

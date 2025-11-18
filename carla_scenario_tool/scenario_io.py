#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARLA Senaryo Kaydetme/Yükleme Modülü
Senaryoları JSON formatında kaydeder ve yükler.
Python 3.7+ uyumlu
"""

import json
import os
from typing import Optional
from datetime import datetime
from scenario_config import ScenarioConfig


class ScenarioIO:
    """Senaryo dosya işlemleri sınıfı"""

    @staticmethod
    def save_scenario(scenario: ScenarioConfig, file_path: str) -> bool:
        """
        Senaryoyu JSON dosyasına kaydet

        Args:
            scenario: Kaydedilecek senaryo konfigürasyonu
            file_path: Dosya yolu (json uzantılı)

        Returns:
            bool: Başarılı ise True
        """
        try:
            # Dosya yolunu kontrol et
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # .json uzantısı ekle
            if not file_path.endswith('.json'):
                file_path += '.json'

            # Senaryoyu dict'e çevir
            scenario_dict = scenario.to_dict()

            # Meta bilgiler ekle
            scenario_dict["_metadata"] = {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }

            # JSON'a kaydet (güzel formatla)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(scenario_dict, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Senaryo kaydetme hatası: {e}")
            return False

    @staticmethod
    def load_scenario(file_path: str) -> Optional[ScenarioConfig]:
        """
        JSON dosyasından senaryo yükle

        Args:
            file_path: Dosya yolu

        Returns:
            ScenarioConfig veya None (hata durumunda)
        """
        try:
            # Dosya var mı kontrol et
            if not os.path.exists(file_path):
                print(f"Dosya bulunamadı: {file_path}")
                return None

            # JSON'dan oku
            with open(file_path, 'r', encoding='utf-8') as f:
                scenario_dict = json.load(f)

            # Metadata varsa temizle
            if "_metadata" in scenario_dict:
                del scenario_dict["_metadata"]

            # ScenarioConfig nesnesine çevir
            scenario = ScenarioConfig.from_dict(scenario_dict)

            return scenario

        except json.JSONDecodeError as e:
            print(f"JSON parse hatası: {e}")
            return None
        except Exception as e:
            print(f"Senaryo yükleme hatası: {e}")
            return None

    @staticmethod
    def list_scenarios(directory: str = "scenarios") -> list:
        """
        Dizindeki tüm senaryo dosyalarını listele

        Args:
            directory: Senaryo dizini

        Returns:
            list: Senaryo dosya adları listesi
        """
        try:
            if not os.path.exists(directory):
                return []

            scenarios = []
            for filename in os.listdir(directory):
                if filename.endswith('.json'):
                    scenarios.append(filename)

            return sorted(scenarios)

        except Exception as e:
            print(f"Senaryo listeleme hatası: {e}")
            return []

    @staticmethod
    def export_scenario_summary(scenario: ScenarioConfig) -> str:
        """
        Senaryo özetini metin olarak döndür

        Args:
            scenario: Senaryo konfigürasyonu

        Returns:
            str: Senaryo özet metni
        """
        summary = []
        summary.append("=" * 60)
        summary.append(f"SENARYO: {scenario.name}")
        summary.append("=" * 60)
        summary.append(f"Açıklama: {scenario.description}")
        summary.append(f"Harita: {scenario.carla_map}")
        summary.append(f"Süre: {scenario.duration} saniye")
        summary.append("")

        summary.append("--- EGO VEHICLE (Test Edilen Araç) ---")
        summary.append(f"Model: {scenario.ego_vehicle.blueprint}")
        summary.append(f"Başlangıç Konumu: X={scenario.ego_vehicle.spawn_point.location.x:.1f}, "
                      f"Y={scenario.ego_vehicle.spawn_point.location.y:.1f}, "
                      f"Z={scenario.ego_vehicle.spawn_point.location.z:.1f}")
        summary.append(f"Hedef Hız: {scenario.ego_vehicle.target_speed} km/h")
        summary.append(f"Waypoint Sayısı: {len(scenario.ego_vehicle.route_waypoints)}")
        summary.append("")

        summary.append(f"--- NPC AKTÖRLER ({len(scenario.npc_actors)} adet) ---")
        for i, npc in enumerate(scenario.npc_actors, 1):
            summary.append(f"{i}. {npc.actor_id} ({npc.actor_type})")
            summary.append(f"   Model: {npc.blueprint}")
            summary.append(f"   Konum: X={npc.spawn_point.location.x:.1f}, "
                          f"Y={npc.spawn_point.location.y:.1f}, "
                          f"Z={npc.spawn_point.location.z:.1f}")
            summary.append(f"   Waypoint: {len(npc.route_waypoints)} adet")
        summary.append("")

        summary.append("--- HAVA DURUMU ---")
        summary.append(f"Preset: {scenario.weather.preset}")
        if scenario.weather.preset == "custom":
            summary.append(f"Bulutluluk: {scenario.weather.cloudiness}%")
            summary.append(f"Yağmur: {scenario.weather.precipitation}%")
            summary.append(f"Sis: {scenario.weather.fog_density}%")
            summary.append(f"Rüzgar: {scenario.weather.wind_intensity}%")
        summary.append("")

        summary.append("--- ZAMAN ---")
        summary.append(f"Saat: {scenario.time.hour:02d}:{scenario.time.minute:02d}")
        summary.append("=" * 60)

        return "\n".join(summary)


def create_example_scenarios():
    """Örnek senaryolar oluştur"""
    from scenario_config import (
        ScenarioConfig, EgoVehicleConfig, NPCActorConfig,
        Transform, Vector3D, Waypoint, WeatherConfig, TimeConfig,
        WeatherPreset, ActorType
    )

    scenarios_dir = "scenarios"
    os.makedirs(scenarios_dir, exist_ok=True)

    # Örnek 1: Basit düz yol senaryosu
    scenario1 = ScenarioConfig(
        name="Basit Düz Yol Testi",
        description="Tek bir NPC araç ile düz yolda takip senaryosu",
        carla_map="Town01",
        duration=120.0,
        ego_vehicle=EgoVehicleConfig(
            blueprint="vehicle.tesla.model3",
            spawn_point=Transform(
                location=Vector3D(x=100.0, y=50.0, z=0.5),
                rotation=Vector3D(x=0.0, y=0.0, z=0.0)
            ),
            target_speed=50.0,
            route_waypoints=[
                Waypoint(location=Vector3D(x=200.0, y=50.0, z=0.5), speed=50.0),
                Waypoint(location=Vector3D(x=300.0, y=50.0, z=0.5), speed=50.0),
            ]
        ),
        npc_actors=[
            NPCActorConfig(
                actor_id="npc_vehicle_01",
                actor_type=ActorType.VEHICLE.value,
                blueprint="vehicle.audi.a2",
                spawn_point=Transform(
                    location=Vector3D(x=150.0, y=50.0, z=0.5),
                    rotation=Vector3D(x=0.0, y=0.0, z=0.0)
                ),
                route_waypoints=[
                    Waypoint(location=Vector3D(x=250.0, y=50.0, z=0.5), speed=30.0),
                    Waypoint(location=Vector3D(x=350.0, y=50.0, z=0.5), speed=30.0),
                ],
                behavior="normal"
            )
        ],
        weather=WeatherConfig(preset=WeatherPreset.CLEAR_NOON.value),
        time=TimeConfig(hour=12, minute=0)
    )
    ScenarioIO.save_scenario(scenario1, os.path.join(scenarios_dir, "example_basic.json"))

    # Örnek 2: Kavşak senaryosu
    scenario2 = ScenarioConfig(
        name="Kavşak Geçiş Testi",
        description="Sağdan gelen araç ile kavşak senaryosu",
        carla_map="Town03",
        duration=90.0,
        ego_vehicle=EgoVehicleConfig(
            blueprint="vehicle.tesla.model3",
            spawn_point=Transform(
                location=Vector3D(x=0.0, y=0.0, z=0.5),
                rotation=Vector3D(x=0.0, y=90.0, z=0.0)
            ),
            target_speed=30.0,
            route_waypoints=[
                Waypoint(location=Vector3D(x=0.0, y=50.0, z=0.5), speed=30.0),
            ]
        ),
        npc_actors=[
            NPCActorConfig(
                actor_id="npc_vehicle_right",
                actor_type=ActorType.VEHICLE.value,
                blueprint="vehicle.bmw.grandtourer",
                spawn_point=Transform(
                    location=Vector3D(x=30.0, y=25.0, z=0.5),
                    rotation=Vector3D(x=0.0, y=180.0, z=0.0)
                ),
                route_waypoints=[
                    Waypoint(location=Vector3D(x=-20.0, y=25.0, z=0.5), speed=40.0),
                ],
                behavior="normal"
            )
        ],
        weather=WeatherConfig(preset=WeatherPreset.CLOUDY_NOON.value),
        time=TimeConfig(hour=14, minute=30)
    )
    ScenarioIO.save_scenario(scenario2, os.path.join(scenarios_dir, "example_intersection.json"))

    # Örnek 3: Yaya geçidi senaryosu
    scenario3 = ScenarioConfig(
        name="Yaya Geçidi Testi",
        description="Karşıdan karşıya geçen yayalar ile test senaryosu",
        carla_map="Town02",
        duration=60.0,
        ego_vehicle=EgoVehicleConfig(
            blueprint="vehicle.audi.tt",
            spawn_point=Transform(
                location=Vector3D(x=0.0, y=0.0, z=0.5),
                rotation=Vector3D(x=0.0, y=0.0, z=0.0)
            ),
            target_speed=40.0,
            route_waypoints=[
                Waypoint(location=Vector3D(x=100.0, y=0.0, z=0.5), speed=40.0),
            ]
        ),
        npc_actors=[
            NPCActorConfig(
                actor_id="pedestrian_01",
                actor_type=ActorType.PEDESTRIAN.value,
                blueprint="walker.pedestrian.0001",
                spawn_point=Transform(
                    location=Vector3D(x=50.0, y=-5.0, z=0.5),
                    rotation=Vector3D(x=0.0, y=90.0, z=0.0)
                ),
                route_waypoints=[
                    Waypoint(location=Vector3D(x=50.0, y=5.0, z=0.5), speed=5.0),
                ],
                behavior="normal"
            ),
            NPCActorConfig(
                actor_id="pedestrian_02",
                actor_type=ActorType.PEDESTRIAN.value,
                blueprint="walker.pedestrian.0002",
                spawn_point=Transform(
                    location=Vector3D(x=50.0, y=-6.0, z=0.5),
                    rotation=Vector3D(x=0.0, y=90.0, z=0.0)
                ),
                route_waypoints=[
                    Waypoint(location=Vector3D(x=50.0, y=6.0, z=0.5), speed=4.5, wait_time=2.0),
                ],
                behavior="cautious"
            )
        ],
        weather=WeatherConfig(preset=WeatherPreset.CLEAR_NOON.value),
        time=TimeConfig(hour=10, minute=0)
    )
    ScenarioIO.save_scenario(scenario3, os.path.join(scenarios_dir, "example_pedestrian.json"))

    print(f"3 örnek senaryo oluşturuldu: {scenarios_dir}/")


if __name__ == "__main__":
    # Örnek senaryolar oluştur
    create_example_scenarios()

    # Test: Senaryoyu yükle ve özet yazdır
    scenario = ScenarioIO.load_scenario("scenarios/example_basic.json")
    if scenario:
        print("\n" + ScenarioIO.export_scenario_summary(scenario))

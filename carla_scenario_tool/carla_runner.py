#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARLA Senaryo Çalıştırıcı
JSON senaryo dosyasını CARLA simülatöründe çalıştırır
Python 3.7+ uyumlu
"""

import sys
import os
import time
import argparse
import random
from typing import List, Optional

try:
    import carla
except ImportError:
    print("HATA: CARLA Python API bulunamadı!")
    print("CARLA kurulumundan sonra PythonAPI/carla dizinini PYTHONPATH'e ekleyin:")
    print("  export PYTHONPATH=$PYTHONPATH:/path/to/CARLA/PythonAPI/carla")
    print("  export PYTHONPATH=$PYTHONPATH:/path/to/CARLA/PythonAPI/carla/dist/carla-*-py3.7-linux-x86_64.egg")
    sys.exit(1)

from scenario_config import (
    ScenarioConfig, WeatherPreset, ActorType
)
from scenario_io import ScenarioIO


class CarlaScenarioRunner:
    """CARLA senaryolarını çalıştıran sınıf"""

    def __init__(self, host='localhost', port=2000, timeout=10.0):
        """
        Args:
            host: CARLA sunucu IP
            port: CARLA sunucu port (varsayılan 2000)
            timeout: Bağlantı timeout süresi
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        self.client = None
        self.world = None
        self.ego_vehicle = None
        self.npc_actors = []
        self.npc_controllers = []

    def connect(self):
        """CARLA sunucusuna bağlan"""
        try:
            print(f"CARLA sunucusuna bağlanılıyor: {self.host}:{self.port}")
            self.client = carla.Client(self.host, self.port)
            self.client.set_timeout(self.timeout)

            # Sunucu versiyonunu kontrol et
            version = self.client.get_client_version()
            server_version = self.client.get_server_version()
            print(f"CARLA Client: {version}, Server: {server_version}")

            self.world = self.client.get_world()
            print("CARLA'ya başarıyla bağlandı")
            return True

        except Exception as e:
            print(f"CARLA bağlantı hatası: {e}")
            print("\nKontrol edilmesi gerekenler:")
            print("1. CARLA sunucusu çalışıyor mu? (./CarlaUE4.sh)")
            print("2. Host ve port doğru mu?")
            print("3. Firewall CARLA portunu engelliyor mu?")
            return False

    def load_map(self, map_name: str):
        """Haritayı yükle"""
        try:
            print(f"Harita yükleniyor: {map_name}")
            self.world = self.client.load_world(map_name)
            time.sleep(2)  # Harita yüklenirken bekle
            print(f"Harita yüklendi: {map_name}")
            return True
        except Exception as e:
            print(f"Harita yükleme hatası: {e}")
            return False

    def set_weather(self, weather_config):
        """Hava durumunu ayarla"""
        try:
            weather = carla.WeatherParameters()

            # Preset kullan
            if weather_config.preset != WeatherPreset.CUSTOM.value:
                preset_map = {
                    WeatherPreset.CLEAR_NOON.value: carla.WeatherParameters.ClearNoon,
                    WeatherPreset.CLEAR_SUNSET.value: carla.WeatherParameters.ClearSunset,
                    WeatherPreset.CLOUDY_NOON.value: carla.WeatherParameters.CloudyNoon,
                    WeatherPreset.CLOUDY_SUNSET.value: carla.WeatherParameters.CloudySunset,
                    WeatherPreset.WET_NOON.value: carla.WeatherParameters.WetNoon,
                    WeatherPreset.WET_SUNSET.value: carla.WeatherParameters.WetSunset,
                    WeatherPreset.WET_CLOUDY_NOON.value: carla.WeatherParameters.WetCloudyNoon,
                    WeatherPreset.WET_CLOUDY_SUNSET.value: carla.WeatherParameters.WetCloudySunset,
                    WeatherPreset.SOFT_RAIN_NOON.value: carla.WeatherParameters.SoftRainNoon,
                    WeatherPreset.SOFT_RAIN_SUNSET.value: carla.WeatherParameters.SoftRainSunset,
                    WeatherPreset.MID_RAIN_NOON.value: carla.WeatherParameters.MidRainyNoon,
                    WeatherPreset.MID_RAIN_SUNSET.value: carla.WeatherParameters.MidRainSunset,
                    WeatherPreset.HARD_RAIN_NOON.value: carla.WeatherParameters.HardRainNoon,
                    WeatherPreset.HARD_RAIN_SUNSET.value: carla.WeatherParameters.HardRainSunset,
                }
                weather = preset_map.get(weather_config.preset, carla.WeatherParameters.ClearNoon)
            else:
                # Custom ayarlar
                weather.cloudiness = weather_config.cloudiness
                weather.precipitation = weather_config.precipitation
                weather.precipitation_deposits = weather_config.precipitation_deposits
                weather.wind_intensity = weather_config.wind_intensity
                weather.sun_azimuth_angle = weather_config.sun_azimuth_angle
                weather.sun_altitude_angle = weather_config.sun_altitude_angle
                weather.fog_density = weather_config.fog_density
                weather.fog_distance = weather_config.fog_distance
                weather.fog_falloff = weather_config.fog_falloff
                weather.wetness = weather_config.wetness

            self.world.set_weather(weather)
            print(f"Hava durumu ayarlandı: {weather_config.preset}")

        except Exception as e:
            print(f"Hava durumu ayarlama hatası: {e}")

    def spawn_ego_vehicle(self, ego_config):
        """Ego vehicle (test aracı) spawn et"""
        try:
            blueprint_library = self.world.get_blueprint_library()
            vehicle_bp = blueprint_library.filter(ego_config.blueprint)[0]

            # Spawn transform
            spawn_transform = carla.Transform(
                carla.Location(
                    x=ego_config.spawn_point.location.x,
                    y=ego_config.spawn_point.location.y,
                    z=ego_config.spawn_point.location.z
                ),
                carla.Rotation(
                    pitch=ego_config.spawn_point.rotation.x,
                    yaw=ego_config.spawn_point.rotation.y,
                    roll=ego_config.spawn_point.rotation.z
                )
            )

            # Spawn
            self.ego_vehicle = self.world.spawn_actor(vehicle_bp, spawn_transform)
            print(f"Ego vehicle spawn edildi: {ego_config.blueprint}")

            # Autopilot aktif ise
            if ego_config.enable_autopilot:
                self.ego_vehicle.set_autopilot(True)
                print("Ego vehicle autopilot aktif")

            return True

        except Exception as e:
            print(f"Ego vehicle spawn hatası: {e}")
            return False

    def spawn_npc_actors(self, npc_configs):
        """NPC aktörleri spawn et"""
        blueprint_library = self.world.get_blueprint_library()

        for npc_config in npc_configs:
            try:
                # Blueprint seç
                if npc_config.actor_type == ActorType.VEHICLE.value:
                    bp = blueprint_library.filter(npc_config.blueprint)[0]
                else:  # Pedestrian
                    bp = blueprint_library.filter(npc_config.blueprint)[0]

                # Spawn transform
                spawn_transform = carla.Transform(
                    carla.Location(
                        x=npc_config.spawn_point.location.x,
                        y=npc_config.spawn_point.location.y,
                        z=npc_config.spawn_point.location.z
                    ),
                    carla.Rotation(
                        pitch=npc_config.spawn_point.rotation.x,
                        yaw=npc_config.spawn_point.rotation.y,
                        roll=npc_config.spawn_point.rotation.z
                    )
                )

                # Spawn
                actor = self.world.spawn_actor(bp, spawn_transform)
                self.npc_actors.append({
                    'actor': actor,
                    'config': npc_config,
                    'waypoint_index': 0
                })

                print(f"NPC spawn edildi: {npc_config.actor_id} ({npc_config.actor_type})")

                # Yaya ise controller ekle
                if npc_config.actor_type == ActorType.PEDESTRIAN.value:
                    walker_controller_bp = blueprint_library.find('controller.ai.walker')
                    controller = self.world.spawn_actor(walker_controller_bp, carla.Transform(), actor)
                    controller.start()
                    self.npc_controllers.append(controller)

                    # İlk waypoint'e git
                    if npc_config.route_waypoints:
                        first_wp = npc_config.route_waypoints[0]
                        controller.go_to_location(carla.Location(
                            x=first_wp.location.x,
                            y=first_wp.location.y,
                            z=first_wp.location.z
                        ))
                        controller.set_max_speed(first_wp.speed / 3.6)  # km/h -> m/s

                # Araç ise autopilot veya waypoint kontrolü
                elif npc_config.actor_type == ActorType.VEHICLE.value:
                    if npc_config.behavior == "stopped":
                        # Durmuş araç
                        pass
                    elif not npc_config.route_waypoints:
                        # Waypoint yoksa autopilot
                        actor.set_autopilot(True)
                    # Waypoint varsa manuel kontrol (update loop'ta)

            except Exception as e:
                print(f"NPC spawn hatası ({npc_config.actor_id}): {e}")

    def update_npc_vehicles(self):
        """NPC araçları waypoint'lere göre güncelle (basit kontrol)"""
        for npc_data in self.npc_actors:
            actor = npc_data['actor']
            config = npc_data['config']

            # Sadece araçlar için
            if config.actor_type != ActorType.VEHICLE.value:
                continue

            # Waypoint yoksa skip
            if not config.route_waypoints:
                continue

            # Waypoint kontrolü
            wp_index = npc_data['waypoint_index']
            if wp_index >= len(config.route_waypoints):
                # Rota bitti
                if config.auto_destroy:
                    actor.destroy()
                    self.npc_actors.remove(npc_data)
                continue

            waypoint = config.route_waypoints[wp_index]
            target_location = carla.Location(
                x=waypoint.location.x,
                y=waypoint.location.y,
                z=waypoint.location.z
            )

            # Mevcut konum
            current_location = actor.get_location()
            distance = current_location.distance(target_location)

            # Waypoint'e ulaşıldı mı?
            if distance < 5.0:  # 5 metre tolerance
                npc_data['waypoint_index'] += 1
                print(f"{config.actor_id} waypoint #{wp_index+1}'e ulaştı")
            else:
                # Basit yönlendirme (gerçek uygulamada PID kontrol kullanılmalı)
                direction = target_location - current_location
                direction.z = 0
                rotation = actor.get_transform().rotation
                rotation.yaw = direction.get_vector_angle()

                # Hız kontrolü (basitleştirilmiş)
                target_speed = waypoint.speed / 3.6  # km/h -> m/s
                actor.enable_constant_velocity(carla.Vector3D(
                    x=direction.x * target_speed / distance,
                    y=direction.y * target_speed / distance,
                    z=0
                ))

    def run_scenario(self, scenario: ScenarioConfig):
        """Senaryoyu çalıştır"""
        print("\n" + "="*60)
        print(f"SENARYO BAŞLIYOR: {scenario.name}")
        print("="*60)
        print(f"Açıklama: {scenario.description}")
        print(f"Harita: {scenario.carla_map}")
        print(f"Süre: {scenario.duration} saniye")
        print("="*60 + "\n")

        # CARLA'ya bağlan
        if not self.connect():
            return False

        # Haritayı yükle
        if not self.load_map(scenario.carla_map):
            return False

        # Hava durumunu ayarla
        self.set_weather(scenario.weather)

        # Ego vehicle spawn et
        if not self.spawn_ego_vehicle(scenario.ego_vehicle):
            print("Ego vehicle spawn edilemedi!")
            return False

        # NPC'leri spawn et
        self.spawn_npc_actors(scenario.npc_actors)

        # Spectator'ı ego vehicle'a ayarla
        if self.ego_vehicle:
            spectator = self.world.get_spectator()
            ego_transform = self.ego_vehicle.get_transform()
            spectator.set_transform(carla.Transform(
                ego_transform.location + carla.Location(z=50),
                carla.Rotation(pitch=-90)
            ))

        print("\n" + "="*60)
        print("SENARYO ÇALIŞIYOR")
        print("Durdurmak için Ctrl+C'ye basın")
        print("="*60 + "\n")

        # Ana loop
        start_time = time.time()
        try:
            while True:
                # Süre kontrolü
                elapsed_time = time.time() - start_time
                if scenario.duration > 0 and elapsed_time >= scenario.duration:
                    print(f"\nSenaryo süresi doldu ({scenario.duration} saniye)")
                    break

                # NPC'leri güncelle
                self.update_npc_vehicles()

                # Spectator'ı güncelle (ego vehicle'ı takip et)
                if self.ego_vehicle:
                    spectator = self.world.get_spectator()
                    ego_transform = self.ego_vehicle.get_transform()
                    spectator.set_transform(carla.Transform(
                        ego_transform.location + carla.Location(z=20, x=-10),
                        carla.Rotation(pitch=-30, yaw=ego_transform.rotation.yaw)
                    ))

                # Dünya güncelleme
                self.world.tick()
                time.sleep(0.05)  # 20 FPS

        except KeyboardInterrupt:
            print("\n\nSenaryo kullanıcı tarafından durduruldu (Ctrl+C)")

        print("\n" + "="*60)
        print("SENARYO TAMAMLANDI")
        print("="*60)

        return True

    def cleanup(self):
        """Aktörleri temizle"""
        print("\nTemizleniyor...")

        # NPC controller'ları durdur
        for controller in self.npc_controllers:
            try:
                controller.stop()
                controller.destroy()
            except:
                pass

        # NPC aktörleri yok et
        for npc_data in self.npc_actors:
            try:
                npc_data['actor'].destroy()
            except:
                pass

        # Ego vehicle'ı yok et
        if self.ego_vehicle:
            try:
                self.ego_vehicle.destroy()
            except:
                pass

        print("Temizleme tamamlandı")


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="CARLA Senaryo Çalıştırıcı")
    parser.add_argument("scenario_file", help="Senaryo JSON dosyası")
    parser.add_argument("--host", default="localhost", help="CARLA sunucu IP (varsayılan: localhost)")
    parser.add_argument("--port", type=int, default=2000, help="CARLA sunucu port (varsayılan: 2000)")

    args = parser.parse_args()

    # Senaryo dosyasını kontrol et
    if not os.path.exists(args.scenario_file):
        print(f"HATA: Senaryo dosyası bulunamadı: {args.scenario_file}")
        sys.exit(1)

    # Senaryoyu yükle
    print(f"Senaryo yükleniyor: {args.scenario_file}")
    scenario = ScenarioIO.load_scenario(args.scenario_file)

    if not scenario:
        print("HATA: Senaryo yüklenemedi!")
        sys.exit(1)

    # Senaryo geçerliliğini kontrol et
    valid, errors = scenario.validate()
    if not valid:
        print("\nHATA: Senaryo geçerli değil!")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    # Senaryo özeti
    print("\n" + ScenarioIO.export_scenario_summary(scenario))

    # Runner oluştur
    runner = CarlaScenarioRunner(host=args.host, port=args.port)

    try:
        # Senaryoyu çalıştır
        success = runner.run_scenario(scenario)
        sys.exit(0 if success else 1)

    finally:
        # Her durumda temizle
        runner.cleanup()


if __name__ == "__main__":
    main()

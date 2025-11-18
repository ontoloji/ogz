#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CARLA Senaryo Konfigürasyon Modülü
Otonom araç test senaryolarının veri yapılarını tanımlar.
Python 3.7+ uyumlu
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class ActorType(Enum):
    """Aktör tipi enum"""
    VEHICLE = "vehicle"
    PEDESTRIAN = "pedestrian"


class WeatherPreset(Enum):
    """Hava durumu ön ayarları"""
    CLEAR_NOON = "clear_noon"
    CLEAR_SUNSET = "clear_sunset"
    CLOUDY_NOON = "cloudy_noon"
    CLOUDY_SUNSET = "cloudy_sunset"
    WET_NOON = "wet_noon"
    WET_SUNSET = "wet_sunset"
    WET_CLOUDY_NOON = "wet_cloudy_noon"
    WET_CLOUDY_SUNSET = "wet_cloudy_sunset"
    SOFT_RAIN_NOON = "soft_rain_noon"
    SOFT_RAIN_SUNSET = "soft_rain_sunset"
    MID_RAIN_NOON = "mid_rain_noon"
    MID_RAIN_SUNSET = "mid_rain_sunset"
    HARD_RAIN_NOON = "hard_rain_noon"
    HARD_RAIN_SUNSET = "hard_rain_sunset"
    CUSTOM = "custom"


@dataclass
class Vector3D:
    """3D vektör (konum, rotasyon vb. için)"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z}

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Vector3D':
        return cls(x=data.get("x", 0.0), y=data.get("y", 0.0), z=data.get("z", 0.0))


@dataclass
class Transform:
    """Konum ve rotasyon bilgisi"""
    location: Vector3D = field(default_factory=Vector3D)
    rotation: Vector3D = field(default_factory=Vector3D)  # pitch, yaw, roll

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "rotation": self.rotation.to_dict()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transform':
        return cls(
            location=Vector3D.from_dict(data.get("location", {})),
            rotation=Vector3D.from_dict(data.get("rotation", {}))
        )


@dataclass
class Waypoint:
    """Hareket rotası için waypoint"""
    location: Vector3D = field(default_factory=Vector3D)
    speed: float = 30.0  # km/h
    wait_time: float = 0.0  # saniye, bu noktada bekleme süresi

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location.to_dict(),
            "speed": self.speed,
            "wait_time": self.wait_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Waypoint':
        return cls(
            location=Vector3D.from_dict(data.get("location", {})),
            speed=data.get("speed", 30.0),
            wait_time=data.get("wait_time", 0.0)
        )


@dataclass
class EgoVehicleConfig:
    """Ego Vehicle (Test edilen otonom araç) konfigürasyonu"""
    blueprint: str = "vehicle.tesla.model3"  # CARLA blueprint ID
    spawn_point: Transform = field(default_factory=Transform)
    initial_speed: float = 0.0  # km/h
    target_speed: float = 50.0  # km/h
    route_waypoints: List[Waypoint] = field(default_factory=list)
    enable_autopilot: bool = False  # CARLA'nın kendi autopilot'u
    enable_sensors: bool = True  # Kamera, LiDAR vb. sensörler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint": self.blueprint,
            "spawn_point": self.spawn_point.to_dict(),
            "initial_speed": self.initial_speed,
            "target_speed": self.target_speed,
            "route_waypoints": [wp.to_dict() for wp in self.route_waypoints],
            "enable_autopilot": self.enable_autopilot,
            "enable_sensors": self.enable_sensors
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EgoVehicleConfig':
        return cls(
            blueprint=data.get("blueprint", "vehicle.tesla.model3"),
            spawn_point=Transform.from_dict(data.get("spawn_point", {})),
            initial_speed=data.get("initial_speed", 0.0),
            target_speed=data.get("target_speed", 50.0),
            route_waypoints=[Waypoint.from_dict(wp) for wp in data.get("route_waypoints", [])],
            enable_autopilot=data.get("enable_autopilot", False),
            enable_sensors=data.get("enable_sensors", True)
        )


@dataclass
class NPCActorConfig:
    """NPC (Hedef araç veya yaya) konfigürasyonu"""
    actor_id: str = ""  # Benzersiz ID
    actor_type: str = ActorType.VEHICLE.value
    blueprint: str = "vehicle.audi.a2"  # CARLA blueprint ID
    spawn_point: Transform = field(default_factory=Transform)
    route_waypoints: List[Waypoint] = field(default_factory=list)
    behavior: str = "normal"  # normal, aggressive, cautious, stopped
    auto_destroy: bool = True  # Rota bitince yok edilsin mi?

    def to_dict(self) -> Dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "blueprint": self.blueprint,
            "spawn_point": self.spawn_point.to_dict(),
            "route_waypoints": [wp.to_dict() for wp in self.route_waypoints],
            "behavior": self.behavior,
            "auto_destroy": self.auto_destroy
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NPCActorConfig':
        return cls(
            actor_id=data.get("actor_id", ""),
            actor_type=data.get("actor_type", ActorType.VEHICLE.value),
            blueprint=data.get("blueprint", "vehicle.audi.a2"),
            spawn_point=Transform.from_dict(data.get("spawn_point", {})),
            route_waypoints=[Waypoint.from_dict(wp) for wp in data.get("route_waypoints", [])],
            behavior=data.get("behavior", "normal"),
            auto_destroy=data.get("auto_destroy", True)
        )


@dataclass
class WeatherConfig:
    """Hava durumu konfigürasyonu"""
    preset: str = WeatherPreset.CLEAR_NOON.value
    # Özel (custom) ayarlar
    cloudiness: float = 0.0  # 0-100
    precipitation: float = 0.0  # 0-100 (yağmur)
    precipitation_deposits: float = 0.0  # 0-100 (yerdeki su birikintileri)
    wind_intensity: float = 0.0  # 0-100
    sun_azimuth_angle: float = 0.0  # 0-360 derece
    sun_altitude_angle: float = 75.0  # -90 to 90 derece
    fog_density: float = 0.0  # 0-100
    fog_distance: float = 0.0  # metre
    fog_falloff: float = 0.0
    wetness: float = 0.0  # 0-100 (yol ıslaklığı)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherConfig':
        return cls(**{k: data.get(k, getattr(cls(), k)) for k in data})


@dataclass
class TimeConfig:
    """Zaman konfigürasyonu (gündüz/gece)"""
    hour: int = 12  # 0-23
    minute: int = 0  # 0-59

    def to_dict(self) -> Dict[str, int]:
        return {"hour": self.hour, "minute": self.minute}

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'TimeConfig':
        return cls(hour=data.get("hour", 12), minute=data.get("minute", 0))


@dataclass
class ScenarioConfig:
    """Tam senaryo konfigürasyonu"""
    name: str = "Untitled Scenario"
    description: str = ""
    carla_map: str = "Town01"  # CARLA harita adı
    ego_vehicle: EgoVehicleConfig = field(default_factory=EgoVehicleConfig)
    npc_actors: List[NPCActorConfig] = field(default_factory=list)
    weather: WeatherConfig = field(default_factory=WeatherConfig)
    time: TimeConfig = field(default_factory=TimeConfig)
    duration: float = 60.0  # Senaryo maksimum süresi (saniye), 0 = sınırsız

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "carla_map": self.carla_map,
            "ego_vehicle": self.ego_vehicle.to_dict(),
            "npc_actors": [actor.to_dict() for actor in self.npc_actors],
            "weather": self.weather.to_dict(),
            "time": self.time.to_dict(),
            "duration": self.duration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScenarioConfig':
        return cls(
            name=data.get("name", "Untitled Scenario"),
            description=data.get("description", ""),
            carla_map=data.get("carla_map", "Town01"),
            ego_vehicle=EgoVehicleConfig.from_dict(data.get("ego_vehicle", {})),
            npc_actors=[NPCActorConfig.from_dict(actor) for actor in data.get("npc_actors", [])],
            weather=WeatherConfig.from_dict(data.get("weather", {})),
            time=TimeConfig.from_dict(data.get("time", {})),
            duration=data.get("duration", 60.0)
        )

    def validate(self) -> Tuple[bool, List[str]]:
        """Senaryo geçerliliğini kontrol et"""
        errors = []

        if not self.name or self.name.strip() == "":
            errors.append("Senaryo adı boş olamaz")

        if not self.carla_map or self.carla_map.strip() == "":
            errors.append("CARLA harita seçilmeli")

        if not self.ego_vehicle.blueprint:
            errors.append("Ego vehicle blueprint seçilmeli")

        # NPC ID'leri benzersiz olmalı
        npc_ids = [npc.actor_id for npc in self.npc_actors if npc.actor_id]
        if len(npc_ids) != len(set(npc_ids)):
            errors.append("NPC aktör ID'leri benzersiz olmalı")

        return len(errors) == 0, errors


# Örnek CARLA blueprintleri (kullanıcıya seçim için)
VEHICLE_BLUEPRINTS = [
    "vehicle.audi.a2",
    "vehicle.audi.tt",
    "vehicle.bmw.grandtourer",
    "vehicle.chevrolet.impala",
    "vehicle.citroen.c3",
    "vehicle.dodge.charger_police",
    "vehicle.ford.mustang",
    "vehicle.jeep.wrangler_rubicon",
    "vehicle.mercedes.coupe",
    "vehicle.mini.cooper_s",
    "vehicle.nissan.micra",
    "vehicle.nissan.patrol",
    "vehicle.tesla.model3",
    "vehicle.toyota.prius",
    "vehicle.volkswagen.t2",
]

PEDESTRIAN_BLUEPRINTS = [
    "walker.pedestrian.0001",
    "walker.pedestrian.0002",
    "walker.pedestrian.0003",
    "walker.pedestrian.0004",
    "walker.pedestrian.0005",
    "walker.pedestrian.0006",
    "walker.pedestrian.0007",
    "walker.pedestrian.0008",
    "walker.pedestrian.0009",
    "walker.pedestrian.0010",
]

CARLA_MAPS = [
    "Town01",
    "Town02",
    "Town03",
    "Town04",
    "Town05",
    "Town06",
    "Town07",
    "Town10HD",
]

BEHAVIOR_TYPES = [
    "normal",
    "aggressive",
    "cautious",
    "stopped",
]

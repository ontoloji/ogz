"""
SORT Test Otomasyon Sistemi - SORT Test Profilleri
UITP SORT 1, 2, 3 test profil tanımları
"""

from dataclasses import dataclass
from typing import List, Tuple
from utils import SegmentType


@dataclass
class Segment:
    """Test segmenti"""
    segment_id: int
    segment_type: str  # ACCEL, CONSTANT, BRAKE, WAIT
    start_distance: float  # metre
    end_distance: float  # metre
    target_speed: float  # km/h
    wait_time: float = 0.0  # saniye (sadece WAIT segmentleri için)
    brake_tolerance: float = 5.0  # metre (frenleme toleransı)

    @property
    def distance(self) -> float:
        """Segment mesafesi"""
        return self.end_distance - self.start_distance

    @property
    def description(self) -> str:
        """Segment açıklaması"""
        if self.segment_type == SegmentType.ACCEL:
            return f"Hızlanma {self.target_speed:.0f} km/h"
        elif self.segment_type == SegmentType.CONSTANT:
            return f"Sabit {self.target_speed:.0f} km/h"
        elif self.segment_type == SegmentType.BRAKE:
            return "Frenleme (sürücü)"
        elif self.segment_type == SegmentType.WAIT:
            return f"Bekleme {self.wait_time:.0f} saniye"
        else:
            return "Hazır"


class SORTProfile:
    """SORT test profili"""

    def __init__(self, profile_type: int):
        self.profile_type = profile_type
        self.segments = self._create_segments()
        self.total_distance = self.segments[-1].end_distance if self.segments else 0.0

    def _create_segments(self) -> List[Segment]:
        """Profil tipine göre segment listesi oluştur"""
        if self.profile_type == 1:
            return self._create_sort1_segments()
        elif self.profile_type == 2:
            return self._create_sort2_segments()
        elif self.profile_type == 3:
            return self._create_sort3_segments()
        else:
            raise ValueError(f"Geçersiz profil tipi: {self.profile_type}")

    def _create_sort1_segments(self) -> List[Segment]:
        """
        SORT 1 profili (Toplam: 1040m)
        3 hız seviyesi: 20, 30, 40 km/h
        Her hız seviyesi 2 kez tekrarlanır
        """
        segments = []
        seg_id = 1

        # İlk tur: 20-30-40 km/h
        # 20 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 0, 15, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 15, 80.7, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 80.7, 100, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 100, 100, 0, wait_time=20))
        seg_id += 1

        # 30 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 100, 145, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 145, 256.6, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 256.6, 300, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 300, 300, 0, wait_time=20))
        seg_id += 1

        # 40 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 300, 400, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 400, 442.8, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 442.8, 520, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 520, 520, 0, wait_time=20))
        seg_id += 1

        # İkinci tur: 20-30-40 km/h
        # 20 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 520, 535, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 535, 600.7, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 600.7, 620, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 620, 620, 0, wait_time=20))
        seg_id += 1

        # 30 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 620, 665, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 665, 776.6, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 776.6, 820, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 820, 820, 0, wait_time=20))
        seg_id += 1

        # 40 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 820, 920, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 920, 962.8, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 962.8, 1040, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 1040, 1040, 0, wait_time=20))

        return segments

    def _create_sort2_segments(self) -> List[Segment]:
        """
        SORT 2 profili (Toplam: 920m)
        3 hız seviyesi: 20, 40, 50 km/h
        """
        segments = []
        seg_id = 1

        # 20 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 0, 15, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 15, 80.7, 20))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 80.7, 100, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 100, 100, 0, wait_time=20))
        seg_id += 1

        # 40 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 100, 200, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 200, 242.8, 40))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 242.8, 320, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 320, 320, 0, wait_time=20))
        seg_id += 1

        # 50 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 320, 490, 50))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 490, 799.4, 50))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 799.4, 920, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 920, 920, 0, wait_time=20))

        return segments

    def _create_sort3_segments(self) -> List[Segment]:
        """
        SORT 3 profili (Toplam: 1450m)
        3 hız seviyesi: 30, 50, 60 km/h
        Son iki bekleme süresi 10 saniye
        """
        segments = []
        seg_id = 1

        # 30 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 0, 45, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 45, 156.6, 30))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 156.6, 200, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 200, 200, 0, wait_time=20))
        seg_id += 1

        # 50 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 200, 370, 50))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 370, 679.4, 50))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 679.4, 800, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 800, 800, 0, wait_time=10))
        seg_id += 1

        # 60 km/h
        segments.append(Segment(seg_id, SegmentType.ACCEL, 800, 1100, 60))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.CONSTANT, 1100, 1276.4, 60))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.BRAKE, 1276.4, 1450, 0))
        seg_id += 1
        segments.append(Segment(seg_id, SegmentType.WAIT, 1450, 1450, 0, wait_time=10))

        return segments

    def get_current_segment(self, distance: float) -> Tuple[Segment, int]:
        """
        Mevcut mesafeye göre aktif segmenti bul
        Returns: (segment, index)
        """
        for idx, segment in enumerate(self.segments):
            if segment.start_distance <= distance < segment.end_distance:
                return segment, idx
            # WAIT segmenti için özel kontrol
            elif segment.segment_type == SegmentType.WAIT and distance >= segment.start_distance:
                # Bir sonraki segment varsa ve mesafe henüz başlamamışsa
                if idx + 1 < len(self.segments):
                    next_segment = self.segments[idx + 1]
                    if distance < next_segment.start_distance:
                        return segment, idx
                else:
                    # Son segment
                    return segment, idx

        # Test tamamlandı veya henüz başlamadı
        if distance >= self.total_distance and self.segments:
            return self.segments[-1], len(self.segments) - 1
        elif self.segments:
            return self.segments[0], 0

        return None, -1

    def get_segment_progress(self, distance: float, segment: Segment) -> float:
        """Segment içindeki ilerleme yüzdesini hesapla (0-100)"""
        if segment.distance == 0:
            return 100.0

        progress = ((distance - segment.start_distance) / segment.distance) * 100.0
        return max(0.0, min(100.0, progress))

    def is_test_completed(self, distance: float) -> bool:
        """Test tamamlandı mı?"""
        return distance >= self.total_distance

    def get_profile_name(self) -> str:
        """Profil adını al"""
        return f"SORT {self.profile_type}"

    def get_profile_summary(self) -> str:
        """Profil özetini al"""
        speed_levels = set()
        for segment in self.segments:
            if segment.segment_type in [SegmentType.ACCEL, SegmentType.CONSTANT]:
                speed_levels.add(segment.target_speed)

        speed_list = sorted(speed_levels)
        speed_str = "-".join([f"{int(s)}" for s in speed_list])

        return f"SORT {self.profile_type} ({speed_str} km/h, {self.total_distance:.0f}m)"


if __name__ == "__main__":
    # Test
    for profile_type in [1, 2, 3]:
        profile = SORTProfile(profile_type)
        print(f"\n{'='*60}")
        print(f"{profile.get_profile_summary()}")
        print(f"{'='*60}")
        print(f"Toplam segment sayısı: {len(profile.segments)}")
        print(f"\nSegmentler:")

        for idx, segment in enumerate(profile.segments, 1):
            print(f"{idx:2d}. {segment.start_distance:7.1f}-{segment.end_distance:7.1f}m "
                  f"({segment.distance:6.1f}m) - {segment.description}")

        # Test belirli mesafelerde
        print(f"\nMesafe testleri:")
        test_distances = [0, 50, 100, 200, 500, profile.total_distance, profile.total_distance + 100]
        for dist in test_distances:
            segment, idx = profile.get_current_segment(dist)
            if segment:
                progress = profile.get_segment_progress(dist, segment)
                print(f"  {dist:6.1f}m -> Segment {idx+1}: {segment.description} ({progress:.0f}%)")

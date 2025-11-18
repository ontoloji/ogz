"""
CAN Bus Güvenlik Test - Örnek Kullanım Scriptleri

⚠️ Bu örnekler sadece yetkili güvenlik testleri için kullanılmalıdır.
"""

import sys
import time
import logging
from pathlib import Path

# Parent dizini path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from can_security_attacks import (
    CANSecurityTester, MockCANSecurityTester,
    AttackType, AttackConfig, CANLIB_AVAILABLE
)


def setup_logging():
    """Logging konfigürasyonu"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def example_1_id_scan():
    """
    Örnek 1: CAN ID Tarama
    Güvenli başlangıç - bus'taki aktif ID'leri keşfet
    """
    print("\n" + "="*60)
    print("Örnek 1: CAN ID Tarama")
    print("="*60)

    # Tester oluştur (gerçek veya mock)
    if CANLIB_AVAILABLE:
        tester = CANSecurityTester(channel=0, bitrate=500000)
    else:
        print("⚠️  Kvaser CANlib bulunamadı, Mock mode kullanılıyor")
        tester = MockCANSecurityTester(channel=0, bitrate=500000)

    # Status callback
    def status_update(status, data):
        print(f"📊 Durum: {status} - {data}")

    # Message callback
    message_count = 0

    def message_received(frame):
        nonlocal message_count
        message_count += 1
        if message_count % 100 == 0:
            print(f"📨 {message_count} mesaj alındı...")

    tester.set_status_callback(status_update)
    tester.set_message_callback(message_received)

    # Bağlan
    print("\n🔌 CAN bus'a bağlanıyor...")
    if not tester.connect():
        print("❌ Bağlantı başarısız!")
        return

    print("✅ Bağlantı başarılı!")

    # ID Scan konfigürasyonu
    config = AttackConfig(
        attack_type=AttackType.ID_SCAN,
        id_range_start=0x000,
        id_range_end=0x100,  # İlk 256 ID
        packet_rate=100,
        duration=5
    )

    # Saldırıyı başlat
    print(f"\n🚀 ID Scan başlatılıyor (0x000-0x100)...")
    tester.start_attack(config)

    # Bekle
    time.sleep(config.duration + 1)

    # İstatistikler
    stats = tester.get_statistics()
    print("\n📈 Test İstatistikleri:")
    print(f"  - Gönderilen paket: {stats['packets_sent']}")
    print(f"  - Alınan paket: {stats['packets_received']}")
    print(f"  - Hata sayısı: {stats['errors']}")

    # Temizle
    tester.disconnect()
    print("\n✅ Test tamamlandı!")


def example_2_fuzzing():
    """
    Örnek 2: Fuzzing Saldırısı
    Belirli ID aralığına rastgele mesajlar gönder
    """
    print("\n" + "="*60)
    print("Örnek 2: Fuzzing Saldırısı")
    print("="*60)

    # Tester oluştur
    if CANLIB_AVAILABLE:
        tester = CANSecurityTester(channel=0, bitrate=500000)
    else:
        print("⚠️  Mock mode")
        tester = MockCANSecurityTester(channel=0, bitrate=500000)

    # Bağlan
    print("\n🔌 Bağlanıyor...")
    if not tester.connect():
        print("❌ Bağlantı başarısız!")
        return

    # Fuzzing config
    config = AttackConfig(
        attack_type=AttackType.FUZZING,
        id_range_start=0x200,
        id_range_end=0x2FF,  # Body control range
        packet_rate=100,
        duration=10,
        data_length=8
    )

    # Onay iste
    print("\n⚠️  UYARI: Fuzzing saldırısı başlatılacak!")
    print(f"  - ID Aralığı: 0x{config.id_range_start:03X} - 0x{config.id_range_end:03X}")
    print(f"  - Paket Hızı: {config.packet_rate} pkt/s")
    print(f"  - Süre: {config.duration} saniye")
    print(f"  - Toplam paket: ~{config.packet_rate * config.duration}")

    response = input("\nDevam etmek istiyor musunuz? (evet/hayir): ")
    if response.lower() != "evet":
        print("❌ İptal edildi")
        tester.disconnect()
        return

    # Başlat
    print("\n🚀 Fuzzing başlatıldı...")
    tester.start_attack(config)

    # Progress göster
    for i in range(config.duration):
        time.sleep(1)
        stats = tester.get_statistics()
        print(f"⏱️  {i+1}/{config.duration}s - Gönderilen: {stats['packets_sent']}", end='\r')

    print()  # Newline

    # Sonuçlar
    stats = tester.get_statistics()
    print("\n📈 Test Sonuçları:")
    print(f"  - Toplam gönderilen: {stats['packets_sent']}")
    print(f"  - Hata: {stats['errors']}")
    print(f"  - Başarı oranı: {(stats['packets_sent']-stats['errors'])/stats['packets_sent']*100:.1f}%")

    tester.disconnect()
    print("\n✅ Test tamamlandı!")


def example_3_replay():
    """
    Örnek 3: Replay Attack
    Mesajları yakala ve tekrarla
    """
    print("\n" + "="*60)
    print("Örnek 3: Replay Attack")
    print("="*60)

    # Tester oluştur
    if CANLIB_AVAILABLE:
        tester = CANSecurityTester(channel=0, bitrate=500000)
    else:
        print("⚠️  Mock mode")
        tester = MockCANSecurityTester(channel=0, bitrate=500000)

    # Bağlan
    print("\n🔌 Bağlanıyor...")
    if not tester.connect():
        print("❌ Bağlantı başarısız!")
        return

    # PHASE 1: Mesaj yakalama
    print("\n📡 PHASE 1: Mesaj Yakalama")
    print("  İstediğiniz işlemi yapın (örn: kilit açma, motor çalıştırma)")
    print("  10 saniye içinde mesajlar yakalanacak...")

    tester.start_capture()

    # Countdown
    for i in range(10, 0, -1):
        print(f"  ⏱️  {i} saniye kaldı...", end='\r')
        time.sleep(1)

    print()  # Newline

    # Yakalamayı durdur
    captured = tester.stop_capture()
    print(f"\n✅ {len(captured)} mesaj yakalandı!")

    if len(captured) == 0:
        print("❌ Hiç mesaj yakalanamadı!")
        tester.disconnect()
        return

    # İlk 10 mesajı göster
    print("\n📋 Yakalanan mesajlar (ilk 10):")
    for i, (msg_id, data) in enumerate(captured[:10]):
        data_hex = ' '.join(f'{b:02X}' for b in data)
        print(f"  {i+1}. ID: 0x{msg_id:03X}, Data: {data_hex}")

    # PHASE 2: Replay
    print("\n🔄 PHASE 2: Replay Attack")
    print("  Yakalanan mesajlar tekrar gönderilecek!")

    response = input("\nDevam etmek istiyor musunuz? (evet/hayir): ")
    if response.lower() != "evet":
        print("❌ İptal edildi")
        tester.disconnect()
        return

    config = AttackConfig(
        attack_type=AttackType.REPLAY,
        replay_messages=captured,
        packet_rate=50,  # Orijinal hıza yakın
        duration=5
    )

    print("\n🚀 Replay başlatıldı...")
    tester.start_attack(config)

    time.sleep(config.duration + 1)

    # Sonuçlar
    stats = tester.get_statistics()
    print("\n📈 Replay İstatistikleri:")
    print(f"  - Replay edilen: {stats['packets_sent']}")
    print(f"  - Hata: {stats['errors']}")

    tester.disconnect()
    print("\n✅ Test tamamlandı!")


def example_4_diagnostic():
    """
    Örnek 4: Diagnostic Saldırısı
    UDS komutları gönder
    """
    print("\n" + "="*60)
    print("Örnek 4: Diagnostic Saldırısı (UDS)")
    print("="*60)

    # Tester oluştur
    if CANLIB_AVAILABLE:
        tester = CANSecurityTester(channel=0, bitrate=500000)
    else:
        print("⚠️  Mock mode")
        tester = MockCANSecurityTester(channel=0, bitrate=500000)

    # Bağlan
    print("\n🔌 Bağlanıyor...")
    if not tester.connect():
        print("❌ Bağlantı başarısız!")
        return

    # Diagnostic config
    config = AttackConfig(
        attack_type=AttackType.DIAGNOSTIC,
        diagnostic_target=0x7DF,  # OBD-II broadcast
        packet_rate=10,
        duration=15
    )

    print("\n🔍 Diagnostic Scan:")
    print(f"  - Hedef: 0x{config.diagnostic_target:03X} (OBD-II Broadcast)")
    print(f"  - Test edilecek UDS servisleri:")
    print("    • 0x10 - DiagnosticSessionControl")
    print("    • 0x11 - ECUReset")
    print("    • 0x22 - ReadDataByIdentifier")
    print("    • 0x27 - SecurityAccess")
    print("    • 0x2E - WriteDataByIdentifier")
    print("    • 0x3E - TesterPresent")

    response = input("\nDevam etmek istiyor musunuz? (evet/hayir): ")
    if response.lower() != "evet":
        print("❌ İptal edildi")
        tester.disconnect()
        return

    print("\n🚀 Diagnostic scan başlatıldı...")
    tester.start_attack(config)

    time.sleep(config.duration + 1)

    # Sonuçlar
    stats = tester.get_statistics()
    print("\n📈 Sonuçlar:")
    print(f"  - Gönderilen: {stats['packets_sent']}")
    print(f"  - Alınan yanıt: {stats['packets_received']}")
    print(f"  - Yanıt oranı: {stats['packets_received']/max(1,stats['packets_sent'])*100:.1f}%")

    tester.disconnect()
    print("\n✅ Test tamamlandı!")


def main():
    """Ana menü"""
    setup_logging()

    print("\n" + "="*60)
    print("🔒 CAN BUS SİBER GÜVENLİK TEST ÖRNEKLERİ")
    print("="*60)
    print("\n⚠️  UYARI: Bu örnekler sadece yetkili güvenlik testleri içindir!")
    print("⚠️  Yetkisiz kullanım yasalara aykırıdır!\n")

    examples = {
        '1': ("CAN ID Tarama (Güvenli)", example_1_id_scan),
        '2': ("Fuzzing Saldırısı", example_2_fuzzing),
        '3': ("Replay Attack", example_3_replay),
        '4': ("Diagnostic Saldırısı", example_4_diagnostic),
    }

    print("Mevcut Örnekler:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  q. Çıkış")

    while True:
        choice = input("\n\nSeçiminiz: ").strip().lower()

        if choice == 'q':
            print("\n👋 Güle güle!")
            break

        if choice in examples:
            _, func = examples[choice]
            try:
                func()
            except KeyboardInterrupt:
                print("\n\n⚠️  Test kullanıcı tarafından iptal edildi!")
            except Exception as e:
                print(f"\n❌ Hata: {e}")
                logging.exception("Test hatası:")
        else:
            print("❌ Geçersiz seçim!")


if __name__ == "__main__":
    main()

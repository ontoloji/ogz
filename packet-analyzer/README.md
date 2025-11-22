# Windows Packet Analyzer

Windows için C++ dilinde yazılmış, tüm network interface'lerini takip eden, paket analizi yapan ve paketleri tiplerine göre açıklayan bir network paket analiz aracı.

## Özellikler

- **Tüm Network Interface'leri Listeler**: Bilgisayardaki tüm ağ arayüzlerini tespit eder ve detaylı bilgi gösterir
- **Canlı Paket Yakalama**: Seçilen interface'den gerçek zamanlı paket yakalama
- **Detaylı Paket Analizi**: Paketleri katmanlarına göre analiz eder:
  - Ethernet Layer (MAC adresleri, EtherType)
  - Network Layer (IPv4/IPv6 adresleri, protokol, TTL)
  - Transport Layer (TCP/UDP port numaraları, TCP flags)
  - Application Layer (HTTP, HTTPS, DNS tanıma)
- **Protokol Tanıma**: ARP, ICMP, TCP, UDP, HTTP, HTTPS, DNS ve daha fazlası
- **Paket Filtreleme**: BPF (Berkeley Packet Filter) sözdizimi ile filtreleme
- **İstatistikler**: Yakalanan paketlerin detaylı istatistikleri
- **Hex Dump**: Paketlerin ham verisini hexadecimal formatında görüntüleme

## Desteklenen Paket Tipleri

### Network Layer
- IPv4
- IPv6
- ARP

### Transport Layer
- TCP (flags, sequence/acknowledgment numaraları ile)
- UDP
- ICMP

### Application Layer
- HTTP (port 80)
- HTTPS (port 443)
- DNS (port 53)

## Gereksinimler

### Yazılım Gereksinimleri

1. **Npcap** (Paket yakalama için gerekli)
   - İndirme: [https://npcap.com](https://npcap.com)
   - Kurulum sırasında "WinPcap API-compatible Mode" seçeneğini etkinleştirin

2. **Npcap SDK** (Derleme için gerekli)
   - İndirme: [https://npcap.com/#download](https://npcap.com/#download)
   - Bir klasöre çıkarın (örn: `C:\npcap-sdk-1.13`)

3. **C++ Derleyici** (aşağıdakilerden biri)
   - **MinGW-w64**: [https://www.mingw-w64.org](https://www.mingw-w64.org)
   - **MSVC**: Visual Studio veya Build Tools for Visual Studio
   - **MSYS2**: [https://www.msys2.org](https://www.msys2.org) (MinGW içerir)

### Sistem Gereksinimleri
- Windows 7 veya üzeri
- Yönetici hakları (paket yakalama için gerekli)

## Kurulum

### 1. Bağımlılıkları Kurun

```bash
# Npcap'i indirip kurun
# https://npcap.com

# Npcap SDK'yi indirip çıkarın
# https://npcap.com/#download
```

### 2. Makefile'ı Güncelleyin

`Makefile` dosyasını açın ve `NPCAP_SDK` değişkenini SDK'nın kurulu olduğu yola göre güncelleyin:

```makefile
NPCAP_SDK = C:/npcap-sdk-1.13
```

### 3. Projeyi Derleyin

#### MinGW Kullanarak:

```bash
make all
```

veya

```bash
make COMPILER=mingw
```

#### MSVC Kullanarak:

Visual Studio Developer Command Prompt'u açın ve:

```bash
make COMPILER=msvc
```

### 4. Programı Çalıştırın

```bash
make run
```

veya doğrudan:

```bash
bin\packet-analyzer.exe
```

**NOT**: Program yönetici hakları ile çalıştırılmalıdır!

## Kullanım

### Ana Menü

Program başlatıldığında aşağıdaki menü görüntülenir:

```
========================================
  Windows Packet Analyzer - C++
========================================
1. List all network interfaces
2. Start packet capture
3. Apply capture filter
4. View statistics
5. Reset statistics
0. Exit
========================================
```

### Temel Kullanım Adımları

1. **Interface Seçimi**: Önce "1" seçeneği ile network interface'leri listeleyin ve birini seçin
2. **Paket Yakalama**: "2" seçeneği ile paket yakalamayı başlatın
3. **Filtreleme** (Opsiyonel): "3" seçeneği ile BPF filtresi uygulayın
4. **İstatistikler**: "4" seçeneği ile istatistikleri görüntüleyin

### Yakalama Sırasında

- **Q tuşu**: Yakalamayı durdur
- **S tuşu**: İstatistikleri göster

### BPF Filtre Örnekleri

```bash
# Sadece TCP paketleri
tcp

# Sadece 80 numaralı port (HTTP)
tcp port 80

# Sadece ICMP paketleri
icmp

# Belirli bir IP adresi
host 192.168.1.1

# Belirli bir IP'den gelen paketler
src host 192.168.1.1

# Belirli bir IP'ye giden paketler
dst host 192.168.1.1

# HTTP veya HTTPS
tcp port 80 or tcp port 443

# DNS sorguları
udp port 53
```

## Proje Yapısı

```
packet-analyzer/
├── src/                    # Kaynak kod dosyaları
│   ├── main.cpp           # Ana program
│   ├── NetworkInterface.cpp
│   ├── PacketCapture.cpp
│   ├── PacketAnalyzer.cpp
│   └── PacketTypes.cpp
├── include/               # Header dosyaları
│   ├── NetworkInterface.h
│   ├── PacketCapture.h
│   ├── PacketAnalyzer.h
│   └── PacketTypes.h
├── obj/                   # Derleme nesneleri (otomatik oluşturulur)
├── bin/                   # Çalıştırılabilir dosya (otomatik oluşturulur)
├── Makefile              # Derleme dosyası
└── README.md             # Bu dosya
```

## Makefile Komutları

```bash
# Projeyi derle
make all

# Projeyi derle ve çalıştır
make run

# Derleme dosyalarını temizle
make clean

# Yardım mesajını göster
make help

# Kurulum bilgilerini göster
make install-info

# MinGW ile derle
make COMPILER=mingw

# MSVC ile derle
make COMPILER=msvc
```

## Sınıf Yapısı

### NetworkInterface
Network interface'lerini yönetir:
- `getAllInterfaces()`: Tüm interface'leri listeler
- `displayInterfaces()`: Interface'leri ekrana yazdırır
- `selectInterface()`: Bir interface seçer

### PacketCapture
Paket yakalama işlemlerini yönetir:
- `openDevice()`: Cihazı açar
- `startCapture()`: Yakalamayı başlatır (blocking)
- `startCaptureAsync()`: Yakalamayı arka planda başlatır
- `setFilter()`: BPF filtresi uygular
- `getStatistics()`: İstatistikleri alır

### Analyzer
Paket analizini yapar:
- `analyzePacket()`: Bir paketi analiz eder
- `printPacketInfo()`: Paket bilgilerini ekrana yazdırır
- `printHexDump()`: Hex dump gösterir
- `printStatistics()`: İstatistikleri gösterir

## Örnek Çıktı

```
----------------------------------------
Packet #1
Time: 1700000000.123456
Length: 74 bytes
Type: TCP

Ethernet Layer:
  Source MAC: 00:11:22:33:44:55
  Dest MAC: aa:bb:cc:dd:ee:ff
  Type: 0x800

IP Layer (v4):
  Source IP: 192.168.1.100
  Dest IP: 93.184.216.34
  Protocol: TCP (6)
  TTL: 64

Transport Layer:
  Source Port: 54321
  Dest Port: 80
  Seq: 1234567890
  Ack: 987654321
  Flags: SYN ACK

Description: HTTP packet from 192.168.1.100:54321 to 93.184.216.34:80 [SYN ACK]
----------------------------------------
```

## Sorun Giderme

### "Device not found" hatası
- Npcap'in doğru kurulduğundan emin olun
- Programı yönetici olarak çalıştırın

### Derleme hataları
- Npcap SDK yolunun Makefile'da doğru ayarlandığından emin olun
- Derleyicinin PATH'e eklendiğinden emin olun

### "Access denied" hatası
- Programı yönetici hakları ile çalıştırın

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## Katkıda Bulunma

Katkılar memnuniyetle karşılanır! Lütfen pull request gönderin veya issue açın.

## Geliştiriciler

- Packet capture: libpcap/Npcap kütüphanesi
- C++ implementation

## Kaynaklar

- [Npcap](https://npcap.com) - Windows packet capture library
- [libpcap](https://www.tcpdump.org) - Packet capture library
- [BPF Filter Syntax](https://biot.com/capstats/bpf.html)
- [TCP/IP Protocol Suite](https://en.wikipedia.org/wiki/Internet_protocol_suite)

# 📖 Kullanıcı Kılavuzu

## İçindekiler

1. [Başlangıç](#başlangıç)
2. [Not Yönetimi](#not-yönetimi)
3. [Görev Yönetimi](#görev-yönetimi)
4. [Pomodoro Timer](#pomodoro-timer)
5. [Takvim Entegrasyonu](#takvim-entegrasyonu)
6. [Ayarlar](#ayarlar)
7. [İpuçları ve Püf Noktaları](#ipuçları-ve-püf-noktaları)

## Başlangıç

### İlk Çalıştırma

1. `run.bat` dosyasını çalıştırın
2. Uygulama açıldığında varsayılan olarak **Notlar** sekmesi görünür
3. Sistem tepsisinde bir ikon belirecektir

### Arayüz Genel Bakış

Uygulama 5 ana sekmeden oluşur:
- **📝 Notlar**: Not alma ve hatırlatmalar
- **✅ Görevler**: To-Do list ve görev takibi
- **🍅 Pomodoro**: Verimlilik timer'ı
- **📅 Takvim**: Outlook entegrasyonu
- **⚙️ Ayarlar**: Uygulama ayarları

## Not Yönetimi

### Yeni Not Oluşturma

1. **Notlar** sekmesine gidin
2. **➕ Yeni Not** butonuna tıklayın
3. Formu doldurun:
   - **Başlık**: Kısa ve açıklayıcı (zorunlu)
   - **İçerik**: Detaylı açıklama
   - **Kategori**: İş, Kişisel, Alışveriş, vs.
   - **Öncelik**: Düşük, Orta, Yüksek, Acil
4. **💾 Kaydet** butonuna tıklayın

#### Öncelik Seviyeleri

- 🔵 **Düşük**: Acelesi olmayan notlar
- ⚪ **Orta**: Normal öncelikli notlar (varsayılan)
- 🟡 **Yüksek**: Önemli notlar
- 🔴 **Acil**: Hemen ilgilenilmesi gereken notlar

### Hatırlatma Ekleme

Not oluştururken veya düzenlerken:

1. **Hatırlatma Ekle** seçeneğini "Evet" yapın
2. **Tarih/Saat** seçin
3. **Tekrar** seçeneğini belirleyin:
   - **Tekrar Yok**: Tek seferlik
   - **Her Gün**: Günlük
   - **Her Hafta**: Haftalık
   - **Her Ay**: Aylık

#### Hatırlatma Örnekleri

**Günlük ilaç hatırlatması:**
- Başlık: "İlaç zamanı"
- Tarih/Saat: Bugün 08:00
- Tekrar: Her Gün

**Haftalık toplantı:**
- Başlık: "Ekip toplantısı"
- Tarih/Saat: Pazartesi 10:00
- Tekrar: Her Hafta

**Aylık fatura:**
- Başlık: "Elektrik faturası öde"
- Tarih/Saat: Her ayın 1'i
- Tekrar: Her Ay

### Not Düzenleme

1. Listeden bir not seçin
2. **✏️ Düzenle** butonuna tıklayın
3. Değişiklikleri yapın
4. **💾 Kaydet** butonuna tıklayın

### Not Arama ve Filtreleme

**Arama:**
- Üstteki arama kutusuna yazın
- Başlık ve içerikte arama yapar

**Filtreleme:**
- Kategori seçerek notları filtreleyin
- "Tümü" seçeneği tüm notları gösterir

### Not Silme

1. Silinecek notu seçin
2. **🗑️ Sil** butonuna tıklayın
3. Onaylayın

**Not**: Silinen notlar veritabanında "soft delete" ile işaretlenir ve geri kurtarılabilir.

## Görev Yönetimi

### Yeni Görev Oluşturma

1. **Görevler** sekmesine gidin
2. **➕ Yeni Görev** butonuna tıklayın
3. Formu doldurun:
   - **Başlık**: Görev adı (zorunlu)
   - **Açıklama**: Detaylı bilgi
   - **Kategori**: İş, Kişisel, vs.
   - **Öncelik**: 1-4 arası
   - **Durum**: Beklemede, Devam Ediyor, vs.
   - **Termin Tarihi**: Son tarih (opsiyonel)
   - **Tahmini Süre**: Dakika cinsinden

### Görev Durumları

- **⏳ Beklemede**: Henüz başlanmadı
- **🔄 Devam Ediyor**: Üzerinde çalışılıyor
- **✅ Tamamlandı**: Bitirildi
- **❌ İptal Edildi**: Yapılmayacak

### Hızlı Tamamlama

1. Görevi seçin
2. **✅ Tamamla** butonuna tıklayın

Görev otomatik olarak "Tamamlandı" durumuna geçer.

### Görev Filtreleme

**Durum Filtresi:**
- Tümü, Beklemede, Devam Ediyor, Tamamlandı

**Kategori Filtresi:**
- Tümü, İş, Kişisel, vs.

### İstatistikler

Üstteki bar gösterir:
- **Progress Bar**: Tamamlanma yüzdesi
- **Toplam Görev**: Tüm görevler
- **Tamamlandı**: Bitirilen görevler
- **Bekliyor**: Başlanmamış görevler
- **Devam Ediyor**: Üzerinde çalışılan görevler

## Pomodoro Timer

### Pomodoro Tekniği Nedir?

Pomodoro, 25 dakika çalışma + 5 dakika mola döngüsüyle verimlilik artırma tekniğidir.

### Çalışma Oturumu Başlatma

1. **Pomodoro** sekmesine gidin
2. **🍅 Çalışma Başlat** butonuna tıklayın
3. Timer başlayacaktır
4. Çalışmaya odaklanın!

### Timer Kontrolü

**⏸ Duraklat**: Timer'ı geçici olarak durdurur
**▶ Devam Et**: Timer'ı sürdürür
**⏹ Durdur**: Timer'ı tamamen bitirir

### Mola Türleri

**☕ Kısa Mola**: 5 dakika (varsayılan)
- Her çalışma oturumu sonrası

**🎉 Uzun Mola**: 15 dakika (varsayılan)
- Her 4 çalışma oturumundan sonra

### Ayarları Özelleştirme

**Ayarlar** sekmesinde:
- **Çalışma Süresi**: 1-60 dakika
- **Kısa Mola**: 1-30 dakika
- **Uzun Mola**: 5-60 dakika
- **Uzun Molaya Kadar**: Kaç oturum sonra

### İstatistikler

**Bugünün İstatistikleri:**
- Toplam oturum sayısı
- Çalışma oturumları
- Toplam dakika

### İpuçları

1. Çalışma sırasında bildirimleri kapatın (Odak Modu)
2. Her çalışma için bir görev belirleyin
3. Mola sırasında ekrandan uzaklaşın
4. Uzun molalarda kısa bir yürüyüş yapın

## Takvim Entegrasyonu

### Outlook'a Bağlanma

1. **Takvim** sekmesine gidin
2. **🔗 Outlook'a Bağlan** butonuna tıklayın
3. Microsoft hesabınızla giriş yapın
4. İzinleri onaylayın

**Not**: Demo modunda çalışıyorsanız, gerçek bağlantı için Azure AD kaydı gerekir. Detaylar için INSTALLATION.md dosyasına bakın.

### Etkinlikleri Senkronize Etme

1. **🔄 Senkronize Et** butonuna tıklayın
2. Önümüzdeki 7 gün için etkinlikler çekilir
3. Yerel veritabanında önbelleklenir

### Otomatik Senkronizasyon

**Ayarlar** sekmesinde:
- **Otomatik Senkronizasyon**: Etkinleştir
- **Senkronizasyon Aralığı**: 5-120 dakika

### Bildirimler

- Etkinliklerden **24 saat önce** otomatik bildirim
- Konu, yer, katılımcılar ve saat bilgisi

### Etkinlik Detayları

Listeden bir etkinlik seçtiğinizde görürsünüz:
- 📋 Konu
- 📅 Başlangıç ve bitiş saati
- 📍 Yer
- 👤 Düzenleyen
- 👥 Katılımcılar
- 📝 Açıklama

## Ayarlar

### Görünüm

**Tema:**
- **Açık**: Aydınlık tema (varsayılan)
- **Koyu**: Karanlık tema

Tema değişikliği anında uygulanır.

### Bildirimler

**Bildirimleri Etkinleştir:**
- Tüm bildirimleri aç/kapat

**Bildirim Sesi:**
- Sesli bildirimler

### Outlook Entegrasyonu

**Otomatik Senkronizasyon:**
- Arka planda periyodik senkronizasyon

**Senkronizasyon Aralığı:**
- Ne sıklıkla kontrol edilecek (5-120 dakika)

### Pomodoro Ayarları

Varsayılan değerler:
- Çalışma Süresi: 25 dakika
- Kısa Mola: 5 dakika
- Uzun Mola: 15 dakika
- Uzun Molaya Kadar: 4 oturum

Değerleri ihtiyacınıza göre ayarlayın.

### Başlangıç

**Windows ile Başlat:**
- Bilgisayar açıldığında otomatik çalıştır

**Sistem Tepsisine Küçült:**
- Pencere kapatıldığında arka planda çalış

### Veri Yönetimi

**📤 Verileri Dışa Aktar:**
- Tüm notlar, görevler ve ayarlar JSON dosyasına

**📥 Verileri İçe Aktar:**
- Yedek dosyadan geri yükleme

**🗑️ Tüm Verileri Temizle:**
- DİKKAT: Geri alınamaz!

## İpuçları ve Püf Noktaları

### Verimlilik Artırma

1. **Öncelik Kullanın**: Görevleri ve notları önceliklendirin
2. **Günlük Planlama**: Her sabah günün görevlerini gözden geçirin
3. **Pomodoro ile Çalışın**: Odaklanmak için 25 dakikalık bloklarda çalışın
4. **Hatırlatma Ayarlayın**: Önemli işler için hatırlatma unutmayın

### Düzenleme

1. **Kategorileri Kullanın**: Notları ve görevleri kategorize edin
2. **Arama Kullanın**: Hızlı bulma için arama özelliğini kullanın
3. **Filtreleme**: Spesifik kategorilere odaklanın
4. **Düzenli Temizlik**: Tamamlanan görevleri arşivleyin/silin

### Yedekleme

1. **Düzenli Yedek**: Haftada bir veri yedekleyin
2. **Güvenli Saklama**: Yedek dosyalarını farklı yerde saklayın
3. **Test Edin**: Bazen geri yüklemeyi test edin

### Klavye Kısayolları (Gelecek Sürümde)

Şu an için mouse kullanımı gereklidir. Klavye kısayolları gelecek sürümde eklenecektir.

### Sorun mu Yaşıyorsunuz?

1. **Uygulamayı Yeniden Başlatın**: Çoğu sorunu çözer
2. **Ayarları Kontrol Edin**: Bildirimlerin açık olduğundan emin olun
3. **Log'lara Bakın**: Hata mesajlarını kontrol edin
4. **GitHub Issues**: Yardım için issue açın

## Sık Sorulan Sorular

**S: Veritabanı nerede?**
C: `data/assistant.db` dosyasında

**S: Outlook zorunlu mu?**
C: Hayır, opsiyoneldir. Diğer özellikler bağımsız çalışır.

**S: Mobil uygulaması var mı?**
C: Şu an sadece Windows. Mobil versiyon planlanıyor.

**S: Veri güvenliği?**
C: Veriler yerel bilgisayarınızda saklanır. Bulut yok.

**S: Kaç not/görev ekleyebilirim?**
C: Sınır yok, ancak performans için 10,000'den az önerilir.

**S: İnternet gerekli mi?**
C: Sadece Outlook senkronizasyonu için. Diğer özellikler çevrimdışı çalışır.

---

**Yardıma mı ihtiyacınız var?**
GitHub Issues: https://github.com/yourusername/windows-assistant/issues

/*
 * SORT Test Otomasyon Sistemi - Arduino Firmware
 *
 * 2 Kanallı PWM Analog Çıkış Kontrolü
 * - Kanal 1 (DAF Motor): Pin 9, 0.5V - 4.5V
 * - Kanal 2 (IBK): Pin 10, 2.5V - 4.5V
 *
 * RC Filter gerekli: Her kanal için 1kΩ + 100µF
 *
 * Serial Komut Formatı: P<channel>,<percentage>\n
 * Örnek: P1,75\n (Kanal 1, %75 gaz)
 *
 * Arduino Uno
 * Baud Rate: 115200
 */

// Pin tanımlamaları
#define CHANNEL1_PIN 9   // DAF Motor PWM çıkışı
#define CHANNEL2_PIN 10  // IBK PWM çıkışı
#define LED_PIN 13       // Durum LED'i

// PWM aralıkları (0-255)
// 5V referans voltaj, RC filter ile analog çıkış

// Kanal 1 (DAF): 0.5V - 4.5V
// 0.5V = 0.5/5 * 255 = 25.5 ≈ 26
// 4.5V = 4.5/5 * 255 = 229.5 ≈ 230
#define DAF_PWM_MIN 26
#define DAF_PWM_MAX 230

// Kanal 2 (IBK): 2.5V - 4.5V
// 2.5V = 2.5/5 * 255 = 127.5 ≈ 128
// 4.5V = 4.5/5 * 255 = 229.5 ≈ 230
#define IBK_PWM_MIN 128
#define IBK_PWM_MAX 230

// Global değişkenler
int channel1_percent = 0;  // Kanal 1 yüzde değeri (0-100)
int channel2_percent = 0;  // Kanal 2 yüzde değeri (0-100)

// Serial buffer
String inputString = "";
boolean stringComplete = false;

// LED yanıp sönme
unsigned long lastBlinkTime = 0;
boolean ledState = false;

void setup() {
  // Serial başlat
  Serial.begin(115200);
  while (!Serial) {
    ; // Serial port hazır olana kadar bekle
  }

  // Pin modları
  pinMode(CHANNEL1_PIN, OUTPUT);
  pinMode(CHANNEL2_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  // Başlangıç değerleri (güvenlik için %0)
  setChannel1(0);
  setChannel2(0);

  // Hazır mesajı
  Serial.println("SORT Arduino Firmware v1.0");
  Serial.println("READY");

  // LED yanıp sönerek hazır sinyali ver
  for (int i = 0; i < 5; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}

void loop() {
  // Serial veri işle
  processSerial();

  // LED yanıp sönme (canlılık göstergesi - her saniye)
  unsigned long currentTime = millis();
  if (currentTime - lastBlinkTime >= 1000) {
    ledState = !ledState;
    digitalWrite(LED_PIN, ledState);
    lastBlinkTime = currentTime;
  }
}

/**
 * Serial veri işleme
 */
void processSerial() {
  // Serial buffer'dan oku
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }

  // Komut tamamlandı mı?
  if (stringComplete) {
    parseCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
}

/**
 * Komutu parse et ve işle
 * Format: P<channel>,<percentage>
 * Örnek: P1,75 -> Kanal 1, %75
 */
void parseCommand(String cmd) {
  cmd.trim();  // Boşlukları temizle

  // 'P' ile başlamalı
  if (cmd.charAt(0) != 'P' && cmd.charAt(0) != 'p') {
    Serial.println("ERROR: Invalid command");
    return;
  }

  // Format: P<channel>,<percentage>
  int commaIndex = cmd.indexOf(',');
  if (commaIndex == -1) {
    Serial.println("ERROR: Missing comma");
    return;
  }

  // Kanal numarasını parse et
  String channelStr = cmd.substring(1, commaIndex);
  int channel = channelStr.toInt();

  // Yüzde değerini parse et
  String percentStr = cmd.substring(commaIndex + 1);
  int percent = percentStr.toInt();

  // Geçerlilik kontrolü
  if (channel < 1 || channel > 2) {
    Serial.println("ERROR: Invalid channel (1 or 2)");
    return;
  }

  if (percent < 0 || percent > 100) {
    Serial.println("ERROR: Invalid percentage (0-100)");
    return;
  }

  // Komutu uygula
  if (channel == 1) {
    setChannel1(percent);
  } else if (channel == 2) {
    setChannel2(percent);
  }

  // Başarı yanıtı
  Serial.println("OK");
}

/**
 * Kanal 1 (DAF) değerini ayarla
 */
void setChannel1(int percent) {
  // Sınırla
  percent = constrain(percent, 0, 100);

  // PWM değerini hesapla
  // 0% -> DAF_PWM_MIN (0.5V)
  // 100% -> DAF_PWM_MAX (4.5V)
  int pwmValue = map(percent, 0, 100, DAF_PWM_MIN, DAF_PWM_MAX);

  // PWM çıkışı
  analogWrite(CHANNEL1_PIN, pwmValue);

  // Değeri kaydet
  channel1_percent = percent;
}

/**
 * Kanal 2 (IBK) değerini ayarla
 */
void setChannel2(int percent) {
  // Sınırla
  percent = constrain(percent, 0, 100);

  // PWM değerini hesapla
  // 0% -> IBK_PWM_MIN (2.5V)
  // 100% -> IBK_PWM_MAX (4.5V)
  int pwmValue = map(percent, 0, 100, IBK_PWM_MIN, IBK_PWM_MAX);

  // PWM çıkışı
  analogWrite(CHANNEL2_PIN, pwmValue);

  // Değeri kaydet
  channel2_percent = percent;
}

/**
 * Acil durum - tüm çıkışları sıfırla
 * (Serial'den 'E' komutu ile tetiklenebilir)
 */
void emergencyStop() {
  setChannel1(0);
  setChannel2(0);
  Serial.println("EMERGENCY STOP");

  // LED hızlı yanıp sönerek uyar
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(50);
    digitalWrite(LED_PIN, LOW);
    delay(50);
  }
}

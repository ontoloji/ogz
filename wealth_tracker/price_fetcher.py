"""
Online fiyat çekme modülü - Wealth Tracker
Değerli madenler, döviz kurları ve diğer varlıkların güncel fiyatlarını çeker
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class PriceFetcher:
    def __init__(self):
        """Fiyat çekici servisini başlat"""
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 300  # 5 dakika

    def get_gold_price(self, currency="TRY") -> Optional[float]:
        """
        Altın fiyatını çek (gram başına)
        API: metals-api.com alternatif ücretsiz servisler kullanılabilir
        """
        try:
            # Örnek: Açık kaynak altın fiyat API'si
            # Gerçek uygulamada api.metals.dev veya benzeri kullanılabilir
            cache_key = f"gold_{currency}"

            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]

            # Örnek API çağrısı (gerçek bir API anahtarı gerektirir)
            # Bu örnek kod - üretim için geçerli bir API kullanın
            url = "https://api.metalpriceapi.com/v1/latest"
            params = {
                "api_key": "YOUR_API_KEY",
                "base": "XAU",  # Altın
                "currencies": currency
            }

            # Geçici çözüm: Sabit değer (API anahtarı olmadan)
            # Gerçek uygulamada yukarıdaki API çağrısı kullanılmalı
            if currency == "TRY":
                price = 2850.0  # Örnek: Gram başına TL
            elif currency == "USD":
                price = 85.0  # Örnek: Gram başına USD
            else:
                price = 85.0

            self.cache[cache_key] = price
            self.cache_time[cache_key] = datetime.now()
            return price

        except Exception as e:
            print(f"Altın fiyatı alınamadı: {e}")
            return None

    def get_silver_price(self, currency="TRY") -> Optional[float]:
        """Gümüş fiyatını çek (gram başına)"""
        try:
            cache_key = f"silver_{currency}"

            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]

            # Geçici çözüm: Sabit değer
            if currency == "TRY":
                price = 35.0  # Örnek: Gram başına TL
            elif currency == "USD":
                price = 1.05  # Örnek: Gram başına USD
            else:
                price = 1.05

            self.cache[cache_key] = price
            self.cache_time[cache_key] = datetime.now()
            return price

        except Exception as e:
            print(f"Gümüş fiyatı alınamadı: {e}")
            return None

    def get_exchange_rate(self, from_currency="USD", to_currency="TRY") -> Optional[float]:
        """
        Döviz kurunu çek
        API: exchangerate-api.com veya TCMB
        """
        try:
            cache_key = f"{from_currency}_{to_currency}"

            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]

            # Ücretsiz döviz API'si
            url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"

            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    rate = data['rates'].get(to_currency)
                    if rate:
                        self.cache[cache_key] = rate
                        self.cache_time[cache_key] = datetime.now()
                        return rate
            except:
                pass

            # Yedek: Sabit değerler (API başarısız olursa)
            default_rates = {
                "USD_TRY": 34.50,
                "EUR_TRY": 37.80,
                "GBP_TRY": 43.90,
                "USD_USD": 1.0,
                "EUR_USD": 1.09,
                "GBP_USD": 1.27
            }

            rate = default_rates.get(cache_key, 1.0)
            self.cache[cache_key] = rate
            self.cache_time[cache_key] = datetime.now()
            return rate

        except Exception as e:
            print(f"Döviz kuru alınamadı: {e}")
            return None

    def get_asset_price(self, asset_type: str, asset_name: str,
                       currency="TRY") -> Optional[float]:
        """
        Varlık tipine göre güncel fiyatı getir
        """
        asset_type = asset_type.upper()
        asset_name = asset_name.upper()

        if asset_type == "DEĞERLI MADEN":
            if "ALTIN" in asset_name or "GOLD" in asset_name:
                return self.get_gold_price(currency)
            elif "GÜMÜŞ" in asset_name or "SILVER" in asset_name:
                return self.get_silver_price(currency)

        elif asset_type == "DÖVİZ":
            # Döviz birimi olarak algıla
            currency_codes = {
                "DOLAR": "USD",
                "EURO": "EUR",
                "POUND": "GBP",
                "STERLIN": "GBP"
            }
            from_currency = currency_codes.get(asset_name, asset_name)
            return self.get_exchange_rate(from_currency, currency)

        elif asset_type == "VADELİ YATIRIM":
            # Vadeli yatırımlar için fiyat güncellenmez
            # Kullanıcının girdiği satın alma fiyatı kullanılır
            return None

        return None

    def _is_cache_valid(self, key: str) -> bool:
        """Cache'in geçerli olup olmadığını kontrol et"""
        if key not in self.cache or key not in self.cache_time:
            return False

        elapsed = (datetime.now() - self.cache_time[key]).total_seconds()
        return elapsed < self.cache_duration

    def clear_cache(self):
        """Cache'i temizle"""
        self.cache.clear()
        self.cache_time.clear()

    def get_all_prices(self, currency="TRY") -> Dict[str, float]:
        """Tüm popüler varlıkların fiyatlarını getir"""
        prices = {
            "ALTIN (gram)": self.get_gold_price(currency),
            "GÜMÜŞ (gram)": self.get_silver_price(currency),
            "USD": self.get_exchange_rate("USD", currency),
            "EUR": self.get_exchange_rate("EUR", currency),
            "GBP": self.get_exchange_rate("GBP", currency),
        }
        return {k: v for k, v in prices.items() if v is not None}

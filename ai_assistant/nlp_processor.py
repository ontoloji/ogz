"""
Doğal Dil İşleme Modülü
Türkçe komutları anlayıp işler
"""

import re
import webbrowser
import subprocess
import os
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import locale

# Türkçe locale ayarla (Windows için)
try:
    locale.setlocale(locale.LC_ALL, 'turkish')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    except:
        pass


class NLPProcessor:
    def __init__(self, database):
        self.db = database

        # Komut pattern'leri
        self.patterns = {
            'reminder': [
                r'(yarın|bugün|.*gün.*)\s+(saat\s+)?(\d{1,2}):?(\d{0,2}).*?(hatırlat|hatırlatma)',
                r'(\d{1,2})\s+(dakika|saat|gün)\s+sonra.*?(hatırlat|hatırlatma)',
                r'(hatırlat|hatırlatma).*?(yarın|bugün|\d{1,2}:\d{2})',
            ],
            'note': [
                r'(not\s+al|not\s+ekle|not\s+yaz|kaydet)',
                r'(.*)\s+(diye\s+not\s+al|diye\s+bir\s+not\s+al)',
            ],
            'calculation': [
                r'(\d+)\s*(artı|\+|ekle)\s*(\d+)',
                r'(\d+)\s*(eksi|\-|çıkar)\s*(\d+)',
                r'(\d+)\s*(çarp|çarpı|\*|x)\s*(\d+)',
                r'(\d+)\s*(böl|bölü|/|÷)\s*(\d+)',
                r'kaç\s+(\d+)\s*(artı|\+|ekle|çarp|çarpı|\*|x|eksi|\-|çıkar|böl|bölü|/|÷)\s*(\d+)',
            ],
            'web_search': [
                r'(ara|arama\s+yap|google\'?da\s+ara|search)\s+(.*)',
                r'(.*)\s+(ara|arama\s+yap|google\'?da\s+ara)',
            ],
            'open_app': [
                r'(aç|başlat|çalıştır|open)\s+(.*)',
                r'(.*)\s+(aç|başlat|çalıştır)',
            ],
            'file_search': [
                r'(dosya\s+ara|dosya\s+bul|ara.*dosya)\s+(.*)',
                r'(.*)\s+(dosya.*ara|dosya.*bul)',
            ],
        }

        # Yaygın uygulamalar ve yolları (Windows)
        self.common_apps = {
            'chrome': 'chrome.exe',
            'google chrome': 'chrome.exe',
            'firefox': 'firefox.exe',
            'edge': 'msedge.exe',
            'microsoft edge': 'msedge.exe',
            'notepad': 'notepad.exe',
            'not defteri': 'notepad.exe',
            'calculator': 'calc.exe',
            'hesap makinesi': 'calc.exe',
            'word': 'winword.exe',
            'excel': 'excel.exe',
            'outlook': 'outlook.exe',
            'paint': 'mspaint.exe',
            'cmd': 'cmd.exe',
            'terminal': 'cmd.exe',
            'powershell': 'powershell.exe',
            'explorer': 'explorer.exe',
            'dosya gezgini': 'explorer.exe',
        }

    def process_command(self, command):
        """Ana komut işleme fonksiyonu"""
        command = command.lower().strip()

        # Boş komut kontrolü
        if not command:
            return "Lütfen bir komut girin."

        # Komut geçmişine kaydet
        response = ""

        # Komut tipini belirle ve işle
        if self._match_pattern('reminder', command):
            response = self._handle_reminder(command)
        elif self._match_pattern('note', command):
            response = self._handle_note(command)
        elif self._match_pattern('calculation', command):
            response = self._handle_calculation(command)
        elif self._match_pattern('web_search', command):
            response = self._handle_web_search(command)
        elif self._match_pattern('file_search', command):
            response = self._handle_file_search(command)
        elif self._match_pattern('open_app', command):
            response = self._handle_open_app(command)
        else:
            response = self._handle_general(command)

        # Geçmişe kaydet
        self.db.add_command_history(command, response)

        return response

    def _match_pattern(self, pattern_type, command):
        """Komutun belirli bir pattern'e uyup uymadığını kontrol et"""
        patterns = self.patterns.get(pattern_type, [])
        for pattern in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def _handle_reminder(self, command):
        """Hatırlatıcı ekle"""
        try:
            # Zaman ifadelerini çıkar
            time_match = re.search(r'(\d{1,2}):?(\d{0,2})', command)
            relative_match = re.search(r'(\d+)\s+(dakika|saat|gün)\s+sonra', command)

            remind_time = None

            if relative_match:
                # Göreceli zaman (X dakika/saat/gün sonra)
                amount = int(relative_match.group(1))
                unit = relative_match.group(2)

                if unit == 'dakika':
                    remind_time = datetime.now() + timedelta(minutes=amount)
                elif unit == 'saat':
                    remind_time = datetime.now() + timedelta(hours=amount)
                elif unit == 'gün':
                    remind_time = datetime.now() + timedelta(days=amount)

            elif time_match:
                # Sabit saat (yarın 10:00, bugün 15:30)
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0

                remind_time = datetime.now().replace(hour=hour, minute=minute, second=0)

                # Yarın mı bugün mü?
                if 'yarın' in command:
                    remind_time += timedelta(days=1)
                elif remind_time <= datetime.now():
                    # Geçmiş bir saat verilmişse yarına al
                    remind_time += timedelta(days=1)

            if remind_time:
                # Hatırlatıcı başlığını çıkar
                title = command
                for word in ['hatırlat', 'hatırlatma', 'yarın', 'bugün', 'saat', 'sonra', 'dakika']:
                    title = title.replace(word, '')
                title = re.sub(r'\d{1,2}:?\d{0,2}', '', title).strip()

                if not title:
                    title = "Hatırlatma"

                self.db.add_reminder(title, remind_time.strftime('%Y-%m-%d %H:%M:%S'))
                return f"✅ Hatırlatıcı oluşturuldu: '{title}' - {remind_time.strftime('%d.%m.%Y %H:%M')}"
            else:
                return "⚠️ Zaman bilgisi anlaşılamadı. Örnek: 'yarın saat 10:00 toplantı hatırlat' veya '30 dakika sonra hatırlat'"

        except Exception as e:
            return f"❌ Hatırlatıcı oluşturulamadı: {str(e)}"

    def _handle_note(self, command):
        """Not ekle"""
        try:
            # Not içeriğini çıkar
            note_match = re.search(r'(.*?)\s+diye\s+(bir\s+)?not\s+al', command)
            if note_match:
                content = note_match.group(1).strip()
            else:
                # "not al: içerik" formatı
                content = re.sub(r'(not\s+al|not\s+ekle|not\s+yaz|kaydet)[:\s]+', '', command).strip()

            if content:
                self.db.add_note(content)
                return f"📝 Not kaydedildi: '{content}'"
            else:
                return "⚠️ Not içeriği bulunamadı. Örnek: 'proje fikirleri diye not al' veya 'not al: alışveriş listesi'"

        except Exception as e:
            return f"❌ Not kaydedilemedi: {str(e)}"

    def _handle_calculation(self, command):
        """Hesaplama yap"""
        try:
            # Türkçe operatörleri sembollere çevir
            command = command.replace('artı', '+').replace('ekle', '+')
            command = command.replace('eksi', '-').replace('çıkar', '-')
            command = command.replace('çarp', '*').replace('çarpı', '*').replace('x', '*')
            command = command.replace('böl', '/').replace('bölü', '/').replace('÷', '/')

            # Sayıları ve operatörleri bul
            calc_match = re.search(r'(\d+\.?\d*)\s*([+\-*/])\s*(\d+\.?\d*)', command)

            if calc_match:
                num1 = float(calc_match.group(1))
                operator = calc_match.group(2)
                num2 = float(calc_match.group(3))

                result = None
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        return "❌ Sıfıra bölme hatası!"

                if result is not None:
                    # Sonuç tam sayı ise .0 gösterme
                    if result == int(result):
                        result = int(result)
                    return f"🔢 Sonuç: {result}"

            return "⚠️ Hesaplama anlaşılamadı. Örnek: '15 çarpı 8' veya '100 eksi 25'"

        except Exception as e:
            return f"❌ Hesaplama hatası: {str(e)}"

    def _handle_web_search(self, command):
        """Web araması yap"""
        try:
            # Arama terimini çıkar
            search_term = re.sub(r'(ara|arama\s+yap|google\'?da\s+ara|search)\s*', '', command).strip()
            search_term = re.sub(r'\s+(ara|arama\s+yap)$', '', search_term).strip()

            if search_term:
                url = f"https://www.google.com/search?q={search_term}"
                webbrowser.open(url)
                return f"🔍 Google'da aranıyor: '{search_term}'"
            else:
                return "⚠️ Arama terimi bulunamadı. Örnek: 'python nedir ara' veya 'yapay zeka google'da ara'"

        except Exception as e:
            return f"❌ Arama başlatılamadı: {str(e)}"

    def _handle_file_search(self, command):
        """Dosya ara"""
        try:
            # Arama terimini çıkar
            search_term = re.sub(r'(dosya\s+ara|dosya\s+bul|ara|bul)\s*', '', command).strip()
            search_term = re.sub(r'\s+(dosya|dosyayı|dosyaları)?\s*(ara|bul)$', '', search_term).strip()

            if search_term:
                from file_search import FileSearcher
                searcher = FileSearcher()
                results = searcher.search(search_term, max_results=10)

                if results:
                    response = f"📁 '{search_term}' için {len(results)} sonuç bulundu:\n\n"
                    for i, file_path in enumerate(results[:5], 1):
                        response += f"{i}. {file_path}\n"
                    if len(results) > 5:
                        response += f"\n... ve {len(results) - 5} sonuç daha"
                    return response
                else:
                    return f"⚠️ '{search_term}' için sonuç bulunamadı."
            else:
                return "⚠️ Arama terimi bulunamadı. Örnek: 'python dosyalarını ara' veya 'rapor.pdf dosya ara'"

        except Exception as e:
            return f"❌ Dosya araması başarısız: {str(e)}"

    def _handle_open_app(self, command):
        """Uygulama aç"""
        try:
            # Uygulama adını çıkar
            app_name = re.sub(r'(aç|başlat|çalıştır|open)\s*', '', command).strip()
            app_name = re.sub(r'\s+(aç|başlat|çalıştır)$', '', app_name).strip()
            app_name = app_name.replace("'u", "").replace("'ü", "").replace("'i", "").replace("'ı", "")

            if app_name:
                # Yaygın uygulamalardan kontrol et
                exe_name = self.common_apps.get(app_name.lower())

                if exe_name:
                    try:
                        subprocess.Popen(exe_name, shell=True)
                        self.db.add_favorite_app(app_name, exe_name)
                        return f"✅ '{app_name}' açılıyor..."
                    except Exception as e:
                        return f"❌ '{app_name}' açılamadı: {str(e)}"
                else:
                    # Doğrudan çalıştırmayı dene
                    try:
                        subprocess.Popen(app_name, shell=True)
                        self.db.add_favorite_app(app_name, app_name)
                        return f"✅ '{app_name}' açılıyor..."
                    except Exception as e:
                        return f"❌ '{app_name}' bulunamadı. Bilinen uygulamalar: Chrome, Firefox, Notepad, Calculator, Word, Excel"
            else:
                return "⚠️ Uygulama adı bulunamadı. Örnek: 'chrome aç' veya 'notepad başlat'"

        except Exception as e:
            return f"❌ Uygulama açılamadı: {str(e)}"

    def _handle_general(self, command):
        """Genel komutları işle"""
        # Basit yanıtlar
        greetings = ['merhaba', 'selam', 'hey', 'hi', 'hello', 'günaydın', 'iyi günler']
        if any(greeting in command for greeting in greetings):
            return "Merhaba! Size nasıl yardımcı olabilirim?"

        thanks = ['teşekkür', 'sağol', 'eyvallah', 'thanks']
        if any(thank in command for thank in thanks):
            return "Rica ederim! Başka bir şey için yardımcı olabilir miyim?"

        if 'nasılsın' in command or 'ne haber' in command:
            return "Ben bir AI asistanım, her zaman iyiyim! Size nasıl yardımcı olabilirim?"

        # Yardım
        if 'yardım' in command or 'help' in command or 'ne yapabilirsin' in command:
            return """
🤖 Size şu konularda yardımcı olabilirim:

📝 Not alma:
   • "proje fikirleri diye not al"
   • "alışveriş listesi not ekle"

⏰ Hatırlatıcı:
   • "yarın saat 10'da toplantı hatırlat"
   • "30 dakika sonra çay hatırlat"

🔢 Hesaplama:
   • "15 çarpı 8 kaç"
   • "100 eksi 25"

🔍 Arama:
   • "python dosyalarını ara"
   • "yapay zeka google'da ara"

🚀 Uygulama açma:
   • "chrome aç"
   • "notepad başlat"
"""

        return "Anlamadım. 'yardım' yazarak neler yapabileceğimi öğrenebilirsin."

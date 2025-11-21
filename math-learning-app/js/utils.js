/**
 * Yardımcı Fonksiyonlar
 * Genel kullanım için yardımcı metodlar
 */

const Utils = {
    /**
     * LocalStorage'a veri kaydet
     */
    saveToStorage(key, data) {
        try {
            localStorage.setItem(key, JSON.stringify(data));
            return true;
        } catch (error) {
            console.error('Storage error:', error);
            return false;
        }
    },

    /**
     * LocalStorage'dan veri oku
     */
    loadFromStorage(key, defaultValue = null) {
        try {
            const data = localStorage.getItem(key);
            return data ? JSON.parse(data) : defaultValue;
        } catch (error) {
            console.error('Storage error:', error);
            return defaultValue;
        }
    },

    /**
     * Rastgele sayı üret (min ve max dahil)
     */
    randomInt(min, max) {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    /**
     * Diziyi karıştır (Fisher-Yates shuffle)
     */
    shuffle(array) {
        const shuffled = [...array];
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        return shuffled;
    },

    /**
     * İki sayının en büyük ortak bölenini bul
     */
    gcd(a, b) {
        a = Math.abs(a);
        b = Math.abs(b);
        while (b) {
            const temp = b;
            b = a % b;
            a = temp;
        }
        return a;
    },

    /**
     * İki sayının en küçük ortak katını bul
     */
    lcm(a, b) {
        return Math.abs(a * b) / Utils.gcd(a, b);
    },

    /**
     * Kesri sadeleştir
     */
    simplifyFraction(numerator, denominator) {
        const divisor = Utils.gcd(numerator, denominator);
        return {
            numerator: numerator / divisor,
            denominator: denominator / divisor
        };
    },

    /**
     * Sayıyı formatla (1000 -> 1.000)
     */
    formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    },

    /**
     * Zamanı formatla (saniye -> saat:dakika:saniye)
     */
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}s ${minutes}dk`;
        } else if (minutes > 0) {
            return `${minutes}dk ${secs}sn`;
        } else {
            return `${secs}sn`;
        }
    },

    /**
     * Tarihi formatla
     */
    formatDate(date) {
        const d = new Date(date);
        const day = d.getDate().toString().padStart(2, '0');
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        const year = d.getFullYear();
        return `${day}.${month}.${year}`;
    },

    /**
     * Bugünün tarihini al (YYYY-MM-DD formatında)
     */
    getTodayKey() {
        const today = new Date();
        const year = today.getFullYear();
        const month = (today.getMonth() + 1).toString().padStart(2, '0');
        const day = today.getDate().toString().padStart(2, '0');
        return `${year}-${month}-${day}`;
    },

    /**
     * İki tarih arasındaki gün farkını bul
     */
    daysBetween(date1, date2) {
        const oneDay = 24 * 60 * 60 * 1000;
        const d1 = new Date(date1);
        const d2 = new Date(date2);
        return Math.round(Math.abs((d1 - d2) / oneDay));
    },

    /**
     * Yüzdeyi hesapla
     */
    calculatePercentage(value, total) {
        if (total === 0) return 0;
        return Math.round((value / total) * 100);
    },

    /**
     * Rastgele bir diziden eleman seç
     */
    randomChoice(array) {
        return array[Math.floor(Math.random() * array.length)];
    },

    /**
     * Dizi içinden N adet rastgele eleman seç
     */
    randomChoices(array, n) {
        const shuffled = Utils.shuffle(array);
        return shuffled.slice(0, n);
    },

    /**
     * Animasyon ile element göster
     */
    showElement(element, animationClass = 'fadeIn') {
        element.classList.remove('hidden');
        element.classList.add(animationClass);
    },

    /**
     * Animasyon ile element gizle
     */
    hideElement(element) {
        element.classList.add('hidden');
    },

    /**
     * Ekran değiştir
     */
    switchScreen(fromScreen, toScreen) {
        if (fromScreen) {
            fromScreen.classList.remove('active');
        }
        toScreen.classList.add('active');
        window.scrollTo(0, 0);
    },

    /**
     * Confetti efekti oluştur
     */
    createConfetti(container) {
        const colors = ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#EF4444'];
        const confettiCount = 50;

        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti-piece';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.backgroundColor = Utils.randomChoice(colors);
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.style.animationDuration = (Math.random() * 2 + 1) + 's';
            container.appendChild(confetti);

            setTimeout(() => confetti.remove(), 3000);
        }
    },

    /**
     * Yıldız efekti oluştur
     */
    createStars(container, count = 10) {
        const starEmojis = ['⭐', '✨', '🌟', '💫'];

        for (let i = 0; i < count; i++) {
            const star = document.createElement('div');
            star.className = 'star-effect';
            star.textContent = Utils.randomChoice(starEmojis);
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = (i * 0.1) + 's';
            container.appendChild(star);

            setTimeout(() => star.remove(), 1500);
        }
    },

    /**
     * Toast bildirim göster
     */
    showToast(message, duration = 3000) {
        const toast = document.getElementById('achievement-toast');
        const toastText = document.getElementById('toast-text');

        toastText.textContent = message;
        toast.classList.remove('hidden');

        setTimeout(() => {
            toast.classList.add('hidden');
        }, duration);
    },

    /**
     * Motivasyon mesajı al
     */
    getMotivationMessage(correctCount, totalCount) {
        const percentage = Utils.calculatePercentage(correctCount, totalCount);

        if (percentage === 100) {
            return Utils.randomChoice([
                'Mükemmel! Hepsini doğru yaptın! 🎉',
                'İnanılmaz! Tam puan! 🌟',
                'Süpersin! %100 başarı! 🏆'
            ]);
        } else if (percentage >= 80) {
            return Utils.randomChoice([
                'Harika gidiyorsun! 🌟',
                'Çok başarılısın! 👏',
                'Mükemmel performans! 🎯'
            ]);
        } else if (percentage >= 60) {
            return Utils.randomChoice([
                'İyi iş çıkarıyorsun! 👍',
                'Gayet iyi! Devam et! 💪',
                'Güzel ilerliyorsun! 🌱'
            ]);
        } else if (percentage >= 40) {
            return Utils.randomChoice([
                'Daha iyisini yapabilirsin! 💡',
                'Pratik yapmaya devam et! 📚',
                'Biraz daha çalışmalısın! 🎯'
            ]);
        } else {
            return Utils.randomChoice([
                'Pes etme, tekrar dene! 💪',
                'Pratik yapmaya devam et! 📖',
                'Her gün biraz daha iyi olacaksın! 🌱'
            ]);
        }
    },

    /**
     * Günlük ipucu al
     */
    getDailyTip() {
        const tips = [
            '💡 İpucu: Her gün 15 dakika pratik yaparsan, matematik çok daha kolay gelecek!',
            '🎯 İpucu: Zorlandığın konuları daha sık çalış, böylece daha güçlü olursun!',
            '⭐ İpucu: Adım adım çözümleri incelersen, problemleri çözmek kolaylaşır!',
            '🌟 İpucu: Her doğru cevap seni daha başarılı yapıyor. Devam et!',
            '📚 İpucu: Günlük meydan okumaları tamamlamayı unutma!',
            '🏆 İpucu: Rozetleri toplamak için farklı konularda çalış!',
            '💪 İpucu: Hatalarından öğren, her hata seni daha güçlü yapar!',
            '🎓 İpucu: Problemleri anlamak, ezberlemekkten daha önemlidir!'
        ];
        return Utils.randomChoice(tips);
    },

    /**
     * Ses efekti çal (basit beep)
     */
    playSound(type) {
        // Web Audio API ile basit ses efektleri
        // Tarayıcı desteği için try-catch kullanıyoruz
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);

            if (type === 'correct') {
                oscillator.frequency.value = 523.25; // C5 notası
                gainNode.gain.value = 0.3;
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.2);
            } else if (type === 'incorrect') {
                oscillator.frequency.value = 220; // A3 notası
                oscillator.type = 'triangle';
                gainNode.gain.value = 0.2;
                oscillator.start();
                oscillator.stop(audioContext.currentTime + 0.3);
            } else if (type === 'achievement') {
                // Basit melodi için
                const notes = [261.63, 329.63, 392.00]; // C4, E4, G4
                notes.forEach((freq, i) => {
                    const osc = audioContext.createOscillator();
                    const gain = audioContext.createGain();
                    osc.connect(gain);
                    gain.connect(audioContext.destination);
                    osc.frequency.value = freq;
                    gain.gain.value = 0.2;
                    osc.start(audioContext.currentTime + (i * 0.15));
                    osc.stop(audioContext.currentTime + (i * 0.15) + 0.2);
                });
            }
        } catch (error) {
            console.log('Audio not supported');
        }
    },

    /**
     * Debounce fonksiyonu
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Deep clone object
     */
    deepClone(obj) {
        return JSON.parse(JSON.stringify(obj));
    }
};

// Global erişim için
window.Utils = Utils;

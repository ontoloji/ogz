/**
 * Başarılar ve Rozetler Sistemi
 * Motivasyon ve ödüllendirme mekanizması
 */

const Achievements = {
    /**
     * Tüm rozetlerin listesi
     */
    badges: [
        // İlk Adımlar
        {
            id: 'first_question',
            name: 'İlk Adım',
            description: 'İlk soruyu cevapladın',
            icon: '🎯',
            condition: (profile) => profile.totalQuestions >= 1,
            points: 10
        },
        {
            id: 'first_correct',
            name: 'İlk Başarı',
            description: 'İlk doğru cevabın',
            icon: '✅',
            condition: (profile) => profile.correctQuestions >= 1,
            points: 10
        },

        // Soru Sayısı Rozetleri
        {
            id: 'questions_10',
            name: 'Yeni Başlayan',
            description: '10 soru cevapladın',
            icon: '🌱',
            condition: (profile) => profile.totalQuestions >= 10,
            points: 50
        },
        {
            id: 'questions_50',
            name: 'Çalışkan',
            description: '50 soru cevapladın',
            icon: '📚',
            condition: (profile) => profile.totalQuestions >= 50,
            points: 100
        },
        {
            id: 'questions_100',
            name: 'Azimli',
            description: '100 soru cevapladın',
            icon: '💪',
            condition: (profile) => profile.totalQuestions >= 100,
            points: 200
        },
        {
            id: 'questions_250',
            name: 'Üstün Çaba',
            description: '250 soru cevapladın',
            icon: '🌟',
            condition: (profile) => profile.totalQuestions >= 250,
            points: 500
        },
        {
            id: 'questions_500',
            name: 'Matematik Uzmanı',
            description: '500 soru cevapladın',
            icon: '🏆',
            condition: (profile) => profile.totalQuestions >= 500,
            points: 1000
        },

        // Başarı Oranı Rozetleri
        {
            id: 'accuracy_50',
            name: 'Güzel Başlangıç',
            description: '%50 doğruluk oranı (en az 20 soru)',
            icon: '👍',
            condition: (profile) => {
                return profile.totalQuestions >= 20 &&
                       UserProfile.getAccuracyRate(profile) >= 50;
            },
            points: 100
        },
        {
            id: 'accuracy_75',
            name: 'Harika Performans',
            description: '%75 doğruluk oranı (en az 50 soru)',
            icon: '⭐',
            condition: (profile) => {
                return profile.totalQuestions >= 50 &&
                       UserProfile.getAccuracyRate(profile) >= 75;
            },
            points: 300
        },
        {
            id: 'accuracy_90',
            name: 'Mükemmel',
            description: '%90 doğruluk oranı (en az 100 soru)',
            icon: '🌟',
            condition: (profile) => {
                return profile.totalQuestions >= 100 &&
                       UserProfile.getAccuracyRate(profile) >= 90;
            },
            points: 500
        },

        // Streak (Süreklilik) Rozetleri
        {
            id: 'streak_3',
            name: 'Kararlı',
            description: '3 gün üst üste pratik',
            icon: '🔥',
            condition: (profile) => profile.streak >= 3,
            points: 50
        },
        {
            id: 'streak_7',
            name: 'Sürekli',
            description: '7 gün üst üste pratik',
            icon: '🔥🔥',
            condition: (profile) => profile.streak >= 7,
            points: 150
        },
        {
            id: 'streak_30',
            name: 'Efsane Seri',
            description: '30 gün üst üste pratik',
            icon: '🔥🔥🔥',
            condition: (profile) => profile.streak >= 30,
            points: 1000
        },

        // Puan Rozetleri
        {
            id: 'points_100',
            name: 'Puan Toplayıcı',
            description: '100 puan topladın',
            icon: '💰',
            condition: (profile) => profile.points >= 100,
            points: 0
        },
        {
            id: 'points_500',
            name: 'Zengin',
            description: '500 puan topladın',
            icon: '💎',
            condition: (profile) => profile.points >= 500,
            points: 0
        },
        {
            id: 'points_1000',
            name: 'Hazine Avcısı',
            description: '1000 puan topladın',
            icon: '👑',
            condition: (profile) => profile.points >= 1000,
            points: 0
        },

        // Konu Bazlı Rozetler
        {
            id: 'fractions_master',
            name: 'Kesir Ustası',
            description: 'Kesirlerde %80+ başarı (en az 20 soru)',
            icon: '🍕',
            condition: (profile) => {
                const stats = UserProfile.getSubjectStats(profile, 'fractions');
                return stats.totalQuestions >= 20 &&
                       Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions) >= 80;
            },
            points: 200
        },
        {
            id: 'geometry_master',
            name: 'Geometri Kralı',
            description: 'Geometride %80+ başarı (en az 20 soru)',
            icon: '📐',
            condition: (profile) => {
                const stats = UserProfile.getSubjectStats(profile, 'geometry');
                return stats.totalQuestions >= 20 &&
                       Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions) >= 80;
            },
            points: 200
        },
        {
            id: 'equations_master',
            name: 'Denklem Çözücü',
            description: 'Denklemlerde %80+ başarı (en az 20 soru)',
            icon: '⚖️',
            condition: (profile) => {
                const stats = UserProfile.getSubjectStats(profile, 'equations');
                return stats.totalQuestions >= 20 &&
                       Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions) >= 80;
            },
            points: 200
        },

        // Özel Rozetler
        {
            id: 'perfect_10',
            name: 'Mükemmel 10',
            description: 'Üst üste 10 doğru cevap',
            icon: '💯',
            condition: (profile) => {
                // Bu kontrol uygulama içinde özel olarak yapılacak
                return profile.maxStreak >= 10;
            },
            points: 500
        },
        {
            id: 'night_owl',
            name: 'Gece Kuşu',
            description: 'Gece 22:00-06:00 arası pratik yap',
            icon: '🦉',
            condition: (profile) => profile.nightStudy === true,
            points: 100
        },
        {
            id: 'early_bird',
            name: 'Erken Kalkan',
            description: 'Sabah 05:00-08:00 arası pratik yap',
            icon: '🐦',
            condition: (profile) => profile.morningStudy === true,
            points: 100
        },
        {
            id: 'daily_champion',
            name: 'Günlük Şampiyon',
            description: 'Bir günde 50 soru çöz',
            icon: '🏅',
            condition: (profile) => {
                const today = Utils.getTodayKey();
                const activity = UserProfile.getDailyActivity(profile, today);
                return activity.questions >= 50;
            },
            points: 300
        },
        {
            id: 'all_subjects',
            name: 'Çok Yönlü',
            description: 'Tüm konularda en az 10 soru çöz',
            icon: '🌈',
            condition: (profile) => {
                const subjects = Subjects.list;
                return subjects.every(subject => {
                    const stats = UserProfile.getSubjectStats(profile, subject.id);
                    return stats.totalQuestions >= 10;
                });
            },
            points: 500
        },
        {
            id: 'speed_demon',
            name: 'Hız Canavarı',
            description: '1 dakikada 10 kolay soru çöz',
            icon: '⚡',
            condition: (profile) => profile.speedChallenge === true,
            points: 300
        },
        {
            id: 'patient_learner',
            name: 'Sabırlı Öğrenci',
            description: 'Toplam 10 saat çalışma süresi',
            icon: '⏰',
            condition: (profile) => profile.totalStudyTime >= 36000, // 10 saat
            points: 500
        }
    ],

    /**
     * Profildeki tüm rozetleri kontrol et
     */
    checkAll(profile) {
        const earnedBadges = [];

        this.badges.forEach(badge => {
            // Rozet zaten kazanılmış mı?
            if (profile.badges.includes(badge.id)) {
                return;
            }

            // Koşul sağlanıyor mu?
            if (badge.condition(profile)) {
                const isNew = UserProfile.addBadge(profile, badge.id);

                if (isNew) {
                    // Rozet puanını ekle
                    if (badge.points > 0) {
                        UserProfile.addPoints(profile, badge.points);
                    }

                    earnedBadges.push(badge);
                }
            }
        });

        return earnedBadges;
    },

    /**
     * ID'ye göre rozet bul
     */
    getBadgeById(id) {
        return this.badges.find(badge => badge.id === id);
    },

    /**
     * Kullanıcının kazandığı rozetleri al
     */
    getEarnedBadges(profile) {
        return this.badges.filter(badge => profile.badges.includes(badge.id));
    },

    /**
     * Kullanıcının kazanmadığı rozetleri al
     */
    getLockedBadges(profile) {
        return this.badges.filter(badge => !profile.badges.includes(badge.id));
    },

    /**
     * Yaklaşan rozetleri bul (yakın olan rozetler)
     */
    getUpcomingBadges(profile) {
        const upcoming = [];

        this.badges.forEach(badge => {
            if (profile.badges.includes(badge.id)) {
                return;
            }

            // Basit bir yakınlık hesabı
            let progress = 0;

            if (badge.id.startsWith('questions_')) {
                const target = parseInt(badge.id.split('_')[1]);
                progress = Utils.calculatePercentage(profile.totalQuestions, target);
            } else if (badge.id.startsWith('streak_')) {
                const target = parseInt(badge.id.split('_')[1]);
                progress = Utils.calculatePercentage(profile.streak, target);
            } else if (badge.id.startsWith('points_')) {
                const target = parseInt(badge.id.split('_')[1]);
                progress = Utils.calculatePercentage(profile.points, target);
            } else if (badge.id.startsWith('accuracy_')) {
                const target = parseInt(badge.id.split('_')[1]);
                const current = UserProfile.getAccuracyRate(profile);
                progress = Utils.calculatePercentage(current, target);
            }

            if (progress >= 50 && progress < 100) {
                upcoming.push({
                    ...badge,
                    progress
                });
            }
        });

        return upcoming.sort((a, b) => b.progress - a.progress);
    },

    /**
     * Rozet bildirimi göster
     */
    showBadgeNotification(badge) {
        Utils.showToast(`${badge.icon} ${badge.name} rozetini kazandın!`, 5000);
        Utils.playSound('achievement');

        // Confetti efekti
        const container = document.getElementById('app');
        if (container) {
            Utils.createConfetti(container);
        }
    },

    /**
     * Birden fazla rozet kazanıldığında
     */
    showMultipleBadges(badges) {
        if (badges.length === 0) return;

        badges.forEach((badge, index) => {
            setTimeout(() => {
                this.showBadgeNotification(badge);
            }, index * 2000);
        });
    },

    /**
     * Rozet kazanımını kontrol et ve göster
     */
    processNewBadges(profile) {
        const newBadges = this.checkAll(profile);

        if (newBadges.length > 0) {
            this.showMultipleBadges(newBadges);
        }

        return newBadges;
    },

    /**
     * Rozet ilerlemesi göster (progress bar için)
     */
    getBadgeProgress(profile, badgeId) {
        const badge = this.getBadgeById(badgeId);
        if (!badge) return 0;

        if (profile.badges.includes(badgeId)) {
            return 100;
        }

        // İlerleme hesapla
        if (badgeId.startsWith('questions_')) {
            const target = parseInt(badgeId.split('_')[1]);
            return Utils.calculatePercentage(profile.totalQuestions, target);
        } else if (badgeId.startsWith('streak_')) {
            const target = parseInt(badgeId.split('_')[1]);
            return Utils.calculatePercentage(profile.streak, target);
        } else if (badgeId.startsWith('points_')) {
            const target = parseInt(badgeId.split('_')[1]);
            return Utils.calculatePercentage(profile.points, target);
        }

        return 0;
    },

    /**
     * Motivasyon mesajı üret (rozet sayısına göre)
     */
    getMotivationByBadges(profile) {
        const badgeCount = profile.badges.length;

        if (badgeCount === 0) {
            return 'İlk rozetini kazanmak için sorulara başla! 🎯';
        } else if (badgeCount < 5) {
            return `${badgeCount} rozet kazandın! Devam et! 🌟`;
        } else if (badgeCount < 10) {
            return `Harikasın! ${badgeCount} rozet topladın! 🏆`;
        } else if (badgeCount < 20) {
            return `İnanılmaz! ${badgeCount} rozet! Gerçek bir şampiyonsun! 👑`;
        } else {
            return `Efsanesin! ${badgeCount} rozet! Matematik ustası! 🎓`;
        }
    },

    /**
     * Rozet kategorileri
     */
    getBadgesByCategory() {
        return {
            beginner: this.badges.filter(b =>
                b.id.startsWith('first_') ||
                b.id === 'questions_10'
            ),
            questions: this.badges.filter(b =>
                b.id.startsWith('questions_') && b.id !== 'questions_10'
            ),
            accuracy: this.badges.filter(b =>
                b.id.startsWith('accuracy_')
            ),
            streak: this.badges.filter(b =>
                b.id.startsWith('streak_')
            ),
            points: this.badges.filter(b =>
                b.id.startsWith('points_')
            ),
            subjects: this.badges.filter(b =>
                b.id.endsWith('_master')
            ),
            special: this.badges.filter(b =>
                !b.id.startsWith('first_') &&
                !b.id.startsWith('questions_') &&
                !b.id.startsWith('accuracy_') &&
                !b.id.startsWith('streak_') &&
                !b.id.startsWith('points_') &&
                !b.id.endsWith('_master')
            )
        };
    }
};

// Global erişim için
window.Achievements = Achievements;

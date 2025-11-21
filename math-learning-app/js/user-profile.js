/**
 * Kullanıcı Profili ve İlerleme Takibi
 * LocalStorage tabanlı kullanıcı veri yönetimi
 */

const UserProfile = {
    STORAGE_KEY: 'math_app_user_profile',

    /**
     * Varsayılan profil yapısı
     */
    defaultProfile: {
        username: 'Öğrenci',
        createdAt: null,
        lastLoginAt: null,
        points: 0,
        streak: 0,
        lastActivityDate: null,
        totalQuestions: 0,
        correctQuestions: 0,
        totalStudyTime: 0, // saniye cinsinden
        badges: [],
        subjectStats: {}, // { subjectId: { total, correct, time } }
        topicStats: {}, // { 'subjectId_topicId': { total, correct, time } }
        dailyActivity: {}, // { 'YYYY-MM-DD': { questions, correct, time } }
        weeklyGoal: 50, // haftada 50 soru hedefi
        preferences: {
            soundEnabled: true,
            animationsEnabled: true,
            difficulty: 'medium'
        }
    },

    /**
     * Profili yükle veya yeni oluştur
     */
    load() {
        const profile = Utils.loadFromStorage(this.STORAGE_KEY, null);

        if (!profile) {
            return this.create();
        }

        // Son giriş tarihini güncelle
        profile.lastLoginAt = new Date().toISOString();

        // Streak kontrolü
        this.updateStreak(profile);

        this.save(profile);
        return profile;
    },

    /**
     * Yeni profil oluştur
     */
    create() {
        const profile = Utils.deepClone(this.defaultProfile);
        profile.createdAt = new Date().toISOString();
        profile.lastLoginAt = new Date().toISOString();
        profile.lastActivityDate = Utils.getTodayKey();
        this.save(profile);
        return profile;
    },

    /**
     * Profili kaydet
     */
    save(profile) {
        Utils.saveToStorage(this.STORAGE_KEY, profile);
    },

    /**
     * Profili sıfırla
     */
    reset() {
        if (confirm('Tüm ilerlemeniz silinecek. Emin misiniz?')) {
            localStorage.removeItem(this.STORAGE_KEY);
            location.reload();
        }
    },

    /**
     * Kullanıcı adını güncelle
     */
    updateUsername(profile, username) {
        profile.username = username;
        this.save(profile);
    },

    /**
     * Puan ekle
     */
    addPoints(profile, points) {
        profile.points += points;
        this.save(profile);
    },

    /**
     * Streak güncelle
     */
    updateStreak(profile) {
        const today = Utils.getTodayKey();
        const lastActivity = profile.lastActivityDate;

        if (!lastActivity) {
            profile.streak = 1;
            profile.lastActivityDate = today;
            return;
        }

        const daysDiff = Utils.daysBetween(today, lastActivity);

        if (daysDiff === 0) {
            // Bugün zaten aktif
            return;
        } else if (daysDiff === 1) {
            // Dün aktifti, streak devam ediyor
            profile.streak += 1;
        } else {
            // Streak kırıldı
            profile.streak = 1;
        }

        profile.lastActivityDate = today;
    },

    /**
     * Soru cevaplandığında güncelle
     */
    recordAnswer(profile, question, isCorrect, timeSpent) {
        const { subjectId, topicId, difficulty } = question;

        // Genel istatistikler
        profile.totalQuestions += 1;
        if (isCorrect) {
            profile.correctQuestions += 1;

            // Zorluk seviyesine göre puan
            const points = difficulty === 'easy' ? 10 :
                          difficulty === 'medium' ? 20 : 30;
            this.addPoints(profile, points);
        }

        profile.totalStudyTime += timeSpent;

        // Konu bazlı istatistikler
        if (!profile.subjectStats[subjectId]) {
            profile.subjectStats[subjectId] = {
                totalQuestions: 0,
                correctQuestions: 0,
                timeSpent: 0
            };
        }

        profile.subjectStats[subjectId].totalQuestions += 1;
        if (isCorrect) {
            profile.subjectStats[subjectId].correctQuestions += 1;
        }
        profile.subjectStats[subjectId].timeSpent += timeSpent;

        // Alt konu bazlı istatistikler
        const topicKey = `${subjectId}_${topicId}`;
        if (!profile.topicStats[topicKey]) {
            profile.topicStats[topicKey] = {
                totalQuestions: 0,
                correctQuestions: 0,
                timeSpent: 0
            };
        }

        profile.topicStats[topicKey].totalQuestions += 1;
        if (isCorrect) {
            profile.topicStats[topicKey].correctQuestions += 1;
        }
        profile.topicStats[topicKey].timeSpent += timeSpent;

        // Günlük aktivite
        const today = Utils.getTodayKey();
        if (!profile.dailyActivity[today]) {
            profile.dailyActivity[today] = {
                questions: 0,
                correct: 0,
                timeSpent: 0
            };
        }

        profile.dailyActivity[today].questions += 1;
        if (isCorrect) {
            profile.dailyActivity[today].correct += 1;
        }
        profile.dailyActivity[today].timeSpent += timeSpent;

        // Streak güncelle
        this.updateStreak(profile);

        this.save(profile);
    },

    /**
     * Rozet ekle
     */
    addBadge(profile, badgeId) {
        if (!profile.badges.includes(badgeId)) {
            profile.badges.push(badgeId);
            this.save(profile);
            return true;
        }
        return false;
    },

    /**
     * Konu istatistiklerini al
     */
    getSubjectStats(profile, subjectId) {
        return profile.subjectStats[subjectId] || {
            totalQuestions: 0,
            correctQuestions: 0,
            timeSpent: 0
        };
    },

    /**
     * Alt konu istatistiklerini al
     */
    getTopicStats(profile, subjectId, topicId) {
        const key = `${subjectId}_${topicId}`;
        return profile.topicStats[key] || {
            totalQuestions: 0,
            correctQuestions: 0,
            timeSpent: 0
        };
    },

    /**
     * Günlük aktiviteyi al
     */
    getDailyActivity(profile, date) {
        return profile.dailyActivity[date] || {
            questions: 0,
            correct: 0,
            timeSpent: 0
        };
    },

    /**
     * Son 7 günün aktivitesini al
     */
    getWeeklyActivity(profile) {
        const activities = [];
        const today = new Date();

        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            const dateKey = Utils.getTodayKey.call({ getFullYear: () => date.getFullYear(), getMonth: () => date.getMonth(), getDate: () => date.getDate() });

            // Doğru tarih formatı oluştur
            const year = date.getFullYear();
            const month = (date.getMonth() + 1).toString().padStart(2, '0');
            const day = date.getDate().toString().padStart(2, '0');
            const formattedDate = `${year}-${month}-${day}`;

            const activity = this.getDailyActivity(profile, formattedDate);

            activities.push({
                date: formattedDate,
                dayName: ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'][date.getDay()],
                ...activity
            });
        }

        return activities;
    },

    /**
     * Toplam doğruluk oranını hesapla
     */
    getAccuracyRate(profile) {
        if (profile.totalQuestions === 0) return 0;
        return Utils.calculatePercentage(profile.correctQuestions, profile.totalQuestions);
    },

    /**
     * Konu doğruluk oranını hesapla
     */
    getSubjectAccuracy(profile, subjectId) {
        const stats = this.getSubjectStats(profile, subjectId);
        if (stats.totalQuestions === 0) return 0;
        return Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions);
    },

    /**
     * Haftalık hedef ilerlemesini al
     */
    getWeeklyProgress(profile) {
        const weeklyActivity = this.getWeeklyActivity(profile);
        const totalQuestions = weeklyActivity.reduce((sum, day) => sum + day.questions, 0);
        const percentage = Utils.calculatePercentage(totalQuestions, profile.weeklyGoal);

        return {
            current: totalQuestions,
            goal: profile.weeklyGoal,
            percentage: Math.min(percentage, 100)
        };
    },

    /**
     * Tamamlanan konu sayısını al (başarı oranı %80 üzeri)
     */
    getCompletedTopicsCount(profile) {
        let count = 0;

        Object.keys(profile.topicStats).forEach(key => {
            const stats = profile.topicStats[key];
            if (stats.totalQuestions >= 10) {
                const accuracy = Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions);
                if (accuracy >= 80) {
                    count++;
                }
            }
        });

        return count;
    },

    /**
     * Günlük meydan okumayı kontrol et
     */
    isDailyChallengeCompleted(profile) {
        const today = Utils.getTodayKey();
        const todayActivity = this.getDailyActivity(profile, today);
        return todayActivity.questions >= 5; // Günde en az 5 soru
    },

    /**
     * Seviye hesapla (100 puan = 1 seviye)
     */
    getLevel(profile) {
        return Math.floor(profile.points / 100) + 1;
    },

    /**
     * Sonraki seviyeye kalan puanı hesapla
     */
    getPointsToNextLevel(profile) {
        const currentLevel = this.getLevel(profile);
        const pointsForNextLevel = currentLevel * 100;
        return pointsForNextLevel - profile.points;
    },

    /**
     * Seviye içindeki ilerlemeyi hesapla (yüzde)
     */
    getLevelProgress(profile) {
        const currentLevelPoints = (this.getLevel(profile) - 1) * 100;
        const pointsInLevel = profile.points - currentLevelPoints;
        return Utils.calculatePercentage(pointsInLevel, 100);
    },

    /**
     * En çok çalışılan konuyu bul
     */
    getMostStudiedSubject(profile) {
        let maxQuestions = 0;
        let topSubjectId = null;

        Object.keys(profile.subjectStats).forEach(subjectId => {
            const stats = profile.subjectStats[subjectId];
            if (stats.totalQuestions > maxQuestions) {
                maxQuestions = stats.totalQuestions;
                topSubjectId = subjectId;
            }
        });

        if (topSubjectId) {
            const subject = Subjects.getSubjectById(topSubjectId);
            return {
                ...subject,
                questionsAnswered: maxQuestions
            };
        }

        return null;
    },

    /**
     * En başarılı konuyu bul
     */
    getMostSuccessfulSubject(profile) {
        let maxAccuracy = 0;
        let topSubjectId = null;

        Object.keys(profile.subjectStats).forEach(subjectId => {
            const stats = profile.subjectStats[subjectId];
            if (stats.totalQuestions >= 10) { // En az 10 soru çözülmüş olmalı
                const accuracy = Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions);
                if (accuracy > maxAccuracy) {
                    maxAccuracy = accuracy;
                    topSubjectId = subjectId;
                }
            }
        });

        if (topSubjectId) {
            const subject = Subjects.getSubjectById(topSubjectId);
            return {
                ...subject,
                accuracy: maxAccuracy
            };
        }

        return null;
    },

    /**
     * Profil özetini al (Ebeveyn raporu için)
     */
    getSummary(profile) {
        return {
            username: profile.username,
            level: this.getLevel(profile),
            points: profile.points,
            streak: profile.streak,
            totalQuestions: profile.totalQuestions,
            correctQuestions: profile.correctQuestions,
            accuracy: this.getAccuracyRate(profile),
            studyTime: profile.totalStudyTime,
            studyTimeFormatted: Utils.formatTime(profile.totalStudyTime),
            badgeCount: profile.badges.length,
            completedTopics: this.getCompletedTopicsCount(profile),
            weeklyProgress: this.getWeeklyProgress(profile),
            mostStudiedSubject: this.getMostStudiedSubject(profile),
            mostSuccessfulSubject: this.getMostSuccessfulSubject(profile),
            createdAt: profile.createdAt,
            lastLoginAt: profile.lastLoginAt
        };
    }
};

// Global erişim için
window.UserProfile = UserProfile;

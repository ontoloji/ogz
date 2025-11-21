/**
 * Matematik Konuları
 * Ortaokul seviyesi matematik konuları ve alt konuları
 */

const Subjects = {
    /**
     * Tüm matematik konularının listesi
     */
    list: [
        {
            id: 'fractions',
            name: 'Kesirler',
            icon: '🍕',
            description: 'Kesirlerle toplama, çıkarma, çarpma ve bölme',
            color: '#EC4899',
            topics: [
                { id: 'fraction_basics', name: 'Kesir Kavramı', difficulty: 'easy' },
                { id: 'fraction_addition', name: 'Kesirlerle Toplama', difficulty: 'easy' },
                { id: 'fraction_subtraction', name: 'Kesirlerle Çıkarma', difficulty: 'easy' },
                { id: 'fraction_multiplication', name: 'Kesirlerle Çarpma', difficulty: 'medium' },
                { id: 'fraction_division', name: 'Kesirlerle Bölme', difficulty: 'medium' },
                { id: 'mixed_fractions', name: 'Tam Sayılı Kesirler', difficulty: 'medium' },
                { id: 'fraction_simplify', name: 'Kesir Sadeleştirme', difficulty: 'easy' },
                { id: 'fraction_comparison', name: 'Kesirleri Karşılaştırma', difficulty: 'easy' }
            ]
        },
        {
            id: 'decimals',
            name: 'Ondalık Sayılar',
            icon: '🔢',
            description: 'Ondalık sayılarla işlemler',
            color: '#3B82F6',
            topics: [
                { id: 'decimal_basics', name: 'Ondalık Sayı Kavramı', difficulty: 'easy' },
                { id: 'decimal_addition', name: 'Ondalık Sayılarla Toplama', difficulty: 'easy' },
                { id: 'decimal_subtraction', name: 'Ondalık Sayılarla Çıkarma', difficulty: 'easy' },
                { id: 'decimal_multiplication', name: 'Ondalık Sayılarla Çarpma', difficulty: 'medium' },
                { id: 'decimal_division', name: 'Ondalık Sayılarla Bölme', difficulty: 'medium' },
                { id: 'decimal_to_fraction', name: 'Ondalık-Kesir Dönüşümü', difficulty: 'medium' }
            ]
        },
        {
            id: 'equations',
            name: 'Denklemler',
            icon: '⚖️',
            description: 'Basit ve birinci dereceden denklemler',
            color: '#10B981',
            topics: [
                { id: 'equation_basics', name: 'Denklem Kavramı', difficulty: 'easy' },
                { id: 'simple_equations', name: 'Basit Denklemler', difficulty: 'easy' },
                { id: 'linear_equations', name: 'Birinci Derece Denklemler', difficulty: 'medium' },
                { id: 'equation_word_problems', name: 'Denklem Problemleri', difficulty: 'hard' },
                { id: 'two_variable_equations', name: 'İki Bilinmeyenli Denklemler', difficulty: 'hard' }
            ]
        },
        {
            id: 'geometry',
            name: 'Geometri',
            icon: '📐',
            description: 'Şekiller, açılar, alan ve çevre hesaplama',
            color: '#F59E0B',
            topics: [
                { id: 'angles', name: 'Açılar', difficulty: 'easy' },
                { id: 'triangles', name: 'Üçgenler', difficulty: 'medium' },
                { id: 'quadrilaterals', name: 'Dörtgenler', difficulty: 'medium' },
                { id: 'circles', name: 'Daireler', difficulty: 'medium' },
                { id: 'perimeter', name: 'Çevre Hesaplama', difficulty: 'easy' },
                { id: 'area', name: 'Alan Hesaplama', difficulty: 'medium' },
                { id: 'volume', name: 'Hacim Hesaplama', difficulty: 'hard' },
                { id: 'pythagoras', name: 'Pisagor Teoremi', difficulty: 'hard' }
            ]
        },
        {
            id: 'percentages',
            name: 'Yüzdeler',
            icon: '%',
            description: 'Yüzde hesaplamaları ve problemler',
            color: '#8B5CF6',
            topics: [
                { id: 'percentage_basics', name: 'Yüzde Kavramı', difficulty: 'easy' },
                { id: 'percentage_calculation', name: 'Yüzde Hesaplama', difficulty: 'easy' },
                { id: 'percentage_problems', name: 'Yüzde Problemleri', difficulty: 'medium' },
                { id: 'discount_problems', name: 'İndirim Hesaplamaları', difficulty: 'medium' },
                { id: 'interest_problems', name: 'Faiz Hesaplamaları', difficulty: 'hard' }
            ]
        },
        {
            id: 'ratios',
            name: 'Orantı',
            icon: '⚖️',
            description: 'Oran ve orantı problemleri',
            color: '#EF4444',
            topics: [
                { id: 'ratio_basics', name: 'Oran Kavramı', difficulty: 'easy' },
                { id: 'direct_proportion', name: 'Doğru Orantı', difficulty: 'medium' },
                { id: 'inverse_proportion', name: 'Ters Orantı', difficulty: 'medium' },
                { id: 'ratio_problems', name: 'Orantı Problemleri', difficulty: 'hard' }
            ]
        },
        {
            id: 'integers',
            name: 'Tam Sayılar',
            icon: '➕➖',
            description: 'Pozitif ve negatif sayılarla işlemler',
            color: '#06B6D4',
            topics: [
                { id: 'integer_basics', name: 'Tam Sayı Kavramı', difficulty: 'easy' },
                { id: 'integer_addition', name: 'Tam Sayılarla Toplama', difficulty: 'easy' },
                { id: 'integer_subtraction', name: 'Tam Sayılarla Çıkarma', difficulty: 'easy' },
                { id: 'integer_multiplication', name: 'Tam Sayılarla Çarpma', difficulty: 'medium' },
                { id: 'integer_division', name: 'Tam Sayılarla Bölme', difficulty: 'medium' },
                { id: 'integer_operations', name: 'Karışık İşlemler', difficulty: 'hard' }
            ]
        },
        {
            id: 'powers',
            name: 'Üslü Sayılar',
            icon: '²',
            description: 'Üslü sayılar ve köklü sayılar',
            color: '#F97316',
            topics: [
                { id: 'power_basics', name: 'Üs Kavramı', difficulty: 'easy' },
                { id: 'power_operations', name: 'Üslü Sayılarla İşlemler', difficulty: 'medium' },
                { id: 'square_numbers', name: 'Kare Sayılar', difficulty: 'easy' },
                { id: 'square_roots', name: 'Karekök', difficulty: 'medium' },
                { id: 'cube_numbers', name: 'Küp Sayılar', difficulty: 'medium' },
                { id: 'scientific_notation', name: 'Bilimsel Gösterim', difficulty: 'hard' }
            ]
        },
        {
            id: 'sets',
            name: 'Kümeler',
            icon: '{ }',
            description: 'Küme işlemleri ve Venn şemaları',
            color: '#EC4899',
            topics: [
                { id: 'set_basics', name: 'Küme Kavramı', difficulty: 'easy' },
                { id: 'set_operations', name: 'Küme İşlemleri', difficulty: 'medium' },
                { id: 'venn_diagrams', name: 'Venn Şemaları', difficulty: 'medium' },
                { id: 'set_problems', name: 'Küme Problemleri', difficulty: 'hard' }
            ]
        },
        {
            id: 'statistics',
            name: 'İstatistik',
            icon: '📊',
            description: 'Ortalama, ortanca, mod ve grafik okuma',
            color: '#14B8A6',
            topics: [
                { id: 'mean', name: 'Aritmetik Ortalama', difficulty: 'easy' },
                { id: 'median', name: 'Ortanca', difficulty: 'easy' },
                { id: 'mode', name: 'Tepe Değer (Mod)', difficulty: 'easy' },
                { id: 'range', name: 'Değişim Aralığı', difficulty: 'easy' },
                { id: 'graphs', name: 'Grafik Okuma', difficulty: 'medium' },
                { id: 'probability', name: 'Olasılık', difficulty: 'hard' }
            ]
        }
    ],

    /**
     * ID'ye göre konu bul
     */
    getSubjectById(id) {
        return this.list.find(subject => subject.id === id);
    },

    /**
     * Zorluk seviyesine göre konuları filtrele
     */
    getTopicsByDifficulty(subjectId, difficulty) {
        const subject = this.getSubjectById(subjectId);
        if (!subject) return [];
        return subject.topics.filter(topic => topic.difficulty === difficulty);
    },

    /**
     * Alt konuyu bul
     */
    getTopicById(subjectId, topicId) {
        const subject = this.getSubjectById(subjectId);
        if (!subject) return null;
        return subject.topics.find(topic => topic.id === topicId);
    },

    /**
     * Tüm alt konuları getir
     */
    getAllTopics(subjectId) {
        const subject = this.getSubjectById(subjectId);
        return subject ? subject.topics : [];
    },

    /**
     * Rastgele konu seç
     */
    getRandomSubject() {
        return Utils.randomChoice(this.list);
    },

    /**
     * Rastgele alt konu seç
     */
    getRandomTopic(subjectId, difficulty = null) {
        const subject = this.getSubjectById(subjectId);
        if (!subject) return null;

        let topics = subject.topics;
        if (difficulty) {
            topics = topics.filter(topic => topic.difficulty === difficulty);
        }

        return Utils.randomChoice(topics);
    },

    /**
     * Zorluk seviyesi emoji'si al
     */
    getDifficultyEmoji(difficulty) {
        const emojis = {
            'easy': '🌱',
            'medium': '🌿',
            'hard': '🌳'
        };
        return emojis[difficulty] || '🌱';
    },

    /**
     * Zorluk seviyesi adı al
     */
    getDifficultyName(difficulty) {
        const names = {
            'easy': 'Kolay',
            'medium': 'Orta',
            'hard': 'Zor'
        };
        return names[difficulty] || 'Kolay';
    },

    /**
     * Konu ilerlemesini hesapla
     */
    calculateSubjectProgress(subjectId, userProfile) {
        const subject = this.getSubjectById(subjectId);
        if (!subject) return 0;

        const stats = userProfile.getSubjectStats(subjectId);
        if (!stats || stats.totalQuestions === 0) return 0;

        return Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions);
    },

    /**
     * Tüm konuların ilerlemesini al
     */
    getAllProgress(userProfile) {
        return this.list.map(subject => ({
            id: subject.id,
            name: subject.name,
            icon: subject.icon,
            progress: this.calculateSubjectProgress(subject.id, userProfile)
        }));
    },

    /**
     * Zayıf konuları tespit et (başarı oranı %60'ın altında olanlar)
     */
    getWeakTopics(userProfile, threshold = 60) {
        const weakTopics = [];

        this.list.forEach(subject => {
            subject.topics.forEach(topic => {
                const stats = userProfile.getTopicStats(subject.id, topic.id);
                if (stats && stats.totalQuestions >= 5) {
                    const successRate = Utils.calculatePercentage(
                        stats.correctQuestions,
                        stats.totalQuestions
                    );

                    if (successRate < threshold) {
                        weakTopics.push({
                            subjectId: subject.id,
                            subjectName: subject.name,
                            topicId: topic.id,
                            topicName: topic.name,
                            successRate: successRate,
                            questionsAnswered: stats.totalQuestions
                        });
                    }
                }
            });
        });

        // Başarı oranına göre sırala (en düşükten en yükseğe)
        return weakTopics.sort((a, b) => a.successRate - b.successRate);
    },

    /**
     * Güçlü konuları tespit et (başarı oranı %80'in üstünde olanlar)
     */
    getStrongTopics(userProfile, threshold = 80) {
        const strongTopics = [];

        this.list.forEach(subject => {
            subject.topics.forEach(topic => {
                const stats = userProfile.getTopicStats(subject.id, topic.id);
                if (stats && stats.totalQuestions >= 5) {
                    const successRate = Utils.calculatePercentage(
                        stats.correctQuestions,
                        stats.totalQuestions
                    );

                    if (successRate >= threshold) {
                        strongTopics.push({
                            subjectId: subject.id,
                            subjectName: subject.name,
                            topicId: topic.id,
                            topicName: topic.name,
                            successRate: successRate,
                            questionsAnswered: stats.totalQuestions
                        });
                    }
                }
            });
        });

        // Başarı oranına göre sırala (en yüksekten en düşüğe)
        return strongTopics.sort((a, b) => b.successRate - a.successRate);
    }
};

// Global erişim için
window.Subjects = Subjects;

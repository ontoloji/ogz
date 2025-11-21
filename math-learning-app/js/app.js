/**
 * Ana Uygulama
 * Matematik Öğrenme Uygulaması - Ana Kontrol
 */

const App = {
    // Uygulama durumu
    state: {
        currentProfile: null,
        currentScreen: 'home',
        currentSubject: null,
        currentDifficulty: 'easy',
        currentQuestions: [],
        currentQuestionIndex: 0,
        sessionStartTime: null,
        questionStartTime: null,
        sessionCorrectAnswers: 0
    },

    /**
     * Uygulamayı başlat
     */
    init() {
        // Profili yükle
        this.state.currentProfile = UserProfile.load();

        // UI'ı güncelle
        this.updateUI();

        // Event listener'ları ekle
        this.attachEventListeners();

        // Günlük ipucu göster
        this.showDailyTip();

        // Rozetleri kontrol et
        Achievements.processNewBadges(this.state.currentProfile);

        console.log('Matematik Öğrenme Uygulaması başlatıldı! 🎓');
    },

    /**
     * UI'ı güncelle
     */
    updateUI() {
        const profile = this.state.currentProfile;

        // Header bilgileri
        document.getElementById('user-points').textContent = Utils.formatNumber(profile.points);
        document.getElementById('user-streak').textContent = profile.streak;
        document.getElementById('user-badges').textContent = profile.badges.length;

        // Karşılama mesajı
        const hour = new Date().getHours();
        let greeting = 'Merhaba';
        if (hour < 12) greeting = 'Günaydın';
        else if (hour < 18) greeting = 'İyi günler';
        else greeting = 'İyi akşamlar';

        document.getElementById('welcome-message').textContent = `${greeting}, ${profile.username}! 👋`;
    },

    /**
     * Günlük ipucu göster
     */
    showDailyTip() {
        const tip = Utils.getDailyTip();
        document.getElementById('daily-tip').textContent = tip;
    },

    /**
     * Event listener'ları ekle
     */
    attachEventListeners() {
        // Ana menü kartları
        document.querySelectorAll('.menu-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleMenuAction(action);
            });
        });

        // Geri butonları
        document.querySelectorAll('.back-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.showScreen('home');
            });
        });

        // Zorluk seçimi
        document.querySelectorAll('.difficulty-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.difficulty-btn').forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.state.currentDifficulty = e.currentTarget.dataset.level;
                this.renderSubjects();
            });
        });

        // Profil butonu
        document.getElementById('profile-btn').addEventListener('click', () => {
            this.showProfileModal();
        });

        // Modal kapat
        document.querySelectorAll('.close-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
            });
        });

        // Kullanıcı adı kaydet
        document.getElementById('save-username-btn').addEventListener('click', () => {
            const username = document.getElementById('username-input').value.trim();
            if (username) {
                UserProfile.updateUsername(this.state.currentProfile, username);
                this.updateUI();
                Utils.showToast('İsmin kaydedildi! 👍');
            }
        });

        // Ebeveyn raporu
        document.getElementById('parent-report-btn').addEventListener('click', () => {
            document.querySelectorAll('.modal').forEach(m => m.classList.add('hidden'));
            this.showParentReport();
        });

        // İlerlemeyi sıfırla
        document.getElementById('reset-progress-btn').addEventListener('click', () => {
            UserProfile.reset();
        });

        // Raporu indir
        document.getElementById('export-report-btn').addEventListener('click', () => {
            Stats.exportReport(this.state.currentProfile);
        });

        // Soru cevap alanı
        document.getElementById('check-btn').addEventListener('click', () => {
            this.checkAnswer();
        });

        document.getElementById('hint-btn').addEventListener('click', () => {
            this.showHint();
        });

        document.getElementById('solution-btn').addEventListener('click', () => {
            this.showSolution();
        });
    },

    /**
     * Menü aksiyonlarını işle
     */
    handleMenuAction(action) {
        switch (action) {
            case 'start-learning':
            case 'practice':
                this.startPractice();
                break;
            case 'daily-challenge':
                this.startDailyChallenge();
                break;
            case 'progress':
                this.showProgress();
                break;
            case 'weak-topics':
                this.showWeakTopics();
                break;
            case 'achievements':
                this.showAchievements();
                break;
        }
    },

    /**
     * Ekran göster
     */
    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        document.getElementById(`${screenId}-screen`).classList.add('active');
        this.state.currentScreen = screenId;
    },

    /**
     * Pratik başlat
     */
    startPractice() {
        this.showScreen('subject');
        this.renderSubjects();
    },

    /**
     * Konuları render et
     */
    renderSubjects() {
        const container = document.getElementById('subjects-container');
        container.innerHTML = '';

        Subjects.list.forEach((subject, index) => {
            const card = document.createElement('div');
            card.className = `subject-card card-stagger-${(index % 6) + 1}`;
            card.style.cursor = 'pointer';

            const progress = Subjects.calculateSubjectProgress(subject.id, this.state.currentProfile);

            card.innerHTML = `
                <div class="subject-icon">${subject.icon}</div>
                <div class="subject-title">${subject.name}</div>
                <div class="subject-description" style="font-size: 0.9rem; color: #64748B; margin: 8px 0;">
                    ${subject.description}
                </div>
                <div class="subject-progress">
                    <div class="subject-progress-text">${progress}% tamamlandı</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%; background: ${subject.color};"></div>
                    </div>
                </div>
            `;

            card.addEventListener('click', () => {
                this.selectSubject(subject.id);
            });

            container.appendChild(card);
        });
    },

    /**
     * Konu seç ve soruları başlat
     */
    selectSubject(subjectId) {
        this.state.currentSubject = subjectId;
        const subject = Subjects.getSubjectById(subjectId);
        const topic = Subjects.getRandomTopic(subjectId, this.state.currentDifficulty);

        if (!topic) {
            alert('Bu zorluk seviyesinde konu bulunamadı!');
            return;
        }

        // 10 soruluk set oluştur
        this.state.currentQuestions = QuestionGenerator.generateQuestionSet(
            subjectId,
            topic.id,
            this.state.currentDifficulty,
            10
        );

        this.state.currentQuestionIndex = 0;
        this.state.sessionStartTime = Date.now();
        this.state.sessionCorrectAnswers = 0;

        this.showScreen('question');
        this.showQuestion();
    },

    /**
     * Soruyu göster
     */
    showQuestion() {
        const question = this.state.currentQuestions[this.state.currentQuestionIndex];
        const index = this.state.currentQuestionIndex + 1;
        const total = this.state.currentQuestions.length;

        // İlerleme
        document.getElementById('question-counter').textContent = `Soru ${index}/${total}`;
        document.getElementById('progress-fill').style.width = `${(index / total) * 100}%`;

        // Konu başlığı
        const subject = Subjects.getSubjectById(question.subjectId);
        const topic = Subjects.getTopicById(question.subjectId, question.topicId);
        document.getElementById('question-topic').textContent = `${subject.name} - ${topic.name}`;

        // Soru içeriği
        document.getElementById('question-content').innerHTML = question.question;

        // Cevap alanı
        const answerArea = document.getElementById('answer-area');
        answerArea.innerHTML = '';

        if (question.type === 'multiple-choice') {
            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'answer-options';

            question.options.forEach(option => {
                const btn = document.createElement('button');
                btn.className = 'answer-option';
                btn.textContent = option;
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.answer-option').forEach(b => {
                        b.classList.remove('selected');
                    });
                    btn.classList.add('selected');
                });
                optionsDiv.appendChild(btn);
            });

            answerArea.appendChild(optionsDiv);
        } else {
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'answer-input';
            input.placeholder = 'Cevabını yaz...';
            input.id = 'user-answer-input';
            answerArea.appendChild(input);

            // Enter tuşu ile cevapla
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.checkAnswer();
                }
            });
        }

        // Görselleştirme
        if (question.visualizationType && question.visualizationData) {
            const vizArea = document.getElementById('visualization-area');
            Visualizations.create(vizArea, question.visualizationType, question.visualizationData);
            vizArea.classList.remove('hidden');
        } else {
            document.getElementById('visualization-area').classList.add('hidden');
        }

        // Geri bildirimi temizle
        document.getElementById('feedback-area').classList.add('hidden');
        document.getElementById('solution-steps').classList.add('hidden');

        // Soru başlangıç zamanı
        this.state.questionStartTime = Date.now();
    },

    /**
     * Cevabı kontrol et
     */
    checkAnswer() {
        const question = this.state.currentQuestions[this.state.currentQuestionIndex];
        let userAnswer;

        if (question.type === 'multiple-choice') {
            const selected = document.querySelector('.answer-option.selected');
            if (!selected) {
                alert('Lütfen bir seçenek seç!');
                return;
            }
            userAnswer = selected.textContent;
        } else {
            const input = document.getElementById('user-answer-input');
            userAnswer = input.value.trim();
            if (!userAnswer) {
                alert('Lütfen bir cevap gir!');
                return;
            }
        }

        const isCorrect = QuestionGenerator.checkAnswer(question, userAnswer);
        const timeSpent = Math.floor((Date.now() - this.state.questionStartTime) / 1000);

        // Profili güncelle
        UserProfile.recordAnswer(this.state.currentProfile, question, isCorrect, timeSpent);

        // Session istatistikleri
        if (isCorrect) {
            this.state.sessionCorrectAnswers++;
        }

        // Geri bildirim göster
        this.showFeedback(isCorrect);

        // Ses efekti
        Utils.playSound(isCorrect ? 'correct' : 'incorrect');

        // UI güncelle
        this.updateUI();

        // Rozetleri kontrol et
        setTimeout(() => {
            Achievements.processNewBadges(this.state.currentProfile);
        }, 1000);

        // Sonraki soru butonu
        setTimeout(() => {
            if (this.state.currentQuestionIndex < this.state.currentQuestions.length - 1) {
                if (confirm('Sonraki soruya geçelim mi?')) {
                    this.nextQuestion();
                }
            } else {
                this.finishSession();
            }
        }, 2000);
    },

    /**
     * Geri bildirim göster
     */
    showFeedback(isCorrect) {
        const feedbackArea = document.getElementById('feedback-area');
        feedbackArea.classList.remove('hidden', 'correct', 'incorrect');

        if (isCorrect) {
            feedbackArea.classList.add('correct');
            const messages = [
                '🎉 Harika! Doğru cevap!',
                '⭐ Süpersin! Doğru!',
                '🌟 Mükemmel! Tam isabet!',
                '👏 Bravo! Doğru bildin!'
            ];
            feedbackArea.textContent = Utils.randomChoice(messages);
            feedbackArea.classList.add('success-animation');
        } else {
            feedbackArea.classList.add('incorrect');
            feedbackArea.textContent = '❌ Yanlış cevap. Tekrar dene!';
            feedbackArea.classList.add('incorrect-answer-effect');
        }
    },

    /**
     * İpucu göster
     */
    showHint() {
        const question = this.state.currentQuestions[this.state.currentQuestionIndex];
        alert(`💡 İpucu: ${question.hint}`);
    },

    /**
     * Çözümü göster
     */
    showSolution() {
        const question = this.state.currentQuestions[this.state.currentQuestionIndex];
        const solutionArea = document.getElementById('solution-steps');

        solutionArea.innerHTML = '<h4>📖 Adım Adım Çözüm</h4>';

        question.solution.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'solution-step';
            stepDiv.innerHTML = `<strong>Adım ${index + 1}:</strong> ${step}`;
            solutionArea.appendChild(stepDiv);
        });

        solutionArea.classList.remove('hidden');
    },

    /**
     * Sonraki soru
     */
    nextQuestion() {
        this.state.currentQuestionIndex++;
        this.showQuestion();
    },

    /**
     * Oturumu bitir
     */
    finishSession() {
        const totalQuestions = this.state.currentQuestions.length;
        const correctAnswers = this.state.sessionCorrectAnswers;
        const percentage = Utils.calculatePercentage(correctAnswers, totalQuestions);
        const totalTime = Math.floor((Date.now() - this.state.sessionStartTime) / 1000);

        const motivationMessage = Utils.getMotivationMessage(correctAnswers, totalQuestions);

        alert(`
🎓 Oturum Tamamlandı!

✅ Doğru: ${correctAnswers}/${totalQuestions}
📊 Başarı Oranı: %${percentage}
⏱️ Süre: ${Utils.formatTime(totalTime)}

${motivationMessage}
        `);

        // Confetti efekti (eğer başarılıysa)
        if (percentage >= 80) {
            const container = document.getElementById('app');
            Utils.createConfetti(container);
        }

        this.showScreen('home');
    },

    /**
     * Günlük meydan okuma başlat
     */
    startDailyChallenge() {
        this.state.currentQuestions = QuestionGenerator.generateDailyChallenge();
        this.state.currentQuestionIndex = 0;
        this.state.sessionStartTime = Date.now();
        this.state.sessionCorrectAnswers = 0;

        this.showScreen('question');
        this.showQuestion();
    },

    /**
     * İlerleme durumunu göster
     */
    showProgress() {
        this.showScreen('stats');
        Stats.updateStatsScreen(this.state.currentProfile);
    },

    /**
     * Zayıf konuları göster
     */
    showWeakTopics() {
        this.showScreen('stats');
        Stats.updateStatsScreen(this.state.currentProfile);

        // Zayıf konular bölümüne scroll
        setTimeout(() => {
            document.querySelector('.weak-topics-section').scrollIntoView({
                behavior: 'smooth'
            });
        }, 300);
    },

    /**
     * Başarıları göster
     */
    showAchievements() {
        this.showScreen('achievements');
        this.renderAchievements();
    },

    /**
     * Rozetleri render et
     */
    renderAchievements() {
        const container = document.getElementById('badges-grid');
        container.innerHTML = '';

        const earnedBadges = Achievements.getEarnedBadges(this.state.currentProfile);
        const lockedBadges = Achievements.getLockedBadges(this.state.currentProfile);

        // Toplam rozet sayısı
        document.getElementById('total-badges-count').textContent = earnedBadges.length;

        // Kazanılan rozetler
        earnedBadges.forEach(badge => {
            const badgeDiv = document.createElement('div');
            badgeDiv.className = 'badge-item';
            badgeDiv.innerHTML = `
                <div class="badge-icon">${badge.icon}</div>
                <div class="badge-name">${badge.name}</div>
                <div class="badge-description">${badge.description}</div>
            `;
            container.appendChild(badgeDiv);
        });

        // Kilitli rozetler
        lockedBadges.forEach(badge => {
            const badgeDiv = document.createElement('div');
            badgeDiv.className = 'badge-item locked';
            badgeDiv.innerHTML = `
                <div class="badge-icon">🔒</div>
                <div class="badge-name">${badge.name}</div>
                <div class="badge-description">${badge.description}</div>
            `;
            badgeDiv.title = 'Henüz kazanılmadı';
            container.appendChild(badgeDiv);
        });
    },

    /**
     * Profil modalını göster
     */
    showProfileModal() {
        const modal = document.getElementById('profile-modal');
        modal.classList.remove('hidden');

        document.getElementById('username-input').value = this.state.currentProfile.username;
    },

    /**
     * Ebeveyn raporunu göster
     */
    showParentReport() {
        this.showScreen('parent-report');
        Stats.generateParentReport(this.state.currentProfile);
    }
};

// Sayfa yüklendiğinde uygulamayı başlat
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Global erişim için
window.App = App;

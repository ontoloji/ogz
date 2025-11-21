/**
 * İstatistikler ve Raporlama
 * Kullanıcı performans analizi ve ebeveyn raporu
 */

const Stats = {
    /**
     * İstatistik ekranını güncelle
     */
    updateStatsScreen(profile) {
        // Genel istatistikler
        document.getElementById('total-questions').textContent = Utils.formatNumber(profile.totalQuestions);
        document.getElementById('correct-rate').textContent = UserProfile.getAccuracyRate(profile) + '%';
        document.getElementById('study-time').textContent = Math.round(profile.totalStudyTime / 3600);
        document.getElementById('completed-topics').textContent = UserProfile.getCompletedTopicsCount(profile);

        // Konu bazında performans
        this.renderSubjectPerformance(profile);

        // Haftalık ilerleme
        this.renderWeeklyProgress(profile);

        // Zayıf konular
        this.renderWeakTopics(profile);
    },

    /**
     * Konu bazında performans grafiği
     */
    renderSubjectPerformance(profile) {
        const container = document.getElementById('subject-performance-chart');
        container.innerHTML = '';

        const subjects = Subjects.list;
        const chartData = subjects.map(subject => {
            const stats = UserProfile.getSubjectStats(profile, subject.id);
            const accuracy = stats.totalQuestions > 0 ?
                Utils.calculatePercentage(stats.correctQuestions, stats.totalQuestions) : 0;

            return {
                name: subject.name,
                icon: subject.icon,
                accuracy,
                count: stats.totalQuestions,
                color: subject.color
            };
        }).filter(item => item.count > 0);

        if (chartData.length === 0) {
            container.innerHTML = '<p style="text-align: center; padding: 40px; color: #94A3B8;">Henüz hiç soru çözmedin. Hadi başlayalım! 🚀</p>';
            return;
        }

        chartData.forEach(item => {
            const barContainer = document.createElement('div');
            barContainer.style.cssText = 'margin-bottom: 20px;';

            barContainer.innerHTML = `
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <span style="font-weight: 600;">${item.icon} ${item.name}</span>
                    <span style="color: ${item.color}; font-weight: 700;">${item.accuracy}%</span>
                </div>
                <div style="width: 100%; height: 30px; background: #E2E8F0; border-radius: 8px; overflow: hidden;">
                    <div style="width: ${item.accuracy}%; height: 100%; background: ${item.color};
                         transition: width 1s ease; display: flex; align-items: center; padding-left: 10px;
                         color: white; font-size: 12px; font-weight: 600;">
                        ${item.count} soru
                    </div>
                </div>
            `;

            container.appendChild(barContainer);
        });
    },

    /**
     * Haftalık ilerleme grafiği
     */
    renderWeeklyProgress(profile) {
        const container = document.getElementById('weekly-progress-chart');
        container.innerHTML = '';

        const weeklyData = UserProfile.getWeeklyActivity(profile);
        const maxQuestions = Math.max(...weeklyData.map(d => d.questions), 1);

        const chartContainer = document.createElement('div');
        chartContainer.style.cssText = 'display: flex; align-items: flex-end; justify-content: space-around; height: 200px; padding: 20px;';

        weeklyData.forEach(day => {
            const barHeight = (day.questions / maxQuestions) * 150;
            const accuracy = day.questions > 0 ?
                Utils.calculatePercentage(day.correct, day.questions) : 0;

            const barContainer = document.createElement('div');
            barContainer.style.cssText = 'display: flex; flex-direction: column; align-items: center; gap: 8px;';

            const bar = document.createElement('div');
            bar.style.cssText = `
                width: 40px;
                height: ${barHeight}px;
                background: linear-gradient(to top, #6366F1, #EC4899);
                border-radius: 8px 8px 0 0;
                transition: height 0.5s ease;
                position: relative;
                cursor: pointer;
            `;
            bar.title = `${day.questions} soru, ${accuracy}% doğru`;

            const dayLabel = document.createElement('div');
            dayLabel.style.cssText = 'font-size: 12px; font-weight: 600; color: #64748B;';
            dayLabel.textContent = day.dayName;

            const countLabel = document.createElement('div');
            countLabel.style.cssText = 'font-size: 10px; color: #94A3B8;';
            countLabel.textContent = day.questions || '-';

            barContainer.appendChild(bar);
            barContainer.appendChild(dayLabel);
            barContainer.appendChild(countLabel);

            chartContainer.appendChild(barContainer);
        });

        container.appendChild(chartContainer);

        // Özet bilgi
        const totalWeekly = weeklyData.reduce((sum, day) => sum + day.questions, 0);
        const summary = document.createElement('div');
        summary.style.cssText = 'text-align: center; margin-top: 20px; padding: 15px; background: #F0F9FF; border-radius: 8px;';
        summary.innerHTML = `
            <div style="font-size: 16px; color: #1E293B;">
                Bu hafta <strong style="color: #6366F1;">${totalWeekly} soru</strong> çözdün! 🎉
            </div>
        `;
        container.appendChild(summary);
    },

    /**
     * Zayıf konuları göster
     */
    renderWeakTopics(profile) {
        const container = document.getElementById('weak-topics-list');
        container.innerHTML = '';

        const weakTopics = Subjects.getWeakTopics(profile, 60);

        if (weakTopics.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 48px; margin-bottom: 16px;">🌟</div>
                    <div style="font-size: 18px; color: #10B981; font-weight: 600;">
                        Harika! Zayıf konun yok!
                    </div>
                    <div style="color: #64748B; margin-top: 8px;">
                        Tüm konularda başarılısın, böyle devam et!
                    </div>
                </div>
            `;
            return;
        }

        weakTopics.slice(0, 5).forEach(topic => {
            const item = document.createElement('div');
            item.className = 'weak-topic-item';
            item.style.cssText = `
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px;
                background: #FEF3C7;
                border-left: 4px solid #F59E0B;
                border-radius: 8px;
                margin-bottom: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
            `;

            item.innerHTML = `
                <div>
                    <div style="font-weight: 600; color: #1E293B; margin-bottom: 4px;">
                        ${topic.subjectName} - ${topic.topicName}
                    </div>
                    <div style="font-size: 12px; color: #64748B;">
                        ${topic.questionsAnswered} soru çözüldü
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 24px; font-weight: 700; color: #F59E0B;">
                        ${topic.successRate}%
                    </div>
                    <div style="font-size: 11px; color: #94A3B8;">
                        Başarı oranı
                    </div>
                </div>
            `;

            item.addEventListener('mouseover', () => {
                item.style.transform = 'translateX(4px)';
                item.style.boxShadow = '0 4px 12px rgba(245, 158, 11, 0.3)';
            });

            item.addEventListener('mouseout', () => {
                item.style.transform = 'translateX(0)';
                item.style.boxShadow = 'none';
            });

            container.appendChild(item);
        });

        // Öneri mesajı
        const suggestion = document.createElement('div');
        suggestion.style.cssText = 'margin-top: 20px; padding: 16px; background: #EFF6FF; border-radius: 8px; border-left: 4px solid #3B82F6;';
        suggestion.innerHTML = `
            <div style="font-weight: 600; color: #1E40AF; margin-bottom: 8px;">💡 Öneri</div>
            <div style="color: #64748B; font-size: 14px;">
                Bu konularda daha fazla pratik yaparak başarı oranını artırabilirsin!
            </div>
        `;
        container.appendChild(suggestion);
    },

    /**
     * Ebeveyn raporunu oluştur
     */
    generateParentReport(profile) {
        const summary = UserProfile.getSummary(profile);

        // Genel durum
        this.renderParentOverview(summary);

        // Haftalık aktivite
        this.renderParentActivity(profile);

        // Güçlü ve zayıf yönler
        this.renderParentStrengths(profile);

        // Öneriler
        this.renderParentRecommendations(profile, summary);
    },

    /**
     * Ebeveyn raporu - Genel durum
     */
    renderParentOverview(summary) {
        const container = document.getElementById('parent-overview');
        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; border-radius: 12px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Seviye</div>
                    <div style="font-size: 36px; font-weight: 700;">${summary.level}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #EC4899, #F59E0B); color: white; border-radius: 12px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Toplam Puan</div>
                    <div style="font-size: 36px; font-weight: 700;">${Utils.formatNumber(summary.points)}</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #10B981, #3B82F6); color: white; border-radius: 12px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Doğruluk</div>
                    <div style="font-size: 36px; font-weight: 700;">${summary.accuracy}%</div>
                </div>
                <div style="padding: 20px; background: linear-gradient(135deg, #F59E0B, #EF4444); color: white; border-radius: 12px;">
                    <div style="font-size: 14px; opacity: 0.9; margin-bottom: 8px;">Süreklilik</div>
                    <div style="font-size: 36px; font-weight: 700;">${summary.streak} gün</div>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h4 style="margin-bottom: 16px; color: #1E293B;">📊 Detaylı İstatistikler</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px;">
                    <div>
                        <div style="color: #64748B; font-size: 14px;">Toplam Soru</div>
                        <div style="font-size: 24px; font-weight: 600; color: #1E293B;">${summary.totalQuestions}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 14px;">Doğru Cevap</div>
                        <div style="font-size: 24px; font-weight: 600; color: #10B981;">${summary.correctQuestions}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 14px;">Çalışma Süresi</div>
                        <div style="font-size: 24px; font-weight: 600; color: #6366F1;">${summary.studyTimeFormatted}</div>
                    </div>
                    <div>
                        <div style="color: #64748B; font-size: 14px;">Kazanılan Rozet</div>
                        <div style="font-size: 24px; font-weight: 600; color: #EC4899;">${summary.badgeCount}</div>
                    </div>
                </div>
            </div>
        `;
    },

    /**
     * Ebeveyn raporu - Haftalık aktivite
     */
    renderParentActivity(profile) {
        const container = document.getElementById('parent-activity');
        const weeklyData = UserProfile.getWeeklyActivity(profile);
        const weeklyProgress = UserProfile.getWeeklyProgress(profile);

        container.innerHTML = `
            <div style="padding: 20px; background: white; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-weight: 600;">Haftalık Hedef</span>
                        <span style="font-size: 18px; font-weight: 700; color: #6366F1;">
                            ${weeklyProgress.current} / ${weeklyProgress.goal}
                        </span>
                    </div>
                    <div style="width: 100%; height: 20px; background: #E2E8F0; border-radius: 10px; overflow: hidden;">
                        <div style="width: ${weeklyProgress.percentage}%; height: 100%;
                             background: linear-gradient(90deg, #6366F1, #EC4899);
                             transition: width 1s ease;"></div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 20px;">
                    ${weeklyData.map(day => `
                        <div style="text-align: center; padding: 12px; background: ${day.questions > 0 ? '#F0F9FF' : '#F8FAFC'};
                             border-radius: 8px; border: 2px solid ${day.questions > 0 ? '#6366F1' : '#E2E8F0'};">
                            <div style="font-size: 12px; font-weight: 600; color: #64748B; margin-bottom: 4px;">
                                ${day.dayName}
                            </div>
                            <div style="font-size: 20px; font-weight: 700; color: ${day.questions > 0 ? '#6366F1' : '#CBD5E1'};">
                                ${day.questions || '-'}
                            </div>
                            <div style="font-size: 10px; color: #94A3B8;">
                                ${day.questions > 0 ? Utils.calculatePercentage(day.correct, day.questions) + '%' : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },

    /**
     * Ebeveyn raporu - Güçlü ve zayıf yönler
     */
    renderParentStrengths(profile) {
        const container = document.getElementById('parent-strengths');
        const strongTopics = Subjects.getStrongTopics(profile, 80).slice(0, 5);
        const weakTopics = Subjects.getWeakTopics(profile, 60).slice(0, 5);

        container.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="padding: 20px; background: linear-gradient(135deg, #D1FAE5, #A7F3D0); border-radius: 12px;">
                    <h4 style="color: #065F46; margin-bottom: 16px;">✅ Güçlü Konular</h4>
                    ${strongTopics.length > 0 ? `
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            ${strongTopics.map(topic => `
                                <div style="display: flex; justify-content: space-between; padding: 12px;
                                     background: white; border-radius: 8px;">
                                    <span style="font-weight: 600; color: #1E293B;">
                                        ${topic.subjectName} - ${topic.topicName}
                                    </span>
                                    <span style="font-weight: 700; color: #10B981;">
                                        ${topic.successRate}%
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p style="color: #065F46;">Henüz güçlü konu bulunmuyor. Daha fazla pratik gerekli.</p>'}
                </div>

                <div style="padding: 20px; background: linear-gradient(135deg, #FEE2E2, #FECACA); border-radius: 12px;">
                    <h4 style="color: #991B1B; margin-bottom: 16px;">⚠️ Geliştirilmesi Gereken Konular</h4>
                    ${weakTopics.length > 0 ? `
                        <div style="display: flex; flex-direction: column; gap: 12px;">
                            ${weakTopics.map(topic => `
                                <div style="display: flex; justify-content: space-between; padding: 12px;
                                     background: white; border-radius: 8px;">
                                    <span style="font-weight: 600; color: #1E293B;">
                                        ${topic.subjectName} - ${topic.topicName}
                                    </span>
                                    <span style="font-weight: 700; color: #EF4444;">
                                        ${topic.successRate}%
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    ` : '<p style="color: #991B1B;">Tebrikler! Tüm konularda iyi performans gösteriliyor.</p>'}
                </div>
            </div>
        `;
    },

    /**
     * Ebeveyn raporu - Öneriler
     */
    renderParentRecommendations(profile, summary) {
        const container = document.getElementById('parent-recommendations');
        const recommendations = [];

        // Çalışma süresi önerisi
        if (summary.studyTime < 3600) { // 1 saatten az
            recommendations.push({
                icon: '⏰',
                title: 'Çalışma Süresini Artırın',
                text: 'Günde en az 15-20 dakika düzenli çalışma, öğrenmeyi pekiştirecektir.'
            });
        }

        // Süreklilik önerisi
        if (summary.streak < 7) {
            recommendations.push({
                icon: '🔥',
                title: 'Düzenli Çalışma Alışkanlığı',
                text: 'Her gün düzenli çalışma, uzun vadeli başarı için çok önemlidir.'
            });
        }

        // Doğruluk oranı önerisi
        if (summary.accuracy < 70) {
            recommendations.push({
                icon: '🎯',
                title: 'Kavrama Eksiklikleri',
                text: 'Yanlış yapılan soruların çözümlerini incelemek, kavramların daha iyi anlaşılmasını sağlar.'
            });
        }

        // Çeşitlilik önerisi
        const subjectCount = Object.keys(profile.subjectStats).length;
        if (subjectCount < 3) {
            recommendations.push({
                icon: '🌈',
                title: 'Konu Çeşitliliği',
                text: 'Farklı matematik konularında çalışmak, genel matematik becerisini geliştirir.'
            });
        }

        // Pozitif geri bildirim
        if (summary.accuracy >= 80) {
            recommendations.push({
                icon: '🌟',
                title: 'Mükemmel Performans!',
                text: 'Çocuğunuz harika bir performans sergiliyor. Motivasyonunu korumak için ödüllendirin!'
            });
        }

        if (summary.streak >= 7) {
            recommendations.push({
                icon: '🏆',
                title: 'Harika Disiplin!',
                text: 'Düzenli çalışma alışkanlığı kazanmış. Bu başarıyı kutlayın!'
            });
        }

        container.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 16px;">
                ${recommendations.map(rec => `
                    <div style="padding: 20px; background: white; border-radius: 12px;
                         box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 4px solid #6366F1;">
                        <div style="display: flex; gap: 16px; align-items: start;">
                            <div style="font-size: 32px;">${rec.icon}</div>
                            <div>
                                <h4 style="color: #1E293B; margin-bottom: 8px;">${rec.title}</h4>
                                <p style="color: #64748B; line-height: 1.6;">${rec.text}</p>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    },

    /**
     * Raporu PDF olarak indir (basit HTML formatında)
     */
    exportReport(profile) {
        const summary = UserProfile.getSummary(profile);
        const reportDate = Utils.formatDate(new Date());

        const reportHTML = `
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Matematik Öğrenme Raporu - ${summary.username}</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 40px; }
        h1 { color: #6366F1; }
        h2 { color: #1E293B; margin-top: 30px; }
        .stat { display: inline-block; margin: 10px 20px 10px 0; }
        .stat-label { color: #64748B; font-size: 14px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #6366F1; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #E2E8F0; }
        th { background: #F8FAFC; font-weight: 600; }
    </style>
</head>
<body>
    <h1>📊 Matematik Öğrenme Raporu</h1>
    <p><strong>Öğrenci:</strong> ${summary.username}</p>
    <p><strong>Rapor Tarihi:</strong> ${reportDate}</p>

    <h2>Genel Durum</h2>
    <div class="stat">
        <div class="stat-label">Seviye</div>
        <div class="stat-value">${summary.level}</div>
    </div>
    <div class="stat">
        <div class="stat-label">Toplam Puan</div>
        <div class="stat-value">${summary.points}</div>
    </div>
    <div class="stat">
        <div class="stat-label">Doğruluk Oranı</div>
        <div class="stat-value">${summary.accuracy}%</div>
    </div>
    <div class="stat">
        <div class="stat-label">Süreklilik</div>
        <div class="stat-value">${summary.streak} gün</div>
    </div>

    <h2>Detaylı İstatistikler</h2>
    <table>
        <tr>
            <th>Metrik</th>
            <th>Değer</th>
        </tr>
        <tr>
            <td>Toplam Soru Sayısı</td>
            <td>${summary.totalQuestions}</td>
        </tr>
        <tr>
            <td>Doğru Cevap Sayısı</td>
            <td>${summary.correctQuestions}</td>
        </tr>
        <tr>
            <td>Toplam Çalışma Süresi</td>
            <td>${summary.studyTimeFormatted}</td>
        </tr>
        <tr>
            <td>Kazanılan Rozet</td>
            <td>${summary.badgeCount}</td>
        </tr>
        <tr>
            <td>Tamamlanan Konu</td>
            <td>${summary.completedTopics}</td>
        </tr>
    </table>

    <p style="margin-top: 40px; color: #64748B; font-size: 12px;">
        Bu rapor Matematik Öğrenme Uygulaması tarafından otomatik oluşturulmuştur.
    </p>
</body>
</html>
        `;

        // Yeni pencerede aç
        const newWindow = window.open('', '_blank');
        newWindow.document.write(reportHTML);
        newWindow.document.close();
        newWindow.print();
    }
};

// Global erişim için
window.Stats = Stats;

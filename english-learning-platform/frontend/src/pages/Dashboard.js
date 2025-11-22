import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserProgress, getUserStats, getRandomWords } from '../services/api';

function Dashboard() {
  const [progress, setProgress] = useState(null);
  const [stats, setStats] = useState(null);
  const [dailyWords, setDailyWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const userId = 1; // Demo user

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [progressRes, statsRes, wordsRes] = await Promise.all([
        getUserProgress(userId),
        getUserStats(userId),
        getRandomWords({ count: 5, level: 'Beginner' })
      ]);

      setProgress(progressRes.data.data);
      setStats(statsRes.data.data);
      setDailyWords(wordsRes.data.data);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Yükleniyor...</div>;
  }

  const todayProgress = progress?.today || {};
  const dailyGoal = progress?.daily_goal || 10;
  const wordsLearned = todayProgress.words_learned || 0;
  const progressPercentage = Math.min((wordsLearned / dailyGoal) * 100, 100);

  return (
    <div className="container">
      <h1>İngilizce Öğrenme Platformu</h1>

      <div className="card">
        <h2>Bugünkü Hedef</h2>
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progressPercentage}%` }}
          >
            {wordsLearned}/{dailyGoal}
          </div>
        </div>
        <p>{wordsLearned} / {dailyGoal} kelime öğrenildi</p>
      </div>

      <div className="grid grid-3">
        <div className="card stat-card">
          <div className="stat-label">Toplam Kelime</div>
          <div className="stat-number">{stats?.total_words_learned || 0}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">Toplam Alıştırma</div>
          <div className="stat-number">{stats?.total_exercises || 0}</div>
        </div>
        <div className="card stat-card">
          <div className="stat-label">Doğruluk Oranı</div>
          <div className="stat-number">{stats?.accuracy_percentage || 0}%</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h3>Bugünün Kelimeleri</h3>
          {dailyWords.length > 0 ? (
            <div>
              {dailyWords.map((word, index) => (
                <div key={index} style={{
                  padding: '12px',
                  background: '#f7fafc',
                  marginBottom: '8px',
                  borderRadius: '8px'
                }}>
                  <strong>{word.word}</strong> - {word.meaning_tr}
                  {word.example_sentence && (
                    <div style={{ fontSize: '14px', color: '#718096', marginTop: '4px' }}>
                      Örnek: {word.example_sentence}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p>Kelime yükleniyor...</p>
          )}
        </div>

        <div className="card">
          <h3>Alıştırmalar</h3>
          <Link to="/fill-blank" className="btn btn-primary" style={{ width: '100%', marginBottom: '12px' }}>
            Boşluk Doldurma
          </Link>
          <Link to="/match-meaning" className="btn btn-primary" style={{ width: '100%', marginBottom: '12px' }}>
            Kelime Eşleştirme
          </Link>
          <Link to="/words" className="btn btn-secondary" style={{ width: '100%' }}>
            Tüm Kelimeler
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

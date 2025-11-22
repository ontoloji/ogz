import React, { useState, useEffect } from 'react';
import { getUserProgress, getUserStats, updateDailyGoal } from '../services/api';

function Progress() {
  const [progress, setProgress] = useState(null);
  const [stats, setStats] = useState(null);
  const [newGoal, setNewGoal] = useState('');
  const [loading, setLoading] = useState(true);
  const [showGoalInput, setShowGoalInput] = useState(false);
  const userId = 1;

  useEffect(() => {
    loadProgressData();
  }, []);

  const loadProgressData = async () => {
    try {
      setLoading(true);
      const [progressRes, statsRes] = await Promise.all([
        getUserProgress(userId, { days: 7 }),
        getUserStats(userId)
      ]);

      setProgress(progressRes.data.data);
      setStats(statsRes.data.data);
      setNewGoal(progressRes.data.data.daily_goal);
    } catch (error) {
      console.error('Error loading progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateGoal = async () => {
    try {
      await updateDailyGoal(userId, parseInt(newGoal));
      setShowGoalInput(false);
      loadProgressData();
    } catch (error) {
      console.error('Error updating goal:', error);
    }
  };

  if (loading) {
    return <div className="loading">Yükleniyor...</div>;
  }

  const todayProgress = progress?.today || {};
  const dailyGoal = progress?.daily_goal || 10;

  return (
    <div className="container">
      <h1>İlerleme Takibi</h1>

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

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2>Günlük Hedef</h2>
          <button
            className="btn btn-secondary"
            onClick={() => setShowGoalInput(!showGoalInput)}
          >
            Hedef Değiştir
          </button>
        </div>

        {showGoalInput && (
          <div style={{ marginBottom: '20px', padding: '16px', background: '#f7fafc', borderRadius: '8px' }}>
            <label style={{ display: 'block', marginBottom: '8px' }}>
              Yeni günlük hedef:
              <input
                type="number"
                value={newGoal}
                onChange={(e) => setNewGoal(e.target.value)}
                min="1"
                max="100"
                style={{
                  marginLeft: '12px',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #cbd5e0',
                  width: '80px'
                }}
              />
            </label>
            <button className="btn btn-primary" onClick={handleUpdateGoal}>
              Kaydet
            </button>
          </div>
        )}

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${Math.min((todayProgress.words_learned / dailyGoal) * 100, 100)}%`
            }}
          >
            {todayProgress.words_learned || 0}/{dailyGoal}
          </div>
        </div>
        <p style={{ marginTop: '8px' }}>
          Bugün {todayProgress.words_learned || 0} kelime öğrendiniz
        </p>
      </div>

      <div className="card">
        <h2>Son 7 Günlük İlerleme</h2>
        {progress?.history && progress.history.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                  <th style={{ padding: '12px', textAlign: 'left' }}>Tarih</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>Kelimeler</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>Alıştırmalar</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>Doğru/Toplam</th>
                  <th style={{ padding: '12px', textAlign: 'center' }}>Oran</th>
                </tr>
              </thead>
              <tbody>
                {progress.history.map((day, index) => {
                  const accuracy = day.total_answers > 0
                    ? Math.round((day.correct_answers / day.total_answers) * 100)
                    : 0;

                  return (
                    <tr key={index} style={{ borderBottom: '1px solid #e2e8f0' }}>
                      <td style={{ padding: '12px' }}>
                        {new Date(day.date).toLocaleDateString('tr-TR')}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {day.words_learned}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {day.exercises_completed}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        {day.correct_answers}/{day.total_answers}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '4px',
                          background: accuracy >= 70 ? '#c6f6d5' : accuracy >= 50 ? '#fef3c7' : '#fed7d7',
                          color: accuracy >= 70 ? '#22543d' : accuracy >= 50 ? '#78350f' : '#742a2a'
                        }}>
                          {accuracy}%
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <p>Henüz ilerleme kaydı yok. Alıştırma yapmaya başlayın!</p>
        )}
      </div>
    </div>
  );
}

export default Progress;

import React, { useState } from 'react';
import './Goals.css';
import { v4 as uuidv4 } from 'uuid';
import { formatDate } from '../../utils/dateUtils';

const Goals = ({ goals, setGoals }) => {
  const [newGoal, setNewGoal] = useState('');
  const [targetValue, setTargetValue] = useState('');
  const [currentValue, setCurrentValue] = useState('');
  const [deadline, setDeadline] = useState('');
  const [editingId, setEditingId] = useState(null);

  const addGoal = () => {
    if (newGoal.trim() && targetValue) {
      const goal = {
        id: uuidv4(),
        title: newGoal,
        targetValue: parseFloat(targetValue),
        currentValue: parseFloat(currentValue) || 0,
        deadline: deadline || null,
        createdAt: new Date().toISOString(),
        completed: false
      };
      setGoals([...goals, goal]);
      resetForm();
    }
  };

  const resetForm = () => {
    setNewGoal('');
    setTargetValue('');
    setCurrentValue('');
    setDeadline('');
  };

  const updateGoalProgress = (id, value) => {
    setGoals(
      goals.map((goal) => {
        if (goal.id === id) {
          const newValue = parseFloat(value) || 0;
          return {
            ...goal,
            currentValue: newValue,
            completed: newValue >= goal.targetValue
          };
        }
        return goal;
      })
    );
  };

  const deleteGoal = (id) => {
    if (window.confirm('Bu hedefi silmek istediğinizden emin misiniz?')) {
      setGoals(goals.filter((g) => g.id !== id));
    }
  };

  const toggleComplete = (id) => {
    setGoals(
      goals.map((goal) =>
        goal.id === id ? { ...goal, completed: !goal.completed } : goal
      )
    );
  };

  const getProgress = (goal) => {
    return Math.min(Math.round((goal.currentValue / goal.targetValue) * 100), 100);
  };

  const getDaysLeft = (deadline) => {
    if (!deadline) return null;
    const days = Math.ceil((new Date(deadline) - new Date()) / (1000 * 60 * 60 * 24));
    return days;
  };

  return (
    <div className="goals-container">
      <div className="goals-header">
        <h2>🎯 Hedefler</h2>
        <div className="goals-stats">
          <span>
            <strong>{goals.filter((g) => g.completed).length}</strong> / {goals.length} Tamamlandı
          </span>
        </div>
      </div>

      <div className="goal-input-section">
        <input
          type="text"
          value={newGoal}
          onChange={(e) => setNewGoal(e.target.value)}
          placeholder="Hedef başlığı..."
          className="goal-input"
        />
        <div className="goal-inputs-row">
          <input
            type="number"
            value={currentValue}
            onChange={(e) => setCurrentValue(e.target.value)}
            placeholder="Mevcut değer"
            className="goal-input-small"
          />
          <span className="input-separator">/</span>
          <input
            type="number"
            value={targetValue}
            onChange={(e) => setTargetValue(e.target.value)}
            placeholder="Hedef değer"
            className="goal-input-small"
          />
          <input
            type="date"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
            className="goal-input-small"
          />
        </div>
        <button onClick={addGoal} className="btn btn-primary">
          + Hedef Ekle
        </button>
      </div>

      <div className="goals-list">
        {goals.length === 0 ? (
          <div className="empty-state">
            <p>🎯 Henüz hedef yok</p>
            <p className="empty-subtitle">Başarmak istediğiniz hedeflerinizi ekleyin</p>
          </div>
        ) : (
          goals.map((goal) => {
            const progress = getProgress(goal);
            const daysLeft = getDaysLeft(goal.deadline);

            return (
              <div
                key={goal.id}
                className={`goal-item ${goal.completed ? 'completed' : ''}`}
              >
                <div className="goal-header-row">
                  <div className="goal-title-section">
                    <input
                      type="checkbox"
                      checked={goal.completed}
                      onChange={() => toggleComplete(goal.id)}
                      className="goal-checkbox"
                    />
                    <h3 className="goal-title">{goal.title}</h3>
                  </div>
                  <button
                    onClick={() => deleteGoal(goal.id)}
                    className="btn-delete"
                    title="Sil"
                  >
                    🗑️
                  </button>
                </div>

                <div className="goal-progress-section">
                  <div className="goal-values">
                    <input
                      type="number"
                      value={goal.currentValue}
                      onChange={(e) => updateGoalProgress(goal.id, e.target.value)}
                      className="progress-input"
                    />
                    <span className="value-separator">/</span>
                    <span className="target-value">{goal.targetValue}</span>
                  </div>

                  <div className="progress-bar-container">
                    <div className="progress-bar-bg">
                      <div
                        className="progress-bar-fill"
                        style={{
                          width: `${progress}%`,
                          backgroundColor: goal.completed ? '#48bb78' : '#667eea'
                        }}
                      />
                    </div>
                    <span className="progress-percentage">{progress}%</span>
                  </div>

                  {goal.deadline && (
                    <div className="goal-deadline">
                      <span className="deadline-label">Bitiş:</span>
                      <span className="deadline-date">{formatDate(goal.deadline)}</span>
                      {daysLeft !== null && daysLeft >= 0 && (
                        <span className={`days-left ${daysLeft <= 7 ? 'urgent' : ''}`}>
                          ({daysLeft} gün kaldı)
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Goals;

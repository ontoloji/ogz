import React, { useState } from 'react';
import './Reports.css';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { getTodayRange, getWeekRange, getMonthRange, isInRange, formatDuration, formatDate } from '../../utils/dateUtils';

const Reports = ({ todos, timeEntries, projects }) => {
  const [period, setPeriod] = useState('week'); // today, week, month

  const getRange = () => {
    switch (period) {
      case 'today':
        return getTodayRange();
      case 'week':
        return getWeekRange();
      case 'month':
        return getMonthRange();
      default:
        return getWeekRange();
    }
  };

  const range = getRange();

  // Filter data by period
  const filteredTimeEntries = timeEntries.filter((entry) =>
    isInRange(entry.startTime, range)
  );

  const filteredTodos = todos.filter((todo) =>
    todo.completedAt && isInRange(todo.completedAt, range)
  );

  // Calculate stats
  const totalTimeSpent = filteredTimeEntries.reduce((sum, entry) => sum + entry.duration, 0);
  const completedTodosCount = filteredTodos.length;
  const totalTodosCount = todos.length;
  const completionRate = totalTodosCount > 0
    ? Math.round((completedTodosCount / totalTodosCount) * 100)
    : 0;

  // Time by project
  const timeByProject = projects.map((project) => {
    const projectTime = filteredTimeEntries
      .filter((entry) => entry.projectId === project.id)
      .reduce((sum, entry) => sum + entry.duration, 0);
    return {
      name: project.name,
      time: projectTime,
      hours: (projectTime / 60).toFixed(1)
    };
  }).filter((item) => item.time > 0);

  // Todos by project
  const todosByProject = projects.map((project) => {
    const projectTodos = todos.filter((todo) => todo.projectId === project.id);
    const completed = projectTodos.filter((t) => t.completed).length;
    return {
      name: project.name,
      completed,
      active: projectTodos.length - completed,
      total: projectTodos.length
    };
  }).filter((item) => item.total > 0);

  // Daily activity (last 7 days for week, last 30 days for month)
  const getDailyActivity = () => {
    const days = period === 'month' ? 30 : 7;
    const dailyData = [];
    const today = new Date();

    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      date.setHours(0, 0, 0, 0);
      const nextDate = new Date(date);
      nextDate.setDate(nextDate.getDate() + 1);

      const dayTimeEntries = timeEntries.filter((entry) =>
        isInRange(entry.startTime, { start: date, end: nextDate })
      );

      const dayTodos = todos.filter((todo) =>
        todo.completedAt && isInRange(todo.completedAt, { start: date, end: nextDate })
      );

      dailyData.push({
        date: formatDate(date, 'dd MMM'),
        time: dayTimeEntries.reduce((sum, entry) => sum + entry.duration, 0) / 60,
        todos: dayTodos.length
      });
    }

    return dailyData;
  };

  const dailyActivity = getDailyActivity();

  const COLORS = ['#667eea', '#764ba2', '#48bb78', '#f56565', '#ed8936', '#4299e1'];

  return (
    <div className="reports-container">
      <div className="reports-header">
        <h2>📊 Raporlar</h2>
        <div className="period-selector">
          <button
            className={`period-btn ${period === 'today' ? 'active' : ''}`}
            onClick={() => setPeriod('today')}
          >
            Bugün
          </button>
          <button
            className={`period-btn ${period === 'week' ? 'active' : ''}`}
            onClick={() => setPeriod('week')}
          >
            Bu Hafta
          </button>
          <button
            className={`period-btn ${period === 'month' ? 'active' : ''}`}
            onClick={() => setPeriod('month')}
          >
            Bu Ay
          </button>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-label">Toplam Süre</div>
            <div className="stat-value">{formatDuration(totalTimeSpent)}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">✓</div>
          <div className="stat-content">
            <div className="stat-label">Tamamlanan Görevler</div>
            <div className="stat-value">{completedTodosCount}</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-label">Tamamlanma Oranı</div>
            <div className="stat-value">{completionRate}%</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📁</div>
          <div className="stat-content">
            <div className="stat-label">Aktif Projeler</div>
            <div className="stat-value">{projects.length}</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {dailyActivity.length > 0 && (
          <div className="chart-card">
            <h3>Günlük Aktivite</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyActivity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="time" fill="#667eea" name="Saat" />
                <Bar yAxisId="right" dataKey="todos" fill="#48bb78" name="Görevler" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {timeByProject.length > 0 && (
          <div className="chart-card">
            <h3>Projelere Göre Zaman</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={timeByProject}
                  dataKey="time"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.name}: ${entry.hours}sa`}
                >
                  {timeByProject.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatDuration(value)} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {todosByProject.length > 0 && (
          <div className="chart-card">
            <h3>Projelere Göre Görevler</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={todosByProject}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="completed" fill="#48bb78" name="Tamamlanan" stackId="a" />
                <Bar dataKey="active" fill="#ed8936" name="Aktif" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;

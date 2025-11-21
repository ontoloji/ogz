import React, { useState, useEffect } from 'react';
import './App.css';
import PomodoroTimer from './components/PomodoroTimer/PomodoroTimer';
import TodoList from './components/TodoList/TodoList';
import Projects from './components/Projects/Projects';
import TimeTracker from './components/TimeTracker/TimeTracker';
import Reports from './components/Reports/Reports';
import Goals from './components/Goals/Goals';
import Notes from './components/Notes/Notes';
import Calendar from './components/Calendar/Calendar';
import WebsiteBlocker from './components/WebsiteBlocker/WebsiteBlocker';
import Motivation from './components/Motivation/Motivation';
import storage from './utils/storage';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [settings, setSettings] = useState({
    pomodoroWork: 25,
    pomodoroShortBreak: 5,
    pomodoroLongBreak: 15,
    pomodoroSessions: 4
  });

  // State management
  const [todos, setTodos] = useState([]);
  const [projects, setProjects] = useState([]);
  const [timeEntries, setTimeEntries] = useState([]);
  const [goals, setGoals] = useState([]);
  const [notes, setNotes] = useState([]);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [blockedWebsites, setBlockedWebsites] = useState([]);

  // Load data from storage
  useEffect(() => {
    const loadData = async () => {
      try {
        const [
          savedTodos,
          savedProjects,
          savedTimeEntries,
          savedGoals,
          savedNotes,
          savedCalendarEvents,
          savedBlockedWebsites,
          savedSettings
        ] = await Promise.all([
          storage.getTodos(),
          storage.getProjects(),
          storage.getTimeEntries(),
          storage.getGoals(),
          storage.getNotes(),
          storage.getCalendarEvents(),
          storage.getBlockedWebsites(),
          storage.getSettings()
        ]);

        setTodos(savedTodos);
        setProjects(savedProjects);
        setTimeEntries(savedTimeEntries);
        setGoals(savedGoals);
        setNotes(savedNotes);
        setCalendarEvents(savedCalendarEvents);
        setBlockedWebsites(savedBlockedWebsites);
        setSettings(savedSettings);
      } catch (error) {
        console.error('Error loading data:', error);
      }
    };

    loadData();
  }, []);

  // Save data to storage
  useEffect(() => {
    storage.saveTodos(todos);
  }, [todos]);

  useEffect(() => {
    storage.saveProjects(projects);
  }, [projects]);

  useEffect(() => {
    storage.saveTimeEntries(timeEntries);
  }, [timeEntries]);

  useEffect(() => {
    storage.saveGoals(goals);
  }, [goals]);

  useEffect(() => {
    storage.saveNotes(notes);
  }, [notes]);

  useEffect(() => {
    storage.saveCalendarEvents(calendarEvents);
  }, [calendarEvents]);

  useEffect(() => {
    storage.saveBlockedWebsites(blockedWebsites);
  }, [blockedWebsites]);

  useEffect(() => {
    storage.saveSettings(settings);
  }, [settings]);

  // Backup and restore
  const handleExport = async () => {
    try {
      const data = await storage.exportData();
      const dataStr = JSON.stringify(data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `verimlilik-yedek-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export error:', error);
      alert('Yedekleme sırasında bir hata oluştu!');
    }
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target.result);
        await storage.importData(data);

        // Reload data
        setTodos(data.todos || []);
        setProjects(data.projects || []);
        setTimeEntries(data.timeEntries || []);
        setGoals(data.goals || []);
        setNotes(data.notes || []);
        setCalendarEvents(data.calendarEvents || []);
        setBlockedWebsites(data.blockedWebsites || []);
        if (data.settings) setSettings(data.settings);

        alert('Veriler başarıyla geri yüklendi!');
      } catch (error) {
        console.error('Import error:', error);
        alert('Veri yükleme sırasında bir hata oluştu!');
      }
    };
    reader.readAsText(file);
  };

  const navigationItems = [
    { id: 'dashboard', label: 'Anasayfa', icon: '🏠' },
    { id: 'pomodoro', label: 'Pomodoro', icon: '🍅' },
    { id: 'todos', label: 'Görevler', icon: '✓' },
    { id: 'projects', label: 'Projeler', icon: '📁' },
    { id: 'timetracker', label: 'Zaman Takibi', icon: '⏱️' },
    { id: 'goals', label: 'Hedefler', icon: '🎯' },
    { id: 'notes', label: 'Notlar', icon: '📝' },
    { id: 'calendar', label: 'Takvim', icon: '📅' },
    { id: 'reports', label: 'Raporlar', icon: '📊' },
    { id: 'blocker', label: 'Website Engelleyici', icon: '🚫' }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="dashboard">
            <div className="dashboard-section">
              <Motivation />
            </div>
            <div className="dashboard-grid">
              <div className="dashboard-item">
                <PomodoroTimer settings={settings} />
              </div>
              <div className="dashboard-item">
                <TodoList todos={todos} setTodos={setTodos} projects={projects} />
              </div>
            </div>
          </div>
        );
      case 'pomodoro':
        return <PomodoroTimer settings={settings} />;
      case 'todos':
        return <TodoList todos={todos} setTodos={setTodos} projects={projects} />;
      case 'projects':
        return <Projects projects={projects} setProjects={setProjects} todos={todos} />;
      case 'timetracker':
        return <TimeTracker timeEntries={timeEntries} setTimeEntries={setTimeEntries} projects={projects} />;
      case 'goals':
        return <Goals goals={goals} setGoals={setGoals} />;
      case 'notes':
        return <Notes notes={notes} setNotes={setNotes} />;
      case 'calendar':
        return <Calendar calendarEvents={calendarEvents} setCalendarEvents={setCalendarEvents} />;
      case 'reports':
        return <Reports todos={todos} timeEntries={timeEntries} projects={projects} />;
      case 'blocker':
        return <WebsiteBlocker blockedWebsites={blockedWebsites} setBlockedWebsites={setBlockedWebsites} />;
      default:
        return <div>Sayfa bulunamadı</div>;
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">💼 Verimlilik Uygulaması</h1>
          <div className="header-actions">
            <button onClick={handleExport} className="btn btn-secondary" title="Verileri Yedekle">
              💾 Yedekle
            </button>
            <label className="btn btn-secondary" title="Verileri Geri Yükle">
              📂 Geri Yükle
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                style={{ display: 'none' }}
              />
            </label>
          </div>
        </div>
      </header>

      <div className="app-container">
        <nav className="app-nav">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </button>
          ))}
        </nav>

        <main className="app-main">
          {renderContent()}
        </main>
      </div>

      <footer className="app-footer">
        <p>© 2024 Verimlilik Uygulaması - Zamanınızı en iyi şekilde yönetin</p>
      </footer>
    </div>
  );
}

export default App;

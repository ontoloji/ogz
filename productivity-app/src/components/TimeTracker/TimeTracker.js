import React, { useState, useEffect, useRef } from 'react';
import './TimeTracker.css';
import { v4 as uuidv4 } from 'uuid';
import { formatDuration, formatDateTime } from '../../utils/dateUtils';

const TimeTracker = ({ timeEntries, setTimeEntries, projects }) => {
  const [isTracking, setIsTracking] = useState(false);
  const [currentEntry, setCurrentEntry] = useState(null);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [description, setDescription] = useState('');
  const [selectedProject, setSelectedProject] = useState('');
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isTracking) {
      intervalRef.current = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 60000); // Update every minute
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isTracking]);

  const startTracking = () => {
    if (!description.trim()) {
      alert('Lütfen bir açıklama girin');
      return;
    }

    const entry = {
      id: uuidv4(),
      description,
      projectId: selectedProject || null,
      startTime: new Date().toISOString(),
      endTime: null,
      duration: 0
    };

    setCurrentEntry(entry);
    setIsTracking(true);
    setElapsedTime(0);
  };

  const stopTracking = () => {
    if (currentEntry) {
      const endTime = new Date().toISOString();
      const duration = Math.round(
        (new Date(endTime) - new Date(currentEntry.startTime)) / 1000 / 60
      );

      const completedEntry = {
        ...currentEntry,
        endTime,
        duration
      };

      setTimeEntries([completedEntry, ...timeEntries]);
      setIsTracking(false);
      setCurrentEntry(null);
      setElapsedTime(0);
      setDescription('');
      setSelectedProject('');
    }
  };

  const deleteEntry = (id) => {
    if (window.confirm('Bu zaman kaydını silmek istediğinizden emin misiniz?')) {
      setTimeEntries(timeEntries.filter((e) => e.id !== id));
    }
  };

  const getProjectName = (projectId) => {
    const project = projects.find((p) => p.id === projectId);
    return project ? project.name : 'Genel';
  };

  const getTotalTime = () => {
    return timeEntries.reduce((total, entry) => total + entry.duration, 0);
  };

  return (
    <div className="time-tracker-container">
      <div className="tracker-header">
        <h2>⏱️ Zaman Takibi</h2>
        <div className="total-time">
          Toplam: <strong>{formatDuration(getTotalTime())}</strong>
        </div>
      </div>

      <div className="tracker-controls">
        <div className="tracker-inputs">
          <input
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Ne üzerinde çalışıyorsunuz?"
            className="tracker-input"
            disabled={isTracking}
          />
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="tracker-select"
            disabled={isTracking}
          >
            <option value="">Proje Seç (Opsiyonel)</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>

        {isTracking ? (
          <div className="tracking-active">
            <div className="elapsed-time">
              <span className="time-display">{formatDuration(elapsedTime)}</span>
              <span className="tracking-indicator">● Takip ediliyor</span>
            </div>
            <button onClick={stopTracking} className="btn btn-danger">
              ⏹ Durdur
            </button>
          </div>
        ) : (
          <button onClick={startTracking} className="btn btn-success btn-large">
            ▶ Başlat
          </button>
        )}
      </div>

      <div className="time-entries">
        <h3>Son Aktiviteler</h3>
        {timeEntries.length === 0 ? (
          <div className="empty-state">
            <p>⏱️ Henüz zaman kaydı yok</p>
            <p className="empty-subtitle">Çalışmaya başlayın ve zamanınızı takip edin</p>
          </div>
        ) : (
          <div className="entries-list">
            {timeEntries.map((entry) => (
              <div key={entry.id} className="entry-item">
                <div className="entry-content">
                  <div className="entry-description">{entry.description}</div>
                  <div className="entry-meta">
                    {entry.projectId && (
                      <span className="badge badge-info">
                        📁 {getProjectName(entry.projectId)}
                      </span>
                    )}
                    <span className="entry-time">
                      {formatDateTime(entry.startTime)}
                    </span>
                  </div>
                </div>
                <div className="entry-duration">
                  <span className="duration-text">{formatDuration(entry.duration)}</span>
                  <button
                    onClick={() => deleteEntry(entry.id)}
                    className="btn-delete"
                    title="Sil"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TimeTracker;

import React, { useState, useEffect, useRef } from 'react';
import './PomodoroTimer.css';

const PomodoroTimer = ({ settings }) => {
  const [mode, setMode] = useState('work'); // work, shortBreak, longBreak
  const [timeLeft, setTimeLeft] = useState(settings.pomodoroWork * 60);
  const [isRunning, setIsRunning] = useState(false);
  const [sessionsCompleted, setSessionsCompleted] = useState(0);
  const intervalRef = useRef(null);
  const audioRef = useRef(null);

  useEffect(() => {
    // Initialize time based on mode
    switch (mode) {
      case 'work':
        setTimeLeft(settings.pomodoroWork * 60);
        break;
      case 'shortBreak':
        setTimeLeft(settings.pomodoroShortBreak * 60);
        break;
      case 'longBreak':
        setTimeLeft(settings.pomodoroLongBreak * 60);
        break;
      default:
        break;
    }
  }, [mode, settings]);

  useEffect(() => {
    if (isRunning && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handleTimerComplete();
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isRunning, timeLeft]);

  const handleTimerComplete = () => {
    setIsRunning(false);
    playSound();

    if (mode === 'work') {
      const newSessions = sessionsCompleted + 1;
      setSessionsCompleted(newSessions);

      if (newSessions % settings.pomodoroSessions === 0) {
        setMode('longBreak');
      } else {
        setMode('shortBreak');
      }
    } else {
      setMode('work');
    }

    // Show notification
    if (Notification.permission === 'granted') {
      new Notification('Pomodoro Tamamlandı!', {
        body: mode === 'work' ? 'Mola zamanı!' : 'Çalışma zamanı!',
        icon: '/icon-192.png'
      });
    }
  };

  const playSound = () => {
    if (audioRef.current) {
      audioRef.current.play();
    }
  };

  const toggleTimer = () => {
    setIsRunning(!isRunning);

    // Request notification permission
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
  };

  const resetTimer = () => {
    setIsRunning(false);
    switch (mode) {
      case 'work':
        setTimeLeft(settings.pomodoroWork * 60);
        break;
      case 'shortBreak':
        setTimeLeft(settings.pomodoroShortBreak * 60);
        break;
      case 'longBreak':
        setTimeLeft(settings.pomodoroLongBreak * 60);
        break;
      default:
        break;
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getModeLabel = () => {
    switch (mode) {
      case 'work':
        return 'Çalışma';
      case 'shortBreak':
        return 'Kısa Mola';
      case 'longBreak':
        return 'Uzun Mola';
      default:
        return '';
    }
  };

  const progress = () => {
    let total;
    switch (mode) {
      case 'work':
        total = settings.pomodoroWork * 60;
        break;
      case 'shortBreak':
        total = settings.pomodoroShortBreak * 60;
        break;
      case 'longBreak':
        total = settings.pomodoroLongBreak * 60;
        break;
      default:
        total = 1;
    }
    return ((total - timeLeft) / total) * 100;
  };

  return (
    <div className="pomodoro-container">
      <div className={`pomodoro-timer ${mode}`}>
        <div className="pomodoro-header">
          <h2>🍅 Pomodoro Timer</h2>
          <div className="mode-buttons">
            <button
              className={`mode-btn ${mode === 'work' ? 'active' : ''}`}
              onClick={() => !isRunning && setMode('work')}
              disabled={isRunning}
            >
              Çalışma
            </button>
            <button
              className={`mode-btn ${mode === 'shortBreak' ? 'active' : ''}`}
              onClick={() => !isRunning && setMode('shortBreak')}
              disabled={isRunning}
            >
              Kısa Mola
            </button>
            <button
              className={`mode-btn ${mode === 'longBreak' ? 'active' : ''}`}
              onClick={() => !isRunning && setMode('longBreak')}
              disabled={isRunning}
            >
              Uzun Mola
            </button>
          </div>
        </div>

        <div className="pomodoro-display">
          <div className="progress-ring">
            <svg width="300" height="300">
              <circle
                cx="150"
                cy="150"
                r="140"
                stroke="#e2e8f0"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="150"
                cy="150"
                r="140"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 140}`}
                strokeDashoffset={`${2 * Math.PI * 140 * (1 - progress() / 100)}`}
                strokeLinecap="round"
                transform="rotate(-90 150 150)"
                className="progress-circle"
              />
            </svg>
            <div className="timer-text">
              <div className="mode-label">{getModeLabel()}</div>
              <div className="time">{formatTime(timeLeft)}</div>
              <div className="sessions">Seans: {sessionsCompleted}/{settings.pomodoroSessions}</div>
            </div>
          </div>
        </div>

        <div className="pomodoro-controls">
          <button className="btn btn-primary btn-large" onClick={toggleTimer}>
            {isRunning ? '⏸ Duraklat' : '▶ Başlat'}
          </button>
          <button className="btn btn-secondary" onClick={resetTimer}>
            🔄 Sıfırla
          </button>
        </div>
      </div>

      <audio ref={audioRef} src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSuBzvLZiTYIGmm98OScTgwOUKni77RiHAU7k9n0ynosBS16yu/ajz8JE1y05fCnVBIIRp/e8r5uIwUrgs/y2Ik2Bxhpu/Dpn08MD1Co4u+0YhsDP5XZ88t5LAMVW7Ps6aZXFApFnt7xwHAgBSqBzvLZiTYIGWq88OWdTgsNUaff8LVkGwU7k9jzyngsBSl4yu/ajj8JEluz5vCoVRIIRZvd8sBvIwUsgs7y2Yo3Bxhquvbmn1AMDlGo4u+yYRsEPZPY88x4KwUpecrw2o8/CBJcsOXwp1UTCESc3fK/cCQFK4LO8tmJNggZarnw5Z9PDA1Rp+Lvs2IcBDqU2PPKeCsFL3nK8NqOPwgSXLDl8KdVEwlFm93ywG8jBCuBzvHaiTYHGGu68OadTgsNUKXh77NiGwQ9lNjzyngrbhxoKObafl1hqWW4kNOwqYCJi4d/cGxsbHByc3h9g4iMj5CLhH53b2xrcHh9goWIhoBzaWReYmdrb3NyaWJaUFJWXGBjY2FZTkhLUFVYV1VLQz1ARUlKSEI9Nys/GyM5/gRCQD06NSstKSQf"/>
    </div>
  );
};

export default PomodoroTimer;

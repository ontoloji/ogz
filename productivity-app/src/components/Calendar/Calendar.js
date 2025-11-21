import React, { useState } from 'react';
import './Calendar.css';
import { v4 as uuidv4 } from 'uuid';
import { formatDateTime, formatDate } from '../../utils/dateUtils';

const Calendar = ({ calendarEvents, setCalendarEvents }) => {
  const [newEventTitle, setNewEventTitle] = useState('');
  const [newEventDate, setNewEventDate] = useState('');
  const [newEventTime, setNewEventTime] = useState('');
  const [newEventDescription, setNewEventDescription] = useState('');

  const addEvent = () => {
    if (newEventTitle.trim() && newEventDate && newEventTime) {
      const dateTimeString = `${newEventDate}T${newEventTime}`;
      const event = {
        id: uuidv4(),
        title: newEventTitle,
        description: newEventDescription,
        dateTime: dateTimeString,
        createdAt: new Date().toISOString(),
        completed: false
      };
      setCalendarEvents([...calendarEvents, event].sort((a, b) =>
        new Date(a.dateTime) - new Date(b.dateTime)
      ));
      resetForm();
    }
  };

  const resetForm = () => {
    setNewEventTitle('');
    setNewEventDate('');
    setNewEventTime('');
    setNewEventDescription('');
  };

  const deleteEvent = (id) => {
    if (window.confirm('Bu etkinliği silmek istediğinizden emin misiniz?')) {
      setCalendarEvents(calendarEvents.filter((e) => e.id !== id));
    }
  };

  const toggleComplete = (id) => {
    setCalendarEvents(
      calendarEvents.map((event) =>
        event.id === id ? { ...event, completed: !event.completed } : event
      )
    );
  };

  const getUpcomingEvents = () => {
    const now = new Date();
    return calendarEvents.filter((event) => new Date(event.dateTime) >= now);
  };

  const getPastEvents = () => {
    const now = new Date();
    return calendarEvents.filter((event) => new Date(event.dateTime) < now);
  };

  const upcomingEvents = getUpcomingEvents();
  const pastEvents = getPastEvents();

  const isToday = (dateTime) => {
    const eventDate = new Date(dateTime);
    const today = new Date();
    return eventDate.toDateString() === today.toDateString();
  };

  const isTomorrow = (dateTime) => {
    const eventDate = new Date(dateTime);
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return eventDate.toDateString() === tomorrow.toDateString();
  };

  const getTimeUntil = (dateTime) => {
    const now = new Date();
    const eventDate = new Date(dateTime);
    const diff = eventDate - now;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} gün sonra`;
    if (hours > 0) return `${hours} saat sonra`;
    return 'Çok yakında';
  };

  return (
    <div className="calendar-container">
      <div className="calendar-header">
        <h2>📅 Takvim</h2>
        <span className="events-count">{calendarEvents.length} Etkinlik</span>
      </div>

      <div className="event-input-section">
        <input
          type="text"
          value={newEventTitle}
          onChange={(e) => setNewEventTitle(e.target.value)}
          placeholder="Etkinlik başlığı..."
          className="event-input"
        />
        <div className="event-datetime-row">
          <input
            type="date"
            value={newEventDate}
            onChange={(e) => setNewEventDate(e.target.value)}
            className="event-date-input"
          />
          <input
            type="time"
            value={newEventTime}
            onChange={(e) => setNewEventTime(e.target.value)}
            className="event-time-input"
          />
        </div>
        <textarea
          value={newEventDescription}
          onChange={(e) => setNewEventDescription(e.target.value)}
          placeholder="Açıklama (opsiyonel)..."
          className="event-description-input"
          rows="2"
        />
        <button onClick={addEvent} className="btn btn-primary">
          + Etkinlik Ekle
        </button>
      </div>

      <div className="events-sections">
        <div className="events-section">
          <h3>🔜 Yaklaşan Etkinlikler ({upcomingEvents.length})</h3>
          {upcomingEvents.length === 0 ? (
            <div className="empty-message">Yaklaşan etkinlik yok</div>
          ) : (
            <div className="events-list">
              {upcomingEvents.map((event) => (
                <div key={event.id} className={`event-item upcoming ${event.completed ? 'completed' : ''}`}>
                  <div className="event-checkbox">
                    <input
                      type="checkbox"
                      checked={event.completed}
                      onChange={() => toggleComplete(event.id)}
                      id={`event-${event.id}`}
                    />
                    <label htmlFor={`event-${event.id}`}></label>
                  </div>
                  <div className="event-content">
                    <h4 className="event-title">{event.title}</h4>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                    <div className="event-meta">
                      <span className="event-date">
                        {isToday(event.dateTime) && '🔴 Bugün • '}
                        {isTomorrow(event.dateTime) && '🟡 Yarın • '}
                        {formatDateTime(event.dateTime)}
                      </span>
                      <span className="event-countdown">{getTimeUntil(event.dateTime)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteEvent(event.id)}
                    className="btn-delete"
                    title="Sil"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {pastEvents.length > 0 && (
          <div className="events-section">
            <h3>📜 Geçmiş Etkinlikler ({pastEvents.length})</h3>
            <div className="events-list">
              {pastEvents.map((event) => (
                <div key={event.id} className={`event-item past ${event.completed ? 'completed' : ''}`}>
                  <div className="event-checkbox">
                    <input
                      type="checkbox"
                      checked={event.completed}
                      onChange={() => toggleComplete(event.id)}
                      id={`event-${event.id}`}
                    />
                    <label htmlFor={`event-${event.id}`}></label>
                  </div>
                  <div className="event-content">
                    <h4 className="event-title">{event.title}</h4>
                    {event.description && (
                      <p className="event-description">{event.description}</p>
                    )}
                    <div className="event-meta">
                      <span className="event-date">{formatDateTime(event.dateTime)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteEvent(event.id)}
                    className="btn-delete"
                    title="Sil"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Calendar;

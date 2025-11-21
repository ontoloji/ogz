import React, { useState } from 'react';
import './WebsiteBlocker.css';

const WebsiteBlocker = ({ blockedWebsites, setBlockedWebsites }) => {
  const [newWebsite, setNewWebsite] = useState('');

  const addWebsite = () => {
    if (newWebsite.trim()) {
      if (blockedWebsites.includes(newWebsite.toLowerCase())) {
        alert('Bu website zaten engellendi!');
        return;
      }
      setBlockedWebsites([...blockedWebsites, newWebsite.toLowerCase()]);
      setNewWebsite('');
    }
  };

  const removeWebsite = (website) => {
    setBlockedWebsites(blockedWebsites.filter((w) => w !== website));
  };

  const popularDistractions = [
    'facebook.com',
    'twitter.com',
    'instagram.com',
    'youtube.com',
    'reddit.com',
    'tiktok.com',
    'netflix.com'
  ];

  const addPopular = (website) => {
    if (!blockedWebsites.includes(website)) {
      setBlockedWebsites([...blockedWebsites, website]);
    }
  };

  return (
    <div className="blocker-container">
      <div className="blocker-header">
        <h2>🚫 Website Engelleyici</h2>
        <span className="blocked-count">{blockedWebsites.length} Engellendi</span>
      </div>

      <div className="blocker-info">
        <p>
          ⚠️ <strong>Not:</strong> Bu özellik sadece hatırlatma amaçlıdır.
          Gerçek website engelleme için sistem düzeyinde değişiklikler gereklidir.
        </p>
      </div>

      <div className="blocker-input-section">
        <input
          type="text"
          value={newWebsite}
          onChange={(e) => setNewWebsite(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addWebsite()}
          placeholder="example.com"
          className="blocker-input"
        />
        <button onClick={addWebsite} className="btn btn-danger">
          + Engelle
        </button>
      </div>

      <div className="popular-section">
        <h3>Popüler Dikkat Dağıtıcılar</h3>
        <div className="popular-list">
          {popularDistractions.map((website) => (
            <button
              key={website}
              onClick={() => addPopular(website)}
              className={`popular-btn ${blockedWebsites.includes(website) ? 'blocked' : ''}`}
              disabled={blockedWebsites.includes(website)}
            >
              {website}
              {blockedWebsites.includes(website) && ' ✓'}
            </button>
          ))}
        </div>
      </div>

      <div className="blocked-list">
        <h3>Engellenmiş Websiteler</h3>
        {blockedWebsites.length === 0 ? (
          <div className="empty-message">Henüz engellenmiş website yok</div>
        ) : (
          <div className="websites-list">
            {blockedWebsites.map((website) => (
              <div key={website} className="website-item">
                <span className="website-url">🚫 {website}</span>
                <button
                  onClick={() => removeWebsite(website)}
                  className="btn-remove"
                  title="Engeli Kaldır"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default WebsiteBlocker;

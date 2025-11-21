import React, { useState, useEffect } from 'react';
import './Motivation.css';
import { getRandomQuote } from '../../utils/motivationalQuotes';

const Motivation = () => {
  const [quote, setQuote] = useState('');

  useEffect(() => {
    setQuote(getRandomQuote());
  }, []);

  const getNewQuote = () => {
    setQuote(getRandomQuote());
  };

  return (
    <div className="motivation-container">
      <div className="motivation-card">
        <div className="quote-icon">💪</div>
        <blockquote className="quote-text">
          "{quote}"
        </blockquote>
        <button onClick={getNewQuote} className="btn btn-primary refresh-btn">
          🔄 Yeni Söz
        </button>
      </div>
    </div>
  );
};

export default Motivation;

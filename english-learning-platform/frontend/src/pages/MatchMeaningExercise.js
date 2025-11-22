import React, { useState, useEffect } from 'react';
import { getMatchMeaningExercise, submitExercise, markWordAsLearned } from '../services/api';

function MatchMeaningExercise() {
  const [exercise, setExercise] = useState(null);
  const [selectedWord, setSelectedWord] = useState(null);
  const [selectedMeaning, setSelectedMeaning] = useState(null);
  const [matches, setMatches] = useState([]);
  const [wrongAttempts, setWrongAttempts] = useState([]);
  const [completed, setCompleted] = useState(false);
  const [loading, setLoading] = useState(true);
  const userId = 1;

  useEffect(() => {
    loadExercise();
  }, []);

  const loadExercise = async () => {
    try {
      setLoading(true);
      const response = await getMatchMeaningExercise({ count: 6 });
      setExercise(response.data.data);
    } catch (error) {
      console.error('Error loading exercise:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWordClick = (word) => {
    if (matches.find(m => m.word.id === word.id)) return;
    setSelectedWord(word);

    if (selectedMeaning) {
      checkMatch(word, selectedMeaning);
    }
  };

  const handleMeaningClick = (meaning) => {
    if (matches.find(m => m.meaning.id === meaning.id)) return;
    setSelectedMeaning(meaning);

    if (selectedWord) {
      checkMatch(selectedWord, meaning);
    }
  };

  const checkMatch = async (word, meaning) => {
    const isMatch = word.id === meaning.id;

    if (isMatch) {
      setMatches([...matches, { word, meaning }]);
      setSelectedWord(null);
      setSelectedMeaning(null);

      try {
        await submitExercise({
          user_id: userId,
          exercise_type: 'match-meaning',
          exercise_id: word.id,
          user_answer: meaning.meaning,
          correct_answer: meaning.meaning,
          time_spent: 0
        });

        await markWordAsLearned(userId, word.id);
      } catch (error) {
        console.error('Error submitting match:', error);
      }

      if (matches.length + 1 === exercise.words.length) {
        setCompleted(true);
      }
    } else {
      setWrongAttempts([...wrongAttempts, { word: word.id, meaning: meaning.id }]);
      setTimeout(() => {
        setSelectedWord(null);
        setSelectedMeaning(null);
      }, 1000);
    }
  };

  const isMatched = (id, type) => {
    return matches.some(m =>
      type === 'word' ? m.word.id === id : m.meaning.id === id
    );
  };

  const isWrongAttempt = (wordId, meaningId) => {
    return wrongAttempts.some(w => w.word === wordId && w.meaning === meaningId);
  };

  if (loading) {
    return <div className="loading">Alıştırma yükleniyor...</div>;
  }

  if (!exercise) {
    return (
      <div className="container">
        <div className="card">
          <h2>Alıştırma Bulunamadı</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Kelime Eşleştirme</h1>

      <div className="card">
        <h3>Kelimeleri Türkçe anlamlarıyla eşleştirin</h3>
        <p style={{ color: '#718096', marginBottom: '24px' }}>
          Eşleşme: {matches.length} / {exercise.words.length}
        </p>

        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${(matches.length / exercise.words.length) * 100}%` }}
          />
        </div>

        {completed && (
          <div className="success" style={{ marginTop: '20px' }}>
            <h3>Tebrikler! Tüm kelimeleri doğru eşleştirdiniz! 🎉</h3>
            <button className="btn btn-primary" onClick={loadExercise}>
              Yeni Alıştırma
            </button>
          </div>
        )}

        {!completed && (
          <div className="grid grid-2" style={{ marginTop: '24px' }}>
            <div>
              <h4 style={{ marginBottom: '16px' }}>Kelimeler</h4>
              {exercise.words.map((word) => (
                <button
                  key={word.id}
                  className={`option-button ${
                    selectedWord?.id === word.id ? 'selected' : ''
                  } ${isMatched(word.id, 'word') ? 'correct' : ''}`}
                  onClick={() => handleWordClick(word)}
                  disabled={isMatched(word.id, 'word')}
                >
                  {word.word}
                </button>
              ))}
            </div>

            <div>
              <h4 style={{ marginBottom: '16px' }}>Anlamlar</h4>
              {exercise.meanings.map((meaning) => (
                <button
                  key={meaning.id}
                  className={`option-button ${
                    selectedMeaning?.id === meaning.id ? 'selected' : ''
                  } ${isMatched(meaning.id, 'meaning') ? 'correct' : ''} ${
                    selectedWord && isWrongAttempt(selectedWord.id, meaning.id) ? 'incorrect' : ''
                  }`}
                  onClick={() => handleMeaningClick(meaning)}
                  disabled={isMatched(meaning.id, 'meaning')}
                >
                  {meaning.meaning}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MatchMeaningExercise;

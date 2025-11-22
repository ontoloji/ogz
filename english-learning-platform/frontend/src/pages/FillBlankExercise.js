import React, { useState, useEffect } from 'react';
import { getFillBlankExercises, submitExercise } from '../services/api';

function FillBlankExercise() {
  const [exercises, setExercises] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showResult, setShowResult] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const userId = 1;

  useEffect(() => {
    loadExercises();
  }, []);

  const loadExercises = async () => {
    try {
      setLoading(true);
      const response = await getFillBlankExercises({ count: 10 });
      setExercises(response.data.data);
    } catch (error) {
      console.error('Error loading exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (answer) => {
    if (!showResult) {
      setSelectedAnswer(answer);
    }
  };

  const handleSubmit = async () => {
    if (!selectedAnswer) return;

    const currentExercise = exercises[currentIndex];
    const correct = selectedAnswer === currentExercise.correct_answer;

    setIsCorrect(correct);
    setShowResult(true);
    setScore({
      correct: score.correct + (correct ? 1 : 0),
      total: score.total + 1
    });

    try {
      await submitExercise({
        user_id: userId,
        exercise_type: 'fill-blank',
        exercise_id: currentExercise.id,
        user_answer: selectedAnswer,
        correct_answer: currentExercise.correct_answer,
        time_spent: 0
      });
    } catch (error) {
      console.error('Error submitting answer:', error);
    }
  };

  const handleNext = () => {
    if (currentIndex < exercises.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setShowResult(false);
    } else {
      alert(`Tamamlandı! Skorunuz: ${score.correct + (isCorrect ? 1 : 0)}/${exercises.length}`);
    }
  };

  if (loading) {
    return <div className="loading">Alıştırmalar yükleniyor...</div>;
  }

  if (exercises.length === 0) {
    return (
      <div className="container">
        <div className="card">
          <h2>Alıştırma Bulunamadı</h2>
          <p>Henüz alıştırma eklenmemiş.</p>
        </div>
      </div>
    );
  }

  const currentExercise = exercises[currentIndex];
  const displaySentence = currentExercise.sentence.replace('____', '_____');

  return (
    <div className="container">
      <h1>Boşluk Doldurma Alıştırması</h1>

      <div className="card">
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span>Soru {currentIndex + 1} / {exercises.length}</span>
            <span>Skor: {score.correct} / {score.total}</span>
          </div>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${((currentIndex + 1) / exercises.length) * 100}%` }}
            />
          </div>
        </div>

        <h3>{displaySentence}</h3>
        <p style={{ color: '#718096', marginBottom: '24px' }}>
          Seviye: {currentExercise.level || 'Beginner'}
        </p>

        <div>
          {currentExercise.options.map((option, index) => (
            <button
              key={index}
              className={`option-button ${
                selectedAnswer === option ? 'selected' : ''
              } ${
                showResult && option === currentExercise.correct_answer
                  ? 'correct'
                  : showResult && selectedAnswer === option
                  ? 'incorrect'
                  : ''
              }`}
              onClick={() => handleAnswerSelect(option)}
              disabled={showResult}
            >
              {option}
            </button>
          ))}
        </div>

        {showResult && (
          <div className={isCorrect ? 'success' : 'error'} style={{ marginTop: '20px' }}>
            {isCorrect ? (
              <p><strong>Doğru!</strong> Harika iş çıkardınız.</p>
            ) : (
              <p><strong>Yanlış.</strong> Doğru cevap: <strong>{currentExercise.correct_answer}</strong></p>
            )}
          </div>
        )}

        <div style={{ marginTop: '24px' }}>
          {!showResult ? (
            <button
              className="btn btn-primary"
              onClick={handleSubmit}
              disabled={!selectedAnswer}
            >
              Cevabı Gönder
            </button>
          ) : (
            <button className="btn btn-success" onClick={handleNext}>
              {currentIndex < exercises.length - 1 ? 'Sonraki Soru' : 'Bitir'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default FillBlankExercise;

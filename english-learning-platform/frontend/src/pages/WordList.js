import React, { useState, useEffect } from 'react';
import { getWords, getLevels, getCategories } from '../services/api';

function WordList() {
  const [words, setWords] = useState([]);
  const [levels, setLevels] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedLevel, setSelectedLevel] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadWords();
  }, [selectedLevel, selectedCategory]);

  const loadInitialData = async () => {
    try {
      const [levelsRes, categoriesRes] = await Promise.all([
        getLevels(),
        getCategories()
      ]);

      setLevels(levelsRes.data.data);
      setCategories(categoriesRes.data.data);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const loadWords = async () => {
    try {
      setLoading(true);
      const params = {};
      if (selectedLevel) params.level = selectedLevel;
      if (selectedCategory) params.category = selectedCategory;

      const response = await getWords(params);
      setWords(response.data.data);
    } catch (error) {
      console.error('Error loading words:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Kelime Listesi</h1>

      <div className="card">
        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
              Seviye:
            </label>
            <select
              value={selectedLevel}
              onChange={(e) => setSelectedLevel(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                fontSize: '14px'
              }}
            >
              <option value="">Tümü</option>
              {levels.map((level) => (
                <option key={level.id} value={level.name}>
                  {level.name} ({level.word_count})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
              Kategori:
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid #cbd5e0',
                fontSize: '14px'
              }}
            >
              <option value="">Tümü</option>
              {categories.map((category) => (
                <option key={category.id} value={category.name}>
                  {category.name} ({category.word_count})
                </option>
              ))}
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#718096' }}>
            Kelimeler yükleniyor...
          </div>
        ) : words.length > 0 ? (
          <div className="grid grid-2">
            {words.map((word) => (
              <div
                key={word.id}
                style={{
                  padding: '16px',
                  background: '#f7fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <h3 style={{ margin: 0, color: '#2d3748' }}>{word.word}</h3>
                  <span style={{
                    fontSize: '12px',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    background: '#667eea',
                    color: 'white'
                  }}>
                    {word.level_name || 'N/A'}
                  </span>
                </div>
                <p style={{ margin: '8px 0', color: '#4a5568', fontWeight: '600' }}>
                  {word.meaning_tr}
                </p>
                {word.meaning_en && (
                  <p style={{ margin: '4px 0', fontSize: '14px', color: '#718096', fontStyle: 'italic' }}>
                    {word.meaning_en}
                  </p>
                )}
                {word.example_sentence && (
                  <p style={{
                    marginTop: '12px',
                    padding: '8px',
                    background: 'white',
                    borderRadius: '4px',
                    fontSize: '14px',
                    color: '#4a5568'
                  }}>
                    💬 {word.example_sentence}
                  </p>
                )}
                {word.category_name && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#718096' }}>
                    📚 {word.category_name}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '40px', color: '#718096' }}>
            Kelime bulunamadı
          </div>
        )}
      </div>
    </div>
  );
}

export default WordList;

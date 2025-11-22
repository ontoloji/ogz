import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import FillBlankExercise from './pages/FillBlankExercise';
import MatchMeaningExercise from './pages/MatchMeaningExercise';
import Progress from './pages/Progress';
import WordList from './pages/WordList';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <div className="container">
            <div className="logo">English Learning</div>
            <ul>
              <li><Link to="/">Ana Sayfa</Link></li>
              <li><Link to="/fill-blank">Boşluk Doldur</Link></li>
              <li><Link to="/match-meaning">Kelime Eşleştir</Link></li>
              <li><Link to="/words">Kelimeler</Link></li>
              <li><Link to="/progress">İlerleme</Link></li>
            </ul>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/fill-blank" element={<FillBlankExercise />} />
          <Route path="/match-meaning" element={<MatchMeaningExercise />} />
          <Route path="/words" element={<WordList />} />
          <Route path="/progress" element={<Progress />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

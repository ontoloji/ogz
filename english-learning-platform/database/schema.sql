-- English Learning Platform Database Schema

-- Kategoriler tablosu
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seviyeler için enum benzeri tablo
CREATE TABLE IF NOT EXISTS levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    order_num INTEGER NOT NULL
);

-- Kelimeler tablosu
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL,
    meaning_tr VARCHAR(200) NOT NULL,
    meaning_en TEXT,
    example_sentence TEXT,
    pronunciation VARCHAR(100),
    level_id INTEGER,
    category_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (level_id) REFERENCES levels(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Kullanıcılar tablosu
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(150) UNIQUE,
    password_hash VARCHAR(255),
    current_level_id INTEGER DEFAULT 1,
    daily_goal INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    FOREIGN KEY (current_level_id) REFERENCES levels(id)
);

-- Günlük hedefler ve ilerleme
CREATE TABLE IF NOT EXISTS daily_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    words_learned INTEGER DEFAULT 0,
    exercises_completed INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_answers INTEGER DEFAULT 0,
    goal_achieved BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, date)
);

-- Kullanıcının öğrendiği kelimeler
CREATE TABLE IF NOT EXISTS user_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word_id INTEGER NOT NULL,
    learned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mastery_level INTEGER DEFAULT 1,
    review_count INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (word_id) REFERENCES words(id),
    UNIQUE(user_id, word_id)
);

-- Boşluk doldurma alıştırmaları
CREATE TABLE IF NOT EXISTS fill_blank_exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentence TEXT NOT NULL,
    correct_answer VARCHAR(100) NOT NULL,
    blank_position INTEGER NOT NULL,
    level_id INTEGER,
    category_id INTEGER,
    word_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (level_id) REFERENCES levels(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (word_id) REFERENCES words(id)
);

-- Boşluk doldurma seçenekleri
CREATE TABLE IF NOT EXISTS fill_blank_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    option_text VARCHAR(100) NOT NULL,
    is_correct BOOLEAN DEFAULT 0,
    FOREIGN KEY (exercise_id) REFERENCES fill_blank_exercises(id)
);

-- Kullanıcı alıştırma geçmişi
CREATE TABLE IF NOT EXISTS exercise_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_type VARCHAR(50) NOT NULL,
    exercise_id INTEGER NOT NULL,
    user_answer TEXT,
    is_correct BOOLEAN,
    time_spent INTEGER,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- İstatistikler için view
CREATE VIEW IF NOT EXISTS user_statistics AS
SELECT
    u.id as user_id,
    u.username,
    COUNT(DISTINCT uw.word_id) as total_words_learned,
    COUNT(DISTINCT ea.id) as total_exercises,
    SUM(CASE WHEN ea.is_correct = 1 THEN 1 ELSE 0 END) as correct_answers,
    COUNT(ea.id) as total_attempts,
    ROUND(CAST(SUM(CASE WHEN ea.is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) /
          NULLIF(COUNT(ea.id), 0) * 100, 2) as accuracy_percentage
FROM users u
LEFT JOIN user_words uw ON u.id = uw.user_id
LEFT JOIN exercise_attempts ea ON u.id = ea.user_id
GROUP BY u.id, u.username;

-- İlk veri eklemeleri
INSERT INTO levels (name, order_num) VALUES
    ('Beginner', 1),
    ('Intermediate', 2),
    ('Advanced', 3);

INSERT INTO categories (name, description) VALUES
    ('Günlük Konuşma', 'Günlük hayatta kullanılan kelimeler ve ifadeler'),
    ('İş İngilizcesi', 'İş hayatında kullanılan profesyonel kelimeler'),
    ('Akademik', 'Akademik ve resmi İngilizce'),
    ('Seyahat', 'Seyahat sırasında kullanılan ifadeler'),
    ('Teknoloji', 'Teknoloji ve bilgisayar terimleri');

-- Demo kullanıcı (şifre: demo123)
INSERT INTO users (username, email, password_hash, daily_goal) VALUES
    ('demo', 'demo@example.com', '$2a$10$hash', 15);
